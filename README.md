# Personalized Real Estate Recommender


## Introduction

This is the real estate recommendation system that I built for my final project during the Galvanize Data Science Intensive.

The genesis of this project was to assist me in finding a home. I moved to Seattle in early July and knew nothing of the local area, let alone where I should consider moving my family after I finished school. Sites like Zillow and Trulia are useful for getting access to enormous amounts of information but they create a new problem of having to sift through thousands of choices to find the right place. I find this a tedious process.  

I have always been impressed by how well sites like Amazon and Netflix make recommendations for books and content that I may like. It saves the trouble of sifting through countless options and I am usually pleased with the results of their recommendations!  

I wondered why there couldn't be something similar for finding a place to live? I also assumed that I am not the only one who has the same problem, so I attempted to generalize my solution such that it could benefit a larger group of people in finding a home.  

In short, this recommender is my first cut at solving the problem of helping a person who is moving from one city to another, find the RIGHT place to live.

## The Code
Here is a diagram of my repo and a brief 10,000 ft overview of what each of the files does:

**code**

1. `image_getter.py` - class for easily getting an image url for a Zillow listing
2. `learn_preferences.py` - the guts of the recommender system 
3. `load_transform.py` - class for loading data from MongoDB and transforming it for processing
4. `pre_processing.py` - class to transform, normalize, and prep data for the recommender
5. **pipeline**
  1. `get_schools.py` - a class to scrape school data for a given listing and transform it to a Pandas df
  2. `walkscore_api.py` - a class to query WalkScore for walkability and public transit data, and update MongoDB
  3. `web_scraping.py` - a class that streamlines scraping Zillow search results to obtain addresses of listings
  4. `zillow_api.ipynb` - an iPython notebook that I use for querying the Zillow API, need to convert to a script 

**data**

1. san_fran.csv - a csv of zillow listings that I scraped
2. seattle_schools.txt - a list of all Seattle area schools and their scores from 1-10
3. **seattle**
  1. seattle.csv - a csv of aggregated zillow listings that I queried through the API
  2. bellevue-WA.csv - a csv of address and home ids that I scraped from Zillow search results
  3. wallingford-seattle-WA.csv - a csv of address and home ids that I scraped
  4. etc.
 
### Overview

This recommender system is -- at the core -- a content based information retrieval system. Recommendations are made based on the notion of computing a measure of similarity between different listings. A content based recommender is different from a collaborative based recommender because the latter relies on the ratings of other users to make recommendations to a new user. 

### Problem 1 - The Cold Start Problem
Since I have no historical data on any users -- a problem known as the "Cold Start Problem" -- I decided to tackle the problem by using a known house that I liked from a previous city as a "seed" for the recommender.  From this initial seed, recommendations are served using different measures of similarity -- or distance metrics. 

### Problem 2 - How do different people value houses?
The use of different distance metrics is important because the most similar houses to the seed will vary wildly based on how distance is computed. This idea captures the notion that different people value attributes of houses in different ways. For example, a single young professional will be more interested in walkability and nightlife, and less interested in schools and the size of their yard than would a married couple with children.   

### Problem 3 - How does a given user value a house?
This leads into the problem of how to choose which distance metric is best for a particular user so that the system can keep serving them relevant recommendations. To solve this problem, I framed the problem like an AB test. Instead of testing multiple versions of a webpage, I am testing multiple ways to suggest housing recommendations. Additionally, I also show the same user multiple versions of "similar houses" using different distance metrics in the assumption that their feedback will provide enough data to learn which version of providing recommendations is best for them.

In order to make sure that relevant recommendations are served while also determining which method of making recommendations is best, I decided to implement a greedy algorithm -- specifically the Bayesian Multi-Armed Bandit (MAB). 

## How the recommender works 
![alt text](https://github.com/MichaelAHood/real_estate_recommender/blob/master/data/algorithm.png)

Recommendations are shown two at a time and the user is able to pick the one they like best. The user's choice is recorded and then used to update a probabilistic "guess" of what measure of similarity is providing the best recommendations for that user. I am intent on the idea of only showing listings two at a time for one particular reason -- humans are notoriously bad at making value judgements from multiple choices when the number of choices exceeds four to five. We are, however, exceptionally good at making pairwise value comparisons. In general, people can quickly take a look at two things and tell you which is better or more preferable. The downside to this approach is that the user may have to choose listings over a large number of iterations of the algorithm before a high degree of confidence is obtained for the best distance metric.

## Obtaining the Data
1. Zillow
  1. Scraping
  2. API
2. WalkScore
  1. API
3. Noddle
  1. Scraping



