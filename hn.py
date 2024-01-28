import requests
import os
from bs4 import BeautifulSoup, SoupStrainer
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

'''
@params page_no: The page number of HackerNews to fetch.
Adding only page number in order to add multiprocess support in future.
@params verbose: Adds verbose output to screen instead of running the program silently.
'''
def fetch(page_no, verbose=False):
    #Should be unreachable, but just in case
    if page_no <= 0:
        raise ValueError('Number of Pages must be greater than zero')
    page_no = min(page_no, 20)
    i = page_no
    if verbose:
        print('Fetching Page {}...'.format(i))
    try:
        res = requests.get('https://news.ycombinator.com/?p='+str(i))
        only_td = SoupStrainer('td')
        soup = BeautifulSoup(res.content, 'html.parser', parse_only=only_td)
        tdtitle = soup.find_all('td', attrs={'class':'title'})
        tdmetrics = soup.find_all('td', attrs={'class':'subtext'})
        tdrank = soup.find_all('td', attrs={'class':'title', 'align':'right'})
        td_with_morelink = soup.select_one('td.title a.morelink')
        
        tdtitleonly = [t for t in tdtitle if t not in tdrank]
        stats = []
        
        
        for i in range(len(tdtitleonly)-1):
            
            page = {}
            page["rank"] = tdrank[i].find('span', attrs={'class':'rank'}).get_text().rstrip('.')
            page["title"] = tdtitleonly[i].find('a').get_text()
            page["url"] = tdtitleonly[i].find('a')['href']
            score = tdmetrics[i].find('span', attrs={'class':'score'})
            page["score"] = score.text.split()[0] if score else None
            stats.append(page)
        df = pd.DataFrame(stats) 
        df['rank'] = pd.to_numeric(df['rank'], errors='coerce')
        df['score'] = pd.to_numeric(df['score'], errors='coerce')
    
        print(df.nlargest(20, 'score'))  
        print(df.dtypes)
    except (requests.ConnectionError, requests.packages.urllib3.exceptions.ConnectionError) as e:
        print('Connection Failed for page {}'.format(i))
    except requests.RequestException as e:
        print("Some ambiguous Request Exception occurred. The exception is "+str(e))
while(True):
    try:
        pages = int(input('Enter number of pages that you want the HackerNews for (max 20): '))
        v = input('Want verbose output y/[n] ?')
        verbose = v.lower().startswith('y')
        if pages > 20:
            print('A maximum of only 20 pages can be fetched')
        pages = min(pages, 20)
        for page_no in range(1, pages + 1):
            fetch(page_no, verbose)
        break   
    except ValueError as e:
        print('\nInvalid input, probably not a positive integer\n')
        continue