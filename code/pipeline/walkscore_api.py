import requests
import pandas as pd
import pprint as pprint
import json
from itertools import izip
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

class WalkScore(object):
    """
    How to use this class:

    from walkscore_api import WalkScore
    ws = WalkScore()
    ws.query_api()          # queries all the listings in self.df
    ws.get_api_report()     # check how many api calls were successful or not
    ws.get_and_format_data() # put all the queried data into a pandas df
    ws.update_mongo()       # insert all the data into MongoDB

    """
    

    def __init__(self):
        print "Test XXX!"
        self.df = None
        self.walk_scores = []
        self.transit_scores = []
        self.df_api = None
        self.response_status = {}
        self.incompletes = []
        self.df_final = None

    def query_api(self, df):
        self.df = df
        WSAPI_KEY = os.getenv('WALKABLE_API_KEY')
        TRANSIT_BASE_URL = "http://transit.walkscore.com/transit/score/?lat={0}&lon={1}&city={2}&state={3}&wsapikey={4}&research=yes"
        WALK_BASE_URL = "http://api.walkscore.com/score?format={0}&address={1}%20{2}%20{3}%20{4}&lat={5}&lon={6}&wsapikey={7}"
        self.df['city'] = self.df['city'].apply(lambda city: city.replace(' ', '-'))
        self.df['city'] = self.df['city'].apply(lambda city: "Seattle" if city=="Des-Moines" else city) 
        self.df['street'] = self.df['street'].apply(lambda street: street[:street.find('#')-1] if '#' in street else street)
        self.df['street'] = self.df['street'].apply(lambda street: street.replace(' ', '-'))
        count = 1
        for row in self.df.iterrows():
            city = row[1][1]
            lat = row[1][2]
            lon = row[1][3]
            state = row[1][4]
            address = row[1][5]
            zip_code = row[1][6]
            walk_api_query = WALK_BASE_URL.format('json', address, zip_code, city, state, lat, lon, WSAPI_KEY) 
            walk_api_response = requests.get(walk_api_query)
            self.walk_scores.append(walk_api_response.content)
            transit_api_query = TRANSIT_BASE_URL.format(lat, lon, city, state, WSAPI_KEY)
            transit_api_response = requests.get(transit_api_query)
            self.transit_scores.append(transit_api_response.content)
            print "Querying row: {0}".format(count)
            count += 1
       
    def score_api_responses(self):
        walk_succeed_string = '"status": 1' 
        transit_fail_string = "You must provide a valid 'city' and 'state'"
        for index, score in enumerate(izip(self.walk_scores, self.transit_scores)):
            status = {'walkscore_status': 1,
                      'transitscore_status': 1} # 1 --> status is good
            if walk_succeed_string not in score[0]:
                status['transitscore_status'] = 0 # status if bad
            if transit_fail_string in score[1]:
                status['transitscore_status'] = 0
            self.response_status[index] = status
        

    def get_api_report(self):
        self.score_api_responses()
        success_count = 0
        incomplete_count = 0
        for key, value in self.response_status.items():
            if (value['transitscore_status'] == 0) or (value['walkscore_status'] == 0):
                incomplete_count += 1
                self.incompletes.append({key: value})
            else:
                success_count += 1
        print "{0} API calls were successful".format(success_count)
        print "{0} API calls were incomplete or unsuccessful".format(incomplete_count)
         

    def get_and_format_data(self):
        
        def to_json(query_response):
            return json.loads(query_response.replace('\n', ''))
        
        key_ids = []
        walkscore_descriptions = []
        walkscore_scores = []
        trans_descriptions = []
        trans_summaries = []
        trans_scores = []
        for i in range(min([len(self.walk_scores), len(self.transit_scores)])): # take the smaller of the two lists
            key_id = self.df.ix[i][0]
            key_ids.append(key_id)
            try:
                walkscore_desc = to_json(self.walk_scores[i])['description']
            except:
                walkscore_desc = 'None'
            walkscore_descriptions.append(walkscore_desc)
            try:
                walkscore_score = to_json(self.walk_scores[i])['walkscore']
            except:
                walkscore_score = 'None'
            walkscore_scores.append(walkscore_score)
            try:
                trans_desc = to_json(self.transit_scores[i])['description']
            except:
                trans_desc = 'None'
            trans_descriptions.append(trans_desc)
            try:
                trans_summ = to_json(self.transit_scores[i])['summary']
            except:
                trans_summ = 'None'
            trans_summaries.append(trans_summ)
            try:
                trans_score = to_json(self.transit_scores[i])['transit_score']
            except:
                trans_score = "None"
            trans_scores.append(trans_score)
        
        self.df_api = pd.DataFrame({'_id': key_ids, 
                             'walkscore_desc': walkscore_descriptions, 
                             'walkscore_score': walkscore_scores,
                             'trans_desc': trans_desc,
                             'trans_summary': trans_summaries,
                             'trans_score': trans_scores}, index=range(len(key_ids))) 
    def update_mongo(self):
        print "Test!"
        client = MongoClient()
        db = client.updated_proj
        #self.df_final = pd.concat([self.df, self.df_api], axis=1, join='outer')
        for row in self.df_final.iterrows():
            mongo_id = ObjectId(row[1][0])
            trans_desc = row[1][57]
            trans_score = row[1][58]
            trans_summary = row[1][59]
            walkscore_desc = row[1][60]
            walkscore_score = row[1][61]
            
            #print mongo_id, trans_desc, trans_score, trans_summary, walkscore_desc, walkscore_score

            print "updating...    ", mongo_id
            db.listings.update(
                                {'_id': mongo_id},
                                { '$set': { "trans_desc": trans_desc,
                                            "trans_score": trans_score,
                                            "trans_summary": trans_summary,
                                            "walkscore_desc": walkscore_desc,
                                            "walkscore_score": walkscore_score
                                }}
                                )


