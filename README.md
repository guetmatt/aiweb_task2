# Search Engine

This is a search engine for the website of the Institute of Cognitive Science at Osnabrueck University. The program crawls the website and builds and index. The user can then perform a text search on the index to find all pages including the search query. To use this application, install the requriements and run the command ```flask --app app.py run``` in a command line. 

Before using the app, install the requirements.
To build the search index, run the command ```python crawler.py``` in a command line.
To use the flask application, run the command ```flask --app app.py run``` in a command line.

The search engine will not work without a search index.