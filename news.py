import json
import re
from bs4 import BeautifulSoup
import requests
from unidecode import unidecode

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 Edg/95.0.1020.53'
}



with open('sources.json', 'r') as f:
    sources = json.load(f)

def theguardian(url: str) -> dict:
    res = []
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')

    articles = soup.find_all('div', {'class': 'fc-item'})

    for article in articles:
        title_wrapper = article.find('div', {'class': 'fc-item__content'}) if article else None
        title = title_wrapper.find('h3', {'class': 'fc-item__title'}).text if title_wrapper else None
        title = unidecode(u' / '.join(title.strip().split('  '))) if title else None
        link = title_wrapper.find('a', {'class': 'fc-item__link'})['href'] if title_wrapper else None
        description_wrapper = title_wrapper.find('div', {'class': 'fc-item__standfirst'}) if title_wrapper else None
        description = unidecode(description_wrapper.text.strip()) if description_wrapper else None
        if title:
            res.append({
                'title': title,
                'link': link,
                'description': description
            })
    return res

# CNN no scraping?
def cnn(url: str) -> dict:
    res = []
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')

    articles = soup.find_all('article')
    print(soup.text)
    for article in articles:
        link_wrapper = article.find('a') if article else None
        link = link_wrapper['href'] if link_wrapper else None
        title = unidecode(link_wrapper.text.strip()) if link_wrapper else None
        if title:
            res.append({
                'title': title,
                'link': link,
                'description': None
            })
    return res

def nytimes(url: str) -> dict:
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
        if title:
            res.append({
                'title': title,
                'link': link,
                'description': description
            })
    return res

def sort(url: str) -> dict:
    match = re.search(r'https:\/\/www\.(\w+)\.com', url)
    source = match.group(1)
    if source == 'cnn':
        return cnn(url)
    elif source == 'theguardian':
        return theguardian(url)
    elif source == 'nytimes':
        return nytimes(url)
    return {}

# Only working endpoint is headlines for now (different page formats for other endpoints)
def call(endpoint: str = 'headlines', n_articles: int = 10) -> dict:
    response = {
        endpoint: []
    }
    urls = sources[endpoint]
    for url in urls:
        response[endpoint] += sort(url)
    return response


response = call()
with open('response.json', 'w') as f:
    json.dump(response, f)
