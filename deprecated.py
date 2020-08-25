from pymed import PubMed


def get_items_pubmed(fullname):
    """
    Makes request to Pubmed database using pymed library.
    Returns DataFrame with all articles authored by <fullname>.
    Deprecated.
    """
    items = pd.DataFrame(columns=['fullname', 'pubmed_id', 'title', 'abstract', 'keywords', 'journal', 'publication_date',
                                  'authors', 'affiliations', 'methods', 'conclusions', 'results', 'copyrights', 'doi'])
    
    lastname = fullname.split()[0]
    firstname = fullname.split()[1]
    query = '{0}, {1}[Author]'.format(lastname, firstname)
    
    pubmed = PubMed(tool=tool, email=email)
    results = pubmed.query(query, max_results=max_results)
    
    while True:
        try:
            result = next(results)
            result_dict = result.toDict()
            result_dict['fullname'] = fullname
            result_dict['affiliations'] = [author['affiliation'] for author in result_dict['authors']]
            result_dict['affiliations'] = '; '.join(result_dict['affiliations'])
            result_dict['authors'] = [' '.join([author['lastname'], author['firstname']]) for author in result_dict['authors']]
            result_dict['authors'] = '; '.join(result_dict['authors'])
            result_dict['keywords'] = '; '.join(result_dict['keywords'])
            result_dict['pubmed_id'] = result_dict['pubmed_id'].replace('\n', '; ')
            del result_dict['xml']
            items = items.append(result_dict, ignore_index=True)
        except StopIteration:
            break
    
    return items


def add_pmc_id(items):
    """Add PMC ID to <items> DataFrame"""
    params = {
        'format': 'json',
        'dbfrom': 'pubmed',
        'linkname': 'pubmed_pmc',
        'api_key': api_key
    }
    
    if not 'pmc_id' in items.columns:
        items.insert(2, 'pmc_id', pd.np.nan)
    
    for i in range(0, len(items)):
        params['id'] = items.loc[i, 'pubmed_id']
        try:
            response = requests.get(url=url_pubmed_to_pmc, headers=headers, params=params)
        except requests.RequestException:
            print('Problem has occured with Pubmed ID: {0}'.format(params['id']))
        else:
            data = response.json()
            if 'linksetdbs' in data['linksets'][0]:
                items.loc[i, 'pmc_id'] = data['linksets'][0]['linksetdbs'][0]['links'][0]
    return items


def download_query_response(article_id, db, refresh=False):
    """Saves article query response with <article_id> identifier to file"""
    params = {
        'db'      : db,
        'id'      : article_id,
        'api_key' : api_key,
        'retmode' : retmode
    }
    
    filename = os.path.join(db, str(article_id))
    if (os.path.exists(filename)) and (not refresh):
        pass
    else:
        try:
            response = requests.get(url=url_fetch, headers=headers, params=params)
        except requests.RequestException:
            print('Problem has occured with {0} ID: {1}'.format(db, article_id))
        else:
            data = response.text
            with open(filename, 'w+', encoding='utf-8') as f:
                f.write(data)


def handle_query_responses(db, article_ids):
    """Returns articles DataFrame generated from files"""
    items_list = []
    filenames = [os.path.join(db, str(article_id)) for article_id in article_ids]
    items = pd.DataFrame(columns=columns[db])
    
    for i in tqdm.tqdm(range(len(filenames))):
        root = get_element_tree(filenames[i])
        if db == 'pmc':
            item = parse_element_tree_pmc(root)
        elif db == 'pubmed':
            item = parse_element_tree_pubmed(root)
        item['file_size'] = os.path.getsize(filenames[i])
        items_list.append(item)
        if i % 5000 == 0:
            items.to_csv('database/tmp.csv', sep='|', index=False)

    items = items.append(items_list)
    return items
