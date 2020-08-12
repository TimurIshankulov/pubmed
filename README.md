# Pubmed

Pubmed is a python library to work with United States National Library of Medicine (NLM) databases: PubMed and PubMed Central.

Pubmed allows to:
* Send search requests to NLM search engine;
* Download article metadata and save it to files;
* Handle responses to generate a pandas DataFrame.

## Configuration

All settings are storing in **config.py** file. You should create it by copying **config.py.template**.

The most important setting is an API key which could be obtained after registering on the NLM website.

API key allows you to interact with NLM API services, it is neccessary to get started with NLM databases.

## Examples

Usage of this module is simple:

```python
import pubmed

article_ids = pubmed.download_all_query_responses(query, db, refresh=False)
items = pubmed.handle_query_responses(db, article_ids)
```

Argument *db* has two possible options: 'pubmed' or 'pmc'.

Argument *query* is a text string with search query.

After handling all the responses a pandas DataFrame will be returned. It contains all values parsed from downloaded article metadata.
