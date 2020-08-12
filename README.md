# pubmed

Pubmed is a library to work with United States National Library of Medicine (NLM) databases: PubMed and PubMed Central.

Pubmed allows to:
* Send search requests to NLM search engine;
* Download article metadata and save it to files;
* Handle responses to generate a pandas DataFrame.

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
