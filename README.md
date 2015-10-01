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

1. `san_fran.csv` - a csv of zillow listings that I scraped
2. `seattle_schools.txt` - a list of all Seattle area schools and their scores from 1-10
3. **seattle**
  1. `seattle.csv` - a csv of aggregated zillow listings that I queried through the API
  2. `bellevue-WA.csv` - a csv of address and home ids that I scraped from Zillow search results
  3. `wallingford-seattle-WA.csv` - a csv of address and home ids that I scraped
  4. etc, other csv files for each of the major neighborhoods and surrounding towns
 
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
Starting this project I naively assumed that I could easily come across detailed information about large numbers of houses in a given city. This assumption turned out to not be true. Sights like Zillow and Trulia provide fairly detailed information about listings, but the number of listings that they share is extremely limited -- approximately 70% of all Zillow istings are proteced and available to query through the API.

Below is a description about how I aquired the data for my recommender.

1. **Zillow**
  1. **Scraping** - Zillow has an easy to use API, but the precondition for using the API is that you already have to know the Zillow ID (ZPID) of the house you want to query. Since I wanted all of the houses in Seattle and San Francisco, I needed to find a way to automatically construct a list of address and ZPIDs. 

Thankfully, the search results for a Zillow query contain a list of houses with urls. I found that I could parse the html source for a Zillow query to find the links and retreive the addresses and ZPIDs from the url itself. I simply had to construct a url in the form that would return a zillow search results page for a given city, parse the html and repeat, until I had enough listing addresses and ZPIDs.

To facilitte this process, I wrote the web_scraping.py class. Creating a WebScraping() object and using the associated methods -- including a proxy method that allows the use of tor -- makes this process go relatively smoothly. There is also a paramter to set sleep times between GET requests to avoid making too many requests in a short time and gettin blocked. Despite that, Zillow will eventually catch on and start serving captchas, so I would have to inititalize a new tor circuit and create a new session to resume where I left off, when I was blocked.

After scraping both the Seattle and San Francisco Bay areas, I ended up with about 2,000 listings per region, which I wrote to a .csv file.
  
  2. **API** - With the ZPIDs and associated addresses, I was able to construct a series of functions to query the Zillow API. I prototyped this code in an iPython notebook -- and have not yet got around to writing a proper script or class. There are also several other fucntions to parse the API results, structure it, and insert it into a MongoDB collection.

The Zillow API has a daily query limit of 1,000 queries, so I was only able to query about half of the listings for a city each day. This is also when I discovered that about 65-70% of the addresses are not available through the API, so after two days of running API queries, I only ended up with about 700 results of the 2,000 I asked for.

2. WalkScore
  1. API
3. Noddle
  1. Scraping



