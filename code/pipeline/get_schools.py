import pandas as pd
import json
import requests
import requesocks
import time
from bs4 import BeautifulSoup as BS
import re
import os

class GetSchools(object):
    """
    How to use this class to get school info into a pandas dataframe:

    df = pd.read_csv('seattle.csv', index_col=0)
    gs = GetSchools()
    gs.load_school('seattle_schools.txt')
    gs.get_html(df, 0, len(df))
    gs.compute_school_scores()
    gs.to_dataframe()
    gs.impute_missing_values()
    gs.df.to_csv('seattle.csv')

    """


    def __init__(self):
        self.schools = None
        self.df = None
        self.school_scores = []
        self.df_scores = None

    def load_school(self, filename):
        with open(filename, 'r') as f:
            d = f.read()
            self.schools = json.loads(d)

    def get_html(self, df, start, stop):
        self.df = df
        params = {'user-agent': 'Mozilla/5.0'}
        session = requesocks.session()
        #Use Tor for both HTTP and HTTPS
        #session.proxies = {'http': 'socks5://127.0.0.1:9150',
        #                   'https': 'socks5://127.0.0.1:9150'}
        
        os.chdir('../data')
        for row in df.ix[start:stop].iterrows(): # iterate through each address in the df and get the html for it
            query = (row[1][5]+' '+row[1][1]+' '+row[1][4]+' '+str(row[1][6])).replace(' ', '%20')
            # this URL is formatted to query www.noodle.com/schools
            URL = "https://www.noodle.com/search/schools?distance=10&location={0}".format(query)
            query_url = URL + query + "&sort=best_fit"
            try:
                r = requests.get(query_url, headers=params)
            except:
                print "Row {0} HTTP get failed.".format(row[0])
            with open("school_index_{0}.txt".format(row[0]), 'w') as f: # write each html to a txt file so I can parse it later
                f.write(r.content)
                
            print "writing {0}".format(row[0])
        
    
    def compute_school_average(self, html_source):
        school_count = 0
        address_score = 0
        for school in self.schools.keys(): # school_dict is the school info from the string_to_dict function
            m = re.search(school, html_source)
            if m:
                school_count += 1
                address_score += int(self.schools[school])
        if school_count == 0:
            return 0
        return float(address_score) / school_count # returns an average of all the schools within ten miles


    def aggregate_scores(self):
        
        for row in self.df.iterrows():
            with open("school_index_{0}.txt".format(row[0]), 'r') as f:
                doc = f.read()
            
            score = self.compute_school_average(doc)
            self.school_scores.append(score)
        

    def compute_school_scores(self):
        self.aggregate_scores()

    def to_dataframe(self):
        self.df_scores = pd.DataFrame({'school_index': self.school_scores}, 
                                        index=range(len(self.school_scores)))
        self.df_scores['city'] = self.df['city']
        self.df['school_index'] = self.df_scores['school_index']

    def impute_missing_values(self):
        self.df['city'] = self.df['city'].apply(lambda x: x[0] + x[1:].lower())
        for city in self.df['city'].unique():
            
            mean_score = self.df_scores['school_index'][(self.df_scores['city'] == city) & (self.df_scores['school_index'] > 0)].mean()
            print city, mean_score
            self.df['school_index'][(self.df['city'] == city) & (self.df['school_index'] == 0)] = mean_score
            self.df['school_index'][self.df['city'] == 'Mercer island'] = 10
            self.df['school_index'][self.df['city'] == 'Des moines'] = 4


