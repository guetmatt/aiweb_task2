#--- Imports ---#
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from whoosh.index import create_in
from whoosh.fields import *



#--- Functions ---#
def build_index(max_depth=5, max_links=50):
    """Crawl the ikw-uni-osnabrueck website and build an index.
    Two parameters for runtime optimization.
    - max_depth for amount subpages to crawl
    - max_links for amount of links crawled 
    """

    # user information
    print("--- building index, please wait a moment ---")

    # setup for index
    # scores of terms in title boosted by field_boost 
    schema = Schema(title=TEXT(stored=True, field_boost=2.0),
                    url=ID(stored=True), content=TEXT(stored=True))
    ix = create_in("indexdir", schema)
    writer = ix.writer()

    # url to start crawling from
    # start_url = "https://vm009.rz.uos.de/crawl/index.html"
    start_url = "https://www.ikw.uni-osnabrueck.de/en/home.html"

    # links to crawl --> tuples with url and search depth 
    agenda = [(start_url, 0)]
    # links added to index
    done_url = set()
    # count for max_links
    count_links = 0 
    
    while agenda and count_links <= max_links:
        # get next url to crawl
        url, depth = agenda.pop()
        
        # max search depth exceeded by current url
        if depth > max_depth:
            continue
        
        # url already crawled
        if url in done_url:
            continue

        done_url.add(url)
        count_links += 1

        try:
            # request current url
            r = requests.get(url, timeout=5)

            # if url available, crawl content
            if r.status_code == 200:
                soup = BeautifulSoup(r.content, "html.parser")

                # find url's to other pages
                for page in soup.find_all("a", href=True):
                    page_url = urljoin(url, page["href"])
                    
                    # if url's to other pages are on same server as start_url
                    # --> add to agenda
                    if urlparse(page_url).netloc == urlparse(start_url).netloc:
                        agenda.append((page_url, depth+1))
                
                # text from current url
                # str(...) to avoid RecursionError
                text = str(soup.get_text(" ", strip=True))
                
                # title from current url
                if soup.title:
                    title = str(soup.title.string)
                else:
                    title = "Untitled"
                
                # add to index
                writer.add_document(title=title, url=url, content=text)

        # Error handling
        except requests.exceptions.RequestException as e:
            print(f"Error: not able to crawl url {url}")
    
    # write index to disk
    writer.commit()

    print("--- index finished ---")

    return None



#--- Boilerplate ---#
if __name__ == "__main__":
    build_index()