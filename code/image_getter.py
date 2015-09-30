import requests

class GetImage(object):
    """
    This class is to assist in quickly fetching image urls for a 
    Zillow listing.

    """
    def __init__(self):
        self.df = None

    def build_link(self, row):
        """
        Input: a row of a dataframe
        Output: a url to the Zillow listing
        """
        BASE_URL = "http://www.zillow.com/homedetails/{0} {1} {2}/{3}_zpid"
        url = BASE_URL.format(row[5], row[1], row[4], str(row[60]))
        return url.replace(' ', '-').replace('#', 'UNIT')

    def find_image(self, html):
        end_jpg = html.find('.jpg') + 5
        block = html[end_jpg - 100 : end_jpg]
        start_jpg = block.find('href=') + 6
        return block[start_jpg : len(block) -1 ]

    def get_image(self, row):
        """
        Input: a url as a string
        Output: the url link to an image of the house
        """
        url = self.build_link(row)
        params = { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3)'}
        response = requests.get(url, headers=params)
        return self.find_image(response.content)