import time
import random

from enum import Enum
from bs4 import BeautifulSoup
from requests import get


def sleeper():
    time.sleep(random.randrange(3, 11))


def _req(url, ua, term, results, lang, start, proxies, backoff=5):
    sleeper()
    resp = get(
        url=url,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'},
        params=dict(
            q=term,
            num=results + 2,  # Prevents multiple requests
            hl=lang,
            start=start,
        ),
        proxies=proxies,
    )
    if resp.status_code == 429:
        # Retry
        time.sleep(backoff)
        backoff = backoff * 2
        print("Retrying...new backoff: %s" % backoff)
        _req(url, ua, term, results, lang, start, proxies, backoff)
    elif resp.status_code == 200:
        return resp
    else:
        resp.raise_for_status()


class SearchEngineType(Enum):
    google = 1, "https://www.google.com/search"
    bing = 2, "https://www.bing.com/search"

    def __str__(self):
        return self.value[1]


class SearchResult:
    def __init__(self, url, title, description):
        self.url = url
        self.title = title
        self.description = description

    def __repr__(self):
        return f"SearchResult(url={self.url}, title={self.title}, description={self.description})"


def search(engine, term, num_results=10, lang="en", proxy=None, advanced=True):
    location = 'fake_user_agent.json'
    ua = UserAgent(use_cache_server=False, path=location)

    escaped_term = term.replace(' ', '+')

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
        resp = _req(engine, ua, escaped_term, num_results - start, lang, start, proxies)

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
