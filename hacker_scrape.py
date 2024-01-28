import requests
import os
from bs4 import BeautifulSoup, SoupStrainer
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


def scraper(NUM_PAGES_TO_SCRAPE, TOP_N, RANK_BY):
    """
    NUM_PAGES_TO_SCRAPE : number of pages to scrape
    TOP_N : number of articles to fetch
    RANK_BY : Column on which ranking will be computed
    
    """
    stats = []
    for page_no in range(1, NUM_PAGES_TO_SCRAPE + 1):
        try:
            res = requests.get('https://news.ycombinator.com/?p='+str(page_no))
            only_td = SoupStrainer('td')
            soup = BeautifulSoup(res.content, 'html.parser', parse_only=only_td)
            tdtitle = soup.find_all('td', attrs={'class':'title'})
            tdmetrics = soup.find_all('td', attrs={'class':'subtext'})
            tdrank = soup.find_all('td', attrs={'class':'title', 'align':'right'})
            td_with_morelink = soup.select_one('td.title a.morelink')
        
            tdtitleonly = [t for t in tdtitle if t not in tdrank]
            
        
        
            for i in range(len(tdtitleonly)-1):
            
                page = {}
                page["rank"] = tdrank[i].find('span', attrs={'class':'rank'}).get_text().rstrip('.')
                page["title"] = tdtitleonly[i].find('a').get_text()
                page["url"] = tdtitleonly[i].find('a')['href']
                score = tdmetrics[i].find('span', attrs={'class':'score'})
                page["score"] = score.text.split()[0] if score else None
                stats.append(page)

           
        except (requests.ConnectionError, requests.packages.urllib3.exceptions.ConnectionError) as e:
            print('Connection Failed for page {}'.format(i))
        except requests.RequestException as e:
            print("Some ambiguous Request Exception occurred. The exception is "+str(e))
    df = pd.DataFrame(stats) 
    df['rank'] = pd.to_numeric(df['rank'], errors='coerce')
    df['score'] = pd.to_numeric(df['score'], errors='coerce')
            
    if RANK_BY == 'rank': 
         print(df.nsmallest(TOP_N, 'rank'))  
    elif RANK_BY == 'score': 
        print(df.nlargest(TOP_N, 'score'))

if __name__ == '__main__':

    try:
        NUM_PAGES_TO_SCRAPE = int(os.getenv('NUM_PAGES_TO_SCRAPE'))
        TOP_N = int(os.getenv('TOP_N'))
        RANK_BY=os.getenv('RANK_BY')
        
        scraper(NUM_PAGES_TO_SCRAPE, TOP_N, RANK_BY)
           
    except ValueError as e:
        print('\nInvalid input\n')
        