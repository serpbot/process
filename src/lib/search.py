import time
import random
from urllib.parse import urlparse
from enum import Enum
from bs4 import BeautifulSoup
from requests import get

MAX_NUM_RESULTS = 10

def sleeper():
    time.sleep(random.randrange(3, 11))


def _req(engine, term, results, lang, start, proxies, backoff=5):
    sleeper()
    resp = get(
        url=engine.value[1],
        headers={
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36'},
        params=dict(
            q=term,
            num=results + 1,
            hl=lang,
            start=start
        ) if engine == SearchEngineType.google else
        dict(
            q=term,
            count=results,
            cc=lang,
            offset=start
        ),
        proxies=proxies,
    )
    if resp.status_code == 429:
        # Retry
        time.sleep(backoff)
        backoff = backoff * 2
        print("Retrying...new backoff: %s" % backoff)
        _req(engine, term, results, lang, start, proxies, backoff)
    elif resp.status_code == 200:
        return resp
    else:
        resp.raise_for_status()


class SearchEngineType(Enum):
    google = 1, "https://www.google.com/search"
    bing = 2, "https://www.bing.com/search"


class SearchResult:
    def __init__(self, url, title, description):
        self.url = url
        self.title = title
        self.description = description

    def __repr__(self):
        return f"SearchResult(url={self.url}, title={self.title}, description={self.description})"


def search(engine, term, num_results, lang="en", proxy=None, advanced=False):
    # Proxy
    proxies = None
    if proxy:
        if proxy[:5] == "https":
            proxies = {"https": proxy}
        else:
            proxies = {"http": proxy}

    # Fetch
    start = 0
    while start < num_results:
        # Send request
        resp = _req(engine, term, num_results - start, lang, start, proxies)

        # Parse
        soup = BeautifulSoup(resp.text, 'html.parser')
        result_block = soup.find_all('div',
                                     attrs={'class': 'g'}) if engine == SearchEngineType.google else soup.find_all(
            'li',
            attrs={'class': 'b_algo'})
        for result in result_block:
            # Find link, title, description
            link = result.find('a', href=True)
            title = result.find('h3') if engine == SearchEngineType.google else result.find('h2')
            description = result.find('div', {
                'style': '-webkit-line-clamp:2'}) if engine == SearchEngineType.google else result.find('p')

            if description and engine == SearchEngineType.google:
                description = description.find(
                    'span')

            if description and link and title:
                start += 1
                if advanced:
                    yield SearchResult(link['href'], title.text, description.text)
                else:
                    yield link['href']


def get_rank(engine, term, domain, num_results=MAX_NUM_RESULTS):
    results = search(engine, term, num_results)
    rank = 0
    for result in results:
        rank = rank + 1
        result_domain = urlparse(result).netloc
        if domain in result_domain:
            return rank
    return -1
