import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque

from whoosh.index import create_in
from whoosh.fields import *
from whoosh import index
from whoosh.qparser import QueryParser

from flask import Flask, redirect, url_for, request, render_template




#-----------------#
#--- Functions ---#
#-----------------#


def build_index(max_depth=3, max_links=50):
    """Crawl the ikw-uni-osnabrueck website and build an index.
    Two parameters for runtime optimization.
    - max_depth for amount subpages to crawl
    - max_links for amount of links crawled 
    """

    # setup for index 
    schema = Schema(title=TEXT(stored=True), url=TEXT(stored=True), content=TEXT(stored=True))
    ix = create_in("indexdir", schema)
    writer = ix.writer()

    # url to start crawling from
    # crawler will stay on same server as this url
    start_url = "https://www.ikw.uni-osnabrueck.de/en/home.html"

    # links to crawl, deque for runtime optimzation
    agenda = deque([(start_url, 0)]) 
    # links added to index
    done_url = set()
    # count for max_links
    count_links = 0 
    
    while agenda and count_links <= max_links:
        # get next url to crawl
        url, depth = agenda.popleft()
        
        if depth > max_depth:
            continue

        done_url.add(url)
        count_links += 1

        try:
            # request current url
            r = requests.get(url, timeout=5)

            # if url available, crawl content
            if r.status_code == 200:
                soup = BeautifulSoup(r.content, "html.parser")
                
                # text from url
                # str(...) to avoid RecursionError
                text = str(soup.get_text(" ", strip=True))
                
                # title from url
                if soup.title:
                    title = str(soup.title.string)
                else:
                    title = "Untitled"
                
                # add to index
                writer.add_document(title=title, url=url, content=text)

                # find url's to other pages
                for page in soup.find_all("a", href=True):
                    page_url = urljoin(url, page["href"])

                    # url already crawled
                    if page_url in done_url:
                        continue
                    
                    # if found url's are on same server as start_url
                    # --> add to url's to crawl
                    if urlparse(page_url).netloc == urlparse(start_url).netloc:
                        agenda.append((page_url, depth+1))

        # Error handling
        except requests.exceptions.RequestException as e:
            print(f"Error: not able to crawl url {url}")
    
    # write index to disk
    writer.commit()

    return None


def run_search(input_query: str):
    """Perform search on index.
    - input_query: search query from user"""
    
    ix = index.open_dir("indexdir")
    with ix.searcher() as searcher:
        # check for documents where query appears in
        query = QueryParser("content", ix.schema).parse(input_query)
        results = searcher.search(query)

        # no matching documents
        if len(results) == 0:
            result_links = [
                {
                    "url": "",
                    "title": "",
                    "content": "No matching documents found."
                }]
        # matching documents
        else:
            result_links = [
                {
                    "url": result["url"],
                    "title": result["title"],
                    "content": result["content"][:200] + "..."
                }
                for result in results]

    return result_links


#-----------------#
#--- FLASK APP ---#
#-----------------#

app = Flask(__name__)

# redirect from "/" to "/home"
@app.route("/")
def redirect_to_home():
    # crawl web and build index
    build_index()
    return redirect(url_for("home"))


# home page with search query input
@app.route("/home")
def home():
    return render_template("home.html")


# page with search results
@app.route("/search")
def search():
    input_query = request.args.get("search_input")
    if input_query == "":
        return render_template("home.html")
    
    search_results = run_search(input_query)

    return render_template("search.html", results=search_results)


    





















