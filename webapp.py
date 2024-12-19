import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque

from whoosh.index import create_in
from whoosh.fields import *
from whoosh import index
from whoosh.qparser import QueryParser

from flask import Flask, redirect, url_for, request, render_template, render_template_string

app = Flask(__name__)



### FUNCTIONS ###
def run_search(input_query: str):
    
    ix = index.open_dir("indexdir")
    with ix.searcher() as searcher:
        query = QueryParser("content", ix.schema).parse(input_query)
        results = searcher.search(query)

        if len(results) == 0:
            result_links = [
                {
                    "url": "",
                    "title": "",
                    "content": "No matching documents found."
                }]
        else:
            result_links = [
                {
                    "url": result["url"],
                    "title": result["title"],
                    "content": result["content"][:200] + "..."
                }
                for result in results]

    return result_links


def build_index(max_depth=3, max_links=50):
    # crawler and index 
    schema = Schema(title=TEXT(stored=True), url=TEXT(stored=True), content=TEXT(stored=True))
    ix = create_in("indexdir", schema)
    writer = ix.writer()

    start_url = "https://www.ikw.uni-osnabrueck.de/en/home.html"
    # start_url = "https://vm009.rz.uos.de/crawl/index.html"
    # agenda = {start_url}

    # deque for runtime optimization
    agenda = deque([(start_url, 0)])
    done_url = set()
    count_links = 0
    
    while agenda and count_links <= max_links:
        url, depth = agenda.popleft()
        if depth > max_depth:
            continue

        done_url.add(url)
        count_links += 1

        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                soup = BeautifulSoup(r.content, "html.parser")
                
                # str(...) for recursion optimization
                text = str(soup.get_text(" ", strip=True))
                if soup.title:
                    title = str(soup.title.string)
                else:
                    title = "Untitled"
                writer.add_document(title=title, url=url, content=text)

                for page in soup.find_all("a", href=True):
                    page_url = urljoin(url, page["href"])
                
                    if page_url in done_url:
                        continue

                    if urlparse(page_url).netloc == urlparse(start_url).netloc:
                        # agenda.add(page_url)
                        agenda.append((page_url, depth+1))

        except requests.exceptions.RequestException as e:
            print(f"Error: not able to crawl url {url}")
    
    # write index to disk
    writer.commit()



### FLASK APP ###

# redirect from "/" to "/home"
# --> seems more user friendly
@app.route("/")
def redirect_to_home():
    build_index()
    return redirect(url_for("home"))


# home page with crawler and index
@app.route("/home")
def home():
    return render_template("home.html")



@app.route("/search")
def search():
    input_query = request.args.get("search_input")
    if input_query == "":
        return "No search query entered."
    
    search_results = run_search(input_query)

    return render_template("search.html", results=search_results)


    





















