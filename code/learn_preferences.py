import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import pairwise_distances
from scipy.spatial.distance import cosine
from scipy.stats import beta
from pre_processing import PreProcess
from image_getter import GetImage
import re
import sys
import os
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(color_codes=True)



class LearnPreferences(object):
    
    """
    Implements a multi-armed bayeseian bandit to learn a users preferences in houses.
    """

    def __init__(self, df1, df2, df1_raw, df2_raw, ref_listing, num_matches=1):
        """
        Input: two pre-processed dataframe obejcts, list of metrics (e.g. 'walk_distance', 'space_distance'),
        the integer index of the reference listing, the number of matches to return per metric,
        e.g. num_mathces=1 means that the recommender will return two listings at a time
        """
        self.ref_listing = ref_listing # the seed house that all other house are comapred to
        self.df1_raw = df1_raw.reset_index()
        self.df2_raw = df2_raw.reset_index()
        self.orginal_df1 = df1.reset_index()
        self.orginal_df2 = df2.reset_index()
        self.df1 = df1.reset_index().ix[self.ref_listing]
        self.df2 = df2.reset_index()
        self.num_matches = num_matches # the number of mathces to return
        self.recommendations = None
        self.recommendation_history = {}
        self.pairs_served = 0
        self.metrics = ['walk_distance', 'space_distance', 'family_distance']
        self.scores = {}
        self.params = {}
        self.init_scores_and_params() # populates self.scores with a zero for each of the different distance metrics
        self.listings_served = set()
        self.current_pairs = None
        self.sim_mat = self.update_similarity_matrix('cosine')
        
    
    def init_scores_and_params(self): 
        for metric in self.metrics:
            if metric not in self.scores:
                self.scores[metric] = 0
            if metric not in self.params:
                self.params[metric] = (0, 0)


    def update_similarity_matrix(self, distance_metric):

        self.sim_mat = pairwise_distances(self.df1, self.df2, metric=distance_metric, n_jobs=-1) 
        return self.sim_mat

    
    def update_recommendations(self):
        """
        Note:
        """
        if self.pairs_served < 1:
            self.recommendations = {}
            for metric in self.metrics:
                self.df1 = PreProcess(self.df1).filter_df(metric)
                self.df2 = PreProcess(self.df2).filter_df(metric) 
                self.update_similarity_matrix('euclidean')
                # reset the df to their orignal version for the next iteration
                self.df1 = self.orginal_df1
                self.df2 = self.orginal_df2
                self.recommendations[metric] = np.argsort(self.sim_mat[0])[-(self.num_matches):].tolist()
        return self.recommendations

    def get_recommendation(self, metric):
        
        """
        Input: similarity matrix with first arg of parwise distances as rows and
               second arg of pairwise distances as columns, the integer index of the 
               listing you want to compare other listings to, int for the num of listings
               to return.
               
        Output: an numpy array with the indices of the listings that
                are most similar to the ref_listing.
        """
        # draw an element at random from the recommendations list
        recommendation = np.random.choice(self.recommendations[metric])
        # remove the element from recommendations
        index = self.recommendations[metric].index(recommendation)
        self.recommendations[metric].pop(index)
        return recommendation
   

    def choose_models(self):
        # choose two of the available models, where one is the best estimate of the users preference
        # and the other is randomly chosen of the remaining metrics

        # assign the best guess to a list
        if self.pairs_served > 0:
            best_guess = self.recommendation_history[self.pairs_served]['estimated_user_preference']
            metrics = [best_guess]
            remaining_metrics = list(self.metrics) # make a copy of the list, so the original is not modified
            remaining_metrics.pop(remaining_metrics.index(best_guess)) # remove the best guess, since it's already in metrics
            metrics.append(np.random.choice(remaining_metrics)) # randomly choose the other metric
            np.random.shuffle(metrics) # shuffle the metrics, so the best guess recommendation is not always the first one presented
        else:
            # this is the starting point and these is no best guess of the best metric
            metrics = np.random.choice(self.metrics, 2, replace=False)
        return metrics 

    
    def show_recommendations(self):
        sample_metrics = self.choose_models()
        recommendations = []
        for metric in sample_metrics:
            # get a recommednation from each of the metrics in this iteration
            recommendations.append(self.get_recommendation(metric))
        self.current_pairs = recommendations
        left = self.current_pairs[0]
        right = self.current_pairs[1]
        return self.df2_raw[['city', 'state', 'street', 'finishedsqft', 
                'bedrooms', 'bathrooms', 'trans_score', 
                'walkscore_score', 'price']].ix[[left, right]].T



    def get_user_choice(self, user_choice):
        
        """
        Input: a dataframe for each of the cities
        Output: the recommendation corresponding to the user choice 
        """
        
        sample_metrics = self.choose_models()
        
        if user_choice == "l":
            self.scores[sample_metrics[0]] += 1
            winner = self.current_pairs[0]
        else:
            self.scores[sample_metrics[1]] += 1
            winner = self.current_pairs[1]

        #self.user_choices.append(user_choice)
        self.pairs_served += 1
        self.update_recommendation_history(self.current_pairs, winner)
 

    def update_recommendation_history(self, recommendations, winner):
        self.recommendation_history[self.pairs_served] = {'pairs_served': recommendations,
                                                          'winner': winner}
  
    def guess_preferences(self):
        """
        Input: no inputs
        Output: no outputs
        Notes: this function will take the updated score for each metric, compute a 
        beta distribution defined by the win/loss scores, sample from each distribution
        and return the metric that corresponds to the greatest probability. The winning
        metric is added to recommendation_history as the best guess of user preference.
        """
        user_preference = None
        max_prob = 0
        for metric in self.metrics:
            self.params[metric] = (self.scores[metric] + 1, self.pairs_served - self.scores[metric] + 1)
            prob = beta.rvs(self.params[metric][0] + 1, self.params[metric][1] + 1) # sample form the dist for each metric
            if prob > max_prob:
                max_prob = prob
                user_preference = metric
        self.recommendation_history[self.pairs_served]['estimated_user_preference'] = user_preference
        
    def generate_images(self):
        fig = plt.figure()
        for metric in self.metrics:
            x = beta(self.params[metric][0] + 1, self.params[metric][1] + 1).rvs(size=1000)
            sns.kdeplot(x, shade=True, label=metric)
            fig.suptitle("Liklihood that you belong to a segment", fontsize=20)
            plt.legend(fontsize=16, loc='upper left')
            plt.ylabel('Likelihood', fontsize=16)
            plt.xlabel('Choice Preference', fontsize=16)
        plt.savefig("prob_dist.png", dpi=600)

        
    def fetch_content(self, listing_index): 
        image_getter = GetImage()
        image = image_getter.get_image(self.df2_raw.ix[listing_index])
        address = self.df2_raw.ix[listing_index][5]   
        bedroom =  self.df2_raw.ix[listing_index][11]
        bathroom = self.df2_raw.ix[listing_index][12]
        sqft = self.df2_raw.ix[listing_index][16]
        walkscore = self.df2_raw.ix[listing_index][12]
        transcore = self.df2_raw.ix[listing_index][12]
        school = self.df2_raw.ix[listing_index][12]
        print address, bedroom, bathroom, sqft, walkscore, transcore, school




#if __name__ == "__maine__":    

#   df = pd.read_csv('trx_seattle.csv', index_col=0) # this df contains the untransformed listing data
#   my_past_house = df1.ix[0] # user has previously lived in house with index 0
#   user_session = LearnPreferences(df1, df2) # init object and a similarity matrix
#   recommendations = user_session.get_most_similar(user_session.sim_mat, my_past_house, 4) # provides the 4 most similar listings
#   choice = get_user_choice(reccomendations)
#   update_user_history(recommendations)