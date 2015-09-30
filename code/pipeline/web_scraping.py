import requests
import requesocks
import random
import time
from bs4 import BeautifulSoup as BS
import re
import json
import pandas as pd

class WebScraping(object):
    

    def __init__(self):
        self.urls = []
        self.url_base = "http://www.zillow.com/homes/for_sale/{0}-{1}/{2}_p/"
        self.request_params = { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3)'}
        self.session_proxies = {'http': 'socks5://127.0.0.1:9150', # the default port for tor
                                'https': 'socks5://127.0.0.1:9150'}
        self.city_state = None
        self.html_content = {} # key=city_state, value=list of all html_source for a city_state
        self.df = None


    def whoami(self):
        """
        This is a check to make sure the proxy is working.
        """

        IPCHICKEN = "http://www.ipchicken.com"
        session = requesocks.session()
        session.proxies = self.session_proxies
        response = session.get(IPCHICKEN, headers=self.request_params)
        soup = BS(response.content, 'html.parser')
        return soup.find_all('p')[1].find('b').next.replace(' ', '').replace('\n', '')


    def build_urls(self, city, state, num_requests):
        self.city_state = "{0}-{1}".format(city, state).replace(' ', '-')
        for page_num in xrange(1, num_requests + 1):
            url = self.url_base.format(city, state, page_num)
            self.urls.append(url)

    
    def get_pages(self, sleep_time, proxy=False):
    # have to run tor before the proxy option will work 
        self.html_content[self.city_state] = []
        if proxy == True:
            session = requesocks.session()
            session.proxies = self.session_proxies
            for url in self.urls:
                time.sleep(sleep_time)
                response = session.get(url, headers=self.request_params)
                self.html_content[self.city_state].append(response.content)
        else: # the default is no proxy
            for url in self.urls:
                time.sleep(sleep_time)
                response = requests.get(url, headers=self.request_params)
                self.html_content[self.city_state].append(response.content)


    def extract_all(self, list_html_contents):
        df1 = self.extract_address_and_zpid(list_html_contents)
        df2 = self.extract_house_info(list_html_contents)
        df2 = df2.drop(['isPropertyTypeVacantLand', 'label', 'lot'], axis=1)
        df2 = df2.dropna(subset=['zpid'])
        df2['zpid'] = df2['zpid'].apply(lambda x: 'NA' if x=='' else x)
        df2 = df2[df2.zpid != 'NA']
        df2 = df2.reset_index().drop('index', axis=1)
        df1['zpid'] = df1['zpid'].astype(str)
        df1['zpid'] = df1['zpid'].astype(int)
        df2['zpid'] = df2['zpid'].astype(str)
        df2['zpid'] = df2['zpid'].astype(int)
        merged = df2.merge(df1, on='zpid', how='left')
        merged = merged.dropna(subset=['address'])
        # removes bad addresses
        merged = merged[~(merged['address'].str.contains("XX"))]
        self.df = merged[~(merged['address'].str.contains("(Undisclosed-Address)"))]

    def extract_address_and_zpid(self, list_html_contents):
        '''
        Input: a list of html_source for different web_pages 
        
        Output: a pandas dataframe
        '''
        homes = {}
        for html_doc in list_html_contents:
            soup = BS(html_doc, 'html.parser')
            indices = [m.start() for m in re.finditer('_zpid', html_doc)]
            zids = []
            for index in indices:
                string = html_doc[index - 10: index]
                if "/" in string:
                    string = string[string.find('/') + 1 : index]
                if string not in zids:
                    zids.append(string)
            # builds a list of links from the html_source 
            links =  [res['href'] for res in soup.find_all('a', attrs={"href": True})]
            # Takes links and zids and returns the address of a specific zid
            for link in links:
                for zid in zids:
                    if (zid in link) and ('homedetails' in link):
                        if zid not in homes:
                            start_index = link.find('/', 1)
                            stop_index = link.find('/', start_index + 1)
                            homes[zid] = link[start_index + 1 : stop_index]
        return pd.DataFrame({'zpid': homes.keys(), 'address': homes.values()}, index=range(len(homes)))


    def extract_house_info(self, list_html_contents):
        
        def find_nth(haystack, needle, n):
            # taken from http://stackoverflow.com/questions/1883980/find-the-nth-occurrence-of-substring-in-a-string
            start = haystack.find(needle)
            while start >= 0 and n > 1:
                start = haystack.find(needle, start+len(needle))
                n -= 1
            return start

        def convert_price(row):
            price = row.replace('$', '')
            price = price.replace('.', '')
            try:
                if price[-1] == 'M': # add five zero's
                    price = price.replace('M', '00000')
                    return int(price)
                if price[-1] == 'K': # add three zero's
                    price = price.replace('K', '000')
                    return int(price)
            except:
                return price
        master_df = pd.DataFrame(columns=['bath', 'bed', 'isPropertyTypeVacantLand', 
                                        'label', 'lot', 'sqft', 'zpid', 'price'])
        for html in list_html_contents:
            res = []
            num_minibubbles = html.count('minibubble')
            for n in xrange(1, num_minibubbles):
                info = {}
                start_body = find_nth(html, 'minibubble', n)
                stop_body = start_body + 500
                body = html[start_body : stop_body + 1]
                start = body.find('{')
                stop = body.find('}')
                minibubble = body[start : stop + 1]  
                start_zpid = body.find('zpid_')
                stop_zpid = start_zpid + body[start_zpid:].find('"')
                zpid = body[start_zpid : stop_zpid]
                info = json.loads(minibubble.replace('\\', ''))
                info['zpid'] = zpid[5:]
                
                res.append(info)
            df = pd.DataFrame(res)[['bath', 'bed', 'isPropertyTypeVacantLand',
                                    'label', 'sqft', 'zpid']]
            df['isVavcantLand'] = df['isPropertyTypeVacantLand']
            df['price'] = df['label'].apply(convert_price)
            df = df.drop('label', axis=1)
            master_df = pd.concat([master_df, df])

        return master_df

