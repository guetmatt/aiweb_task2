import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import defaultdict






### INDEX SETUP ###
index = defaultdict(set)

def add_content_to_index(content: str, url: str):
    tokens = content.split()
    for tok in tokens:
        tok = tok.strip(".!?()[]{};:,\\/").lower()
        index[tok].add(url)


### SEARCH FUNCTION ###

def search(index: dict, query: list):

    pages = set(index[query[0].lower()])
    # print(pages)
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
            add_content_to_index(text, url)

            for page in soup.find_all("a"):
                page_url = urljoin(url, page["href"])
                
                if page_url in done_url:
                    continue

                if urlparse(page_url).netloc == urlparse(start_url).netloc:
                    agenda.add(page_url)

    except requests.exceptions.RequestException as e:
        print(f"Error: not able to crawl url {url}")


test = search(index, ["might", "home"])
print(test)




# ### INDEX WITH WOOSH ###

# schema = Schema(title=TEXT(stored=True), content=TEXT)

# # Create an index in the directory indexdr (the directory must already exist!)
# index = create_in("indexdir", schema)
# writer = index.writer()

# # now let's add some texts (=documents)
# writer.add_document(title=u"First document", content=u"This is the first document we've added!")
# writer.add_document(title=u"Second document", content=u"The second one is even more interesting!")
# writer.add_document(title=u"Songtext", content=u"Music was my first love and it will be the last")
# writer.add_document(title=u"Test", content=u"This is the first and the last time I am gonna do this!")

# # write the index to the disk
# writer.commit()

# # Retrieving data
# with index.searcher() as searcher:
#     # find entries with the words 'first' AND 'last'
#     query = QueryParser("content", index.schema).parse("first last")
#     results = searcher.search(query)

#     # print all results
#     for r in results:
#         print(r)
