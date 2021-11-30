import json
import re
from bs4 import BeautifulSoup
import requests
from unidecode import unidecode
import sys
import random

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 Edg/95.0.1020.53'
}

class NewsScraper:
    def __init__(self):
        with open('sources.json', 'r') as f:
            self.sources = json.load(f)

    def theguardian(self, url: str) -> dict:
        res = []
        r = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')

        articles = soup.find_all('div', {'class': 'fc-item'})

        for article in articles:
            title_wrapper = article.find('div', {'class': 'fc-item__content'}) if article else None
            kicker_wrapper = title_wrapper.find('span', {'class': 'fc-item__kicker'}) if title_wrapper else None
            kicker = unidecode(kicker_wrapper.text.strip()) if kicker_wrapper else None
            headline_wrapper = title_wrapper.find('span', {'class': 'fc-item__headline'}) if title_wrapper else None
            headline = unidecode(headline_wrapper.text.strip()) if headline_wrapper else None
            title = (kicker if kicker else '') + (' / ' if kicker else '') + (headline if headline else '')
            link = title_wrapper.find('a', {'class': 'fc-item__link'})['href'] if title_wrapper else None
            description_wrapper = title_wrapper.find('div', {'class': 'fc-item__standfirst'}) if title_wrapper else None
            description = unidecode(description_wrapper.text.strip()) if description_wrapper else None
            img_wrapper = article.find('img') if article else None
            img = img_wrapper['src'] if img_wrapper else None
            if title and link:
                res.append({
                    'title': title,
                    'link': link,
                    'description': description,
                    'image': img,
                    'source': 'theguardian'
                })
        return res

    def nytimes(self, url: str) -> dict:
        res = []
        r = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')

        articles = soup.find_all('section', {'class': 'story-wrapper'})

        for article in articles:
            link_wrapper = article.find('a') if article else None
            link = link_wrapper['href'] if link_wrapper else None
            title_wrapper = article.find('h3', {'color': 'primary'}) if article else None
            title = unidecode(title_wrapper.text.strip()) if title_wrapper else None
            description_wrapper = article.find('p') if article else None
            description = unidecode(description_wrapper.text.strip()) if description_wrapper else None
            img_wrapper = article.find('img') if article else None
            img = img_wrapper['src'] if img_wrapper else None
            if title and link:
                res.append({
                    'title': title,
                    'link': link,
                    'description': description,
                    'image': img,
                    'source': 'nytimes'
                })
        return res

    def usatoday(self, url: str) -> dict:
        res = []
        r = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')

        articles = soup.find_all('a', {'href': re.compile("story")})
        for article in articles:
            title = unidecode(article.text.strip())
            link = article['href']
            img_wrapper = article.find('img')
            img = (img_wrapper['src'] if 'src' in img_wrapper.attrs else img_wrapper['data-gl-src']) if img_wrapper else None
            if title and link:
                res.append({
                    'title': title,
                    'link': link,
                    'description': None,
                    'image': img,
                    'source': 'usatoday'
                })
        return res


    def sort(self, url: str) -> dict:
        match = re.search(r'https:\/\/www\.(\w+)\.com', url)
        source = match.group(1)
        if source == 'usatoday':
            return self.usatoday(url)
        elif source == 'theguardian':
            return self.theguardian(url)
        elif source == 'nytimes':
            return self.nytimes(url)
        return {}

    # Only working endpoint is headlines for now (different page formats for other endpoints)
    def call(self, endpoint: str = 'headlines', n_articles: int = 10) -> dict:
        response = {
            endpoint: []
        }

        urls = self.sources[endpoint]

        for url in urls:
            response[endpoint] += self.sort(url)
        
        random.shuffle(response[endpoint])
        response[endpoint] = response[endpoint][:n_articles]
        
        return response



# response = call()
# with open('response.json', 'w') as f:
#     json.dump(response, f)

def main():
    endpoint = str(sys.argv[1])
    n_articles = int(sys.argv[2])

    scraper = NewsScraper()
    response = scraper.call(endpoint, n_articles)

    print(json.dumps(response, indent=4))
    sys.stdout.flush()

def test():
    scraper = NewsScraper()
    # response = scraper.call("headlines", 10)
    print(scraper.usatoday("https://www.usatoday.com/"))
    #print(json.dumps(response, indent=4))
    #sys.stdout.flush()

def lambda_handler(event, context):
    try:
        scraper = NewsScraper()
        response = scraper.call(event['endpoint'], event['n_articles'])
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(response)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }