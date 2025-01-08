#--- Imports ---#
from whoosh.fields import *
from whoosh import index
from whoosh.qparser import QueryParser

from flask import Flask, redirect, url_for, request, render_template

import traceback


#--- Functions ---#
def index_exists():
    """Check existence of an index."""
    try:
        ix = index.open_dir("indexdir")
        return True
    except:
        return False



def run_search(input_query: str):
    """Perform search on index.
    - input_query: search query from user"""
    
    ix = index.open_dir("indexdir")
    
    with ix.searcher() as searcher:
        # check for documents that contain search query
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



#--- Flask app ---#
app = Flask(__name__)

@app.errorhandler(500)
def internal_error(exception):
   return "<pre>"+traceback.format_exc()+"</pre>"

# redirect from url "/" to "/home" or to "/no_index"
@app.route("/")
def redirect_to_home():
    if index_exists():
        return redirect(url_for("home"))
    else:
        return redirect(url_for("no_index"))

# home page with search query input
@app.route("/home")
def home():
    # index check
    # --> to avoid user manually going to /home
    if index_exists():
        return render_template("home.html")    
    else:
        return redirect(url_for("no_index"))

# landing page when no index is found
@app.route("/no_index")
def no_index():
    return render_template("no_index.html")

# page with search results
# also checks for existence of index
@app.route("/search")
def search():
    # index check
    # --> to avoid user manually going to /search
    if index_exists():
        input_query = request.args.get("search_input")
        if input_query == "":
            return render_template("home.html")

        search_results = run_search(input_query)

        return render_template("search.html", results=search_results)
    else:
        return redirect(url_for("no_index"))


    





















