from pymongo import MongoClient
import pandas as pd
import pprint as pprint
import collections
from itertools import izip
import math
import numpy as np

class LoadTransform(object):

	"""
	Creates an object to easily load and tranform the data into a pandas dataframe.

	Example usage:

	from load_transform import LoadTransform
	lt = LoadTransform()
	lt.load_data({"address.state": "WA"})
	lt.transform_data()

	"""


	def __init__(self):
		self.client = MongoClient()
		self.db = self.client.updated_proj
		self.cursor = None
		self.df = None
		self.example_query = 'self.load_data({"address.state": "WA"})'

	def load_data(self, mongo_query):
		
		self.cursor = self.db.listings.find(mongo_query)


	def transform_data(self):
		# taken from Stackoverflow discussion at:
		# http://stackoverflow.com/questions/6027558/flatten-nested-python-dictionaries-compressing-keys
		def flatten(d, parent_key='', sep='_'):
		    items = []
		    for k, v in d.items():
		        new_key = parent_key + sep + k if parent_key else k
		        if isinstance(v, collections.MutableMapping):
		            items.extend(flatten(v, new_key, sep=sep).items())
		        else:
		            items.append((new_key, v))
		    return dict(items)

		def rename_columns(df):
		    df.columns = [col.replace("editedfacts_", '') for col in df.columns]
		    df.columns = [col.replace("address_", '') for col in df.columns]
		    df.columns = [col.replace("posting_", '') for col in df.columns]
		    return df

		flattened = [flatten(document) for document in self.cursor]
		self.df = pd.DataFrame(flattened, index=range(len(flattened)))
		self.df = rename_columns(self.df)
		self.df = self.df.drop_duplicates('zpid') # drop any duplicates	
	

