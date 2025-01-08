# Search Engine

This is a search engine for the website of the Institute of Cognitive Science at Osnabrueck University. The program crawls the website and builds and index. The user can then perform a text search on the index to find all pages including the search query.

Before using the app, install the requirements from the file ```requirements.txt```.
To build the search index, run the command ```python crawler.py``` in a command line.
To use the search engine, run the command ```flask --app app.py run``` in a command line.

The search engine will not work without a search index.