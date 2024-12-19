import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import defaultdict

from whoosh.index import create_in
from whoosh.fields import *
from whoosh import index
from whoosh.qparser import QueryParser



### INDEX WITH WHOOSH ###
schema = Schema(title=TEXT(stored=True), content=TEXT)
index = create_in("indexdir", schema)
writer = index.writer()

### SEARCH WITH WHOOSH ###

def search(index, input_query: str):
    
    with index.searcher() as searcher:
        query = QueryParser("content", index.schema).parse(input_query)
        results = searcher.search(query)

        # print all results
        for r in results:
            print(r)
    
    return results


### CRAWLER WITH INDEX CREATION ###

prefix = "https://vm009.rz.uos.de/crawl/"
start_url = prefix+"index.html"
agenda = {start_url}
done_url = set()

while agenda:
    url = agenda.pop()
    done_url.add(url)

    try:
        r = requests.get(url)
        if r.status_code == 200:
            soup = BeautifulSoup(r.content, "html.parser")
            
            # text content from url for index
            text = soup.get_text(" ", strip=True)
            # add_content_to_index(text, url)
            writer.add_document(title=url, content=text)

            for page in soup.find_all("a"):
                page_url = urljoin(url, page["href"])
                
                if page_url in done_url:
                    continue

                if urlparse(page_url).netloc == urlparse(start_url).netloc:
                    agenda.add(page_url)

    except requests.exceptions.RequestException as e:
        print(f"Error: not able to crawl url {url}")

# write index to disk
writer.commit()

# test search
test = search(index, "HOME might")
print(test)

