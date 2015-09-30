# Personalized Real Estate Recommender


## Introduction

This is the real estate recommendation system that I built for my final project during the Galvanize Data Science Intesive.

The genesis of this project was to assist me in finding a home. I moved to Seattle in early July and knew nothing of the local area, let alone where I should consider moving my family after I finished school. Sites like Zillow and Trulia are useful for getting access to enormous amounts of information but they create a new problem of having to sift through thousands of choices to find the right place. I find this a tedious process.  

I have always been impressed by how well sites like Amazon and Netflix make recommendations for books and content that I may like -- I am usually pleased with the results of their recommendations!  

I wondered why there couldn't be something similar for finding a place to live? I also assumed that I am not the only one who has the same problem, so I attempted to generalize my solution such that it could benefit a larger group of people in finding the right home.  

In short, this recommender is intended to help a person who is moving from one city to another, find a place to live. 

The recommender system is -- at the core -- a content based information retrieval system. Recommendations are made based on the notion of computing a measure of similarity between different listings. A content based recommedner is different from a collaborative based recommeder because the later relies on the ratings of other users to make recommednations to a new user. 

I have no historical data on any users

The results are recorded and used to learn the users preference for certain types of homes. 

The recommendations are served based on a pair-wise similarity matrix that is computed using multiple custom distance metrics. Each distance metric corresponds to a preference for a certain type of house, e.g. spaciousness, walkability, etc. 

To determine the actual preference for a user, an implementation of the Bayesian Multi-Armed Bandit (MAB) apporach to AB testing is used. As data is collected about a users preferences, the results are used to update the algorithms best guess about what type of user you are (i.e. what are your preferences for a home). The algorithm is biased to serve recommendations in accordance with the best guess, as will also serve recommendations from other similarity metrics -- chosen at random.

This repo is a work in progress and is continually updated as I make progress on my project.

# Documentation

## 1. Data Pipeline
  1. **web_scraping.ipynb** (Prototype code to scrape address and listing id from zillow, can be used with a proxy.  Need to convert this to a script).
  2. **zillow_api.ipynb** (Ipython notebook to query Zillow API, convert the output into a JSON like format for insertion into MongoDB.  Also writes a csv of listings that could not be accessed via Zillow API - which is over half.)
  3. **walkable_api.ipynb** (Ipython notebook to query walkable API for addresses, updates MongoDB with the walkscore info for each listing.)
##2. Cleaning and Processing
  a. Dealing with missing values
  b. 
## 3. Implementing the Recommender

