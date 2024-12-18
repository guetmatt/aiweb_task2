import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import defaultdict

from whoosh.index import create_in
from whoosh.fields import *
from whoosh import index






### INDEX WITH WHOOSH ###
schema = Schema(title=TEXT(stored=True), content=TEXT)
index = create_in("indexdir", schema)
writer = index.writer()




### INDEX SETUP ###
# index = defaultdict(set)

# def add_content_to_index(content: str, url: str):
#     tokens = content.split()
#     for tok in tokens:
#         tok = tok.strip(".!?()[]{};:,\\/").lower()
#         index[tok].add(url)


### SEARCH FUNCTION ###

def search(index: dict, query: list):
    pages = set(index[query[0].lower()])

    for word in query:
        pages = pages & set(index[word.lower()])
    
    return pages




### CRAWLER AND INDEX ###

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


# test = search(index, ["might", "home"])
# print(test)

