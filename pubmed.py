import datetime
import json
import os
import sys
import time
import xml.etree.ElementTree as ET

import MySQLdb
import numpy as np
import pandas as pd
import requests
from IPython.display import clear_output
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
#from tqdm import notebook as tqdm
import tqdm.auto as tqdm

from config import api_key, max_results, retmode
from config import conn_string
from models.pubmed_model import Base, PubmedArticle, PMCArticle

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' + \
                         'Chrome/84.0.4147.105 Safari/537.36'
}

dbs = ['pmc', 'pubmed', 'database']
for db in dbs:
    if not os.path.exists(db):
        os.makedirs(db)

files_stoplist = ['6796246', '4669991', '4212306', '4070603', '4912513', '2799065', '5042924', '6032109', '5042923',
                  '6555104', '5724662', '5493079', '6117636', '5933288', '6763540', '6493311', '6737605', '5637785']

url_pubmed_to_pmc = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi'
url_fetch         = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'
url_search        = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'

columns = {'pubmed': ['pmid', 'pmc', 'pii', 'mid', 'doi', 'elocation_id', 'language',
                      'title', 'authors', 'affiliations', 'article_type', 'publication_type',
                      'journal_title', 'volume', 'issue', 'pages', 'pub_date',
                      'issn_electronic', 'issn_print', 'journal_iso_abbr',
                      'publisher_name', 'publisher_location', 'publisher_nlm_id', 'publisher_issn_linking',
                      'abstract_len', 'abstract', 'copyright',
                      'mesh_quals_major', 'mesh_quals_minor', 'mesh_descriptors', 'keywords'],
           'pmc': ['pmid', 'pmc', 'pii', 'doi', 'art-access-id', 'sici', 'pmc-scan', 'medline', 'manuscript', 'other',
                   'title', 'authors', 'affiliations', 'article-type', 'category',
                   'journal_title', 'volume', 'issue', 'pages', 'pub_date', 'issn_epub', 'issn_ppub',
                   'publisher_name', 'publisher_loc', 'publisher-id', 'elocation-id', 'publisher-manuscript',
                   'journal-id_nlm-ta', 'journal-id_pubmed-jr-id', 'journal-id_issn', 'journal-id_pmc',
                   'journal-id_doi', 'journal-id_coden', 'journal-id_publisher-id', 'journal-id_hwp',
                   'journal-id_nlm-journal-id', 'journal-id_iso-abbrev',
                   'abstract_len', 'abstract', 'full_text_len', 'full_text',
                   'license-type', 'license', 'copyright', 'keywords']
}

engine_pubmed = create_engine(conn_string)
Base.metadata.bind = engine_pubmed
DBSession_pubmed = sessionmaker(bind=engine_pubmed)
session = DBSession_pubmed()

#sessions = {'pubmed': session_pubmed}

def parse_pub_date(subroot, pub_type):
    """Returns parsed publication date from given ET <subroot>"""
    pub_date = np.NaN
    pub_dates = subroot.findall('pub-date')
    for pub_record in pub_dates:
        if (pub_record.attrib.get('pub-type', '') == pub_type or
            pub_record.attrib.get('date-type', '') == 'pub'):
            day = pub_record.find('day')
            month = pub_record.find('month')
            year = pub_record.find('year')
            if year is not None:
                pub_date = year.text
                if month is not None:
                    pub_date += '-' + month.text
                    if day is not None:
                        pub_date += '-' + day.text
    if pub_date is np.NaN:
        pub_date = parse_pub_date(subroot, 'ppub')
    return pub_date


def parse_authors(subroot, path):
    """Returns parsed authors string from given ET <subroot>"""
    authors = []
    contributors = subroot.findall(path)
    if contributors is not None:
        for contributor in contributors:
            fullname = ''
            affiliation_links = ''
            for contributor_meta in contributor.iter('name'):
                surname = contributor_meta.find('surname')
                given_name = contributor_meta.find('given-names')
                if (surname is not None) and (given_name is not None):
                    surname = surname.text if surname.text is not None else ''
                    given_name = given_name.text if given_name.text is not None else ''
                    fullname = ' '.join([given_name, surname])
            affiliations = contributor.findall('xref')  # Affiliation links
            if affiliations is not None:
                affiliation_list = []
                for affiliation in affiliations:
                    if affiliation is not None:
                        affiliation_list.append(extract_text(affiliation, ''))
                if affiliation_list:
                    affiliation_links = ' (' + ','.join(affiliation_list) + ')'
            if fullname:
                if affiliation_links:
                    fullname += affiliation_links
                authors.append(fullname)
    if len(authors) > 0:
        authors = '; '.join(authors)
        authors = ' '.join(authors.split())
    if authors:
        return authors
    return np.NaN


def parse_affiliations(subroot, path):
    """Returns parsed affiliations string from given ET <subroot>"""

    def get_affiliation_list(affiliations):
        """Returns affiliation list of present affiliations"""
        affiliation_list = []
        for affiliation in affiliations:
            if affiliation is not None:
                label = ''
                for element in affiliation.iter():
                    if (element.tag == 'label') or (element.tag == 'sup'):
                        label = '(' + element.text + ')'
                        element.text = ''
                affiliation_string = extract_text(affiliation, '')
                if label:
                    affiliation_string = label + ' ' + affiliation_string
                affiliation_list.append(affiliation_string)
        return affiliation_list

    affiliations = subroot.findall(path)  # Find affiliations in author's location
    if not affiliations:
        affiliations = subroot.findall('aff')  # Find affiliations in meta section
    affiliation_list = get_affiliation_list(affiliations)

    if affiliation_list:
        affiliations_string = ' // '.join(affiliation_list)
        return affiliations_string
    return ''


def parse_keywords(subroot):
    """Returns parsed keywords string from given ET <subroot>"""
    keywords = []
    kwds = subroot.find('kwd-group')
    if kwds is not None:
        for kwd in kwds.iter('kwd'):
            if kwd is not None and kwd.text is not None:
                keywords.append(kwd.text)
    if len(keywords) > 0:
        keywords = '; '.join(keywords)
        return keywords
    return np.NaN


def parse_issue(subroot):
    """Returns parsed journal issue dict from given ET <subroot>"""
    journal_issue = {}
    volume = subroot.find('volume')                            # Volume
    if volume is not None:
        journal_issue['volume'] = volume.text
        
    elocation_id = subroot.find('elocation-id')                # Elocation-id
    if elocation_id is not None:
        journal_issue['elocation-id'] = elocation_id.text
        
    issue = subroot.find('issue')                              # Issue
    if issue is not None:
        journal_issue['issue'] = issue.text
        
    fpage = subroot.find('fpage')                              # Pages
    fpage = fpage.text if fpage is not None else None
    lpage = subroot.find('lpage')
    lpage = lpage.text if lpage is not None else None
    
    if isinstance(fpage, str) and isinstance(lpage, str):
        journal_issue['pages'] = '-'.join([fpage, lpage])
        
    return journal_issue


def parse_journal_meta(subroot, path):
    """Returns parsed journal meta dict from given ET <subroot>"""
    journal_meta = {}
    meta = subroot.find(path)
    if meta is not None:
        journal_ids = meta.findall('journal-id')                                            # Journal ids
        for journal_id in journal_ids:
            journal_meta['journal-id_' + journal_id.attrib.get('journal-id-type')] = journal_id.text
            
        issns = meta.findall('issn')                                                        # ISSNs
        for issn in issns:
            journal_meta['issn_' + issn.attrib.get('pub-type')] = issn.text
        
        journal_title = meta.find('journal-title-group/journal-title')                      # Journal title
        if (journal_title is not None) and (journal_title.text is not None):
            journal_meta['journal_title'] = journal_title.text
            
        publisher = meta.find('publisher')                                                  # Publisher
        if publisher is not None:
            publisher_name = publisher.find('publisher-name')                               # Publisher's name
            if (publisher_name is not None) and (publisher_name.text is not None):
                journal_meta['publisher_name'] = publisher_name.text
                
            publisher_loc = publisher.find('publisher-loc')                                 # Publisher's location
            if (publisher_loc is not None) and (publisher_loc.text is not None):
                journal_meta['publisher_loc'] = publisher_loc.text
    return journal_meta


def extract_text(subroot, path):
    """Returns extracted text between xml tags"""
    text = ''
    if path == '':
        section = subroot
    else:
        section = subroot.find(path)
    if section is not None:
        for element in section.iter():
            if element.text:
                text = text + element.text + ' '
            if element.tail:
                text = text + element.tail + ' '
        text = ' '.join(text.split())
    if text:
        return text
    return ''


def parse_element_tree_pmc(root):
    """Returns parsed dict with all values found"""
    item = {}
    
    item['article-type'] = root.find('article').get('article-type')                             # Article type
    article_meta = root.findall('article/front/article-meta')                                   # Article meta
    for meta in article_meta:
        article_ids = meta.findall('article-id')                                                # Article ids
        for article_id in article_ids:
            item[article_id.get('pub-id-type')] = article_id.text
            
        category = meta.find('article-categories/subj-group/subject')                           # Article category
        if category is not None:
            item['category'] = category.text
            
        item['title'] = extract_text(meta, 'title-group/article-title')                         # Article title
        item['authors'] = parse_authors(meta, 'contrib-group/contrib')                          # Authors
        item['affiliations'] = parse_affiliations(meta, 'contrib-group/aff')                    # Affiliations
        item['pub_date'] = parse_pub_date(meta, 'epub')                                         # Publication date
    
        copyright = meta.find('permissions/copyright-statement')                                # Copyright statement
        if copyright is not None:
            item['copyright'] = copyright.text
        license_type = meta.find('permissions/license')                                         # License type
        if license_type is not None:
            item['license-type'] = license_type.get('license-type')
        item['license'] = extract_text(meta, 'permissions/license/license-p')                   # License text
        
        item['keywords'] = parse_keywords(meta)                                                 # Keywords
        item['abstract'] = extract_text(meta, 'abstract')                                       # Abstract
        item.update(parse_issue(meta))                                                          # Journal issue
    
    item.update(parse_journal_meta(root, 'article/front/journal-meta'))                         # Journal meta
    item['full_text'] = extract_text(root, 'article/body')
    item['abstract_len'] = len(item['abstract']) if item['abstract'] is not np.NaN else 0
    item['full_text_len'] = len(item['full_text']) if item['full_text'] is not np.NaN else 0
            
    return item


def parse_top_level_subroots_pubmed(root):
    """Return top-level subroots and item dict with an article-type from given ET <root>"""
    item = {}
    article_type = 'pubmed_article'
    
    pubmed_data = root.find('PubmedArticle/PubmedData')                                         # Pubmed data subroot
    if pubmed_data is None:
        pubmed_data = root.find('PubmedBookArticle/PubmedBookData')
        
    article_meta = root.find('PubmedArticle/MedlineCitation/Article')                           # Article meta subroot
    if article_meta is None:
        article_meta = root.find('PubmedBookArticle/BookDocument')
        if article_meta is not None:
            article_type = 'book'
        else:
            article_type = 'unknown'
            
    item['article_type'] = article_type                                                         # Article type
    
    return item, pubmed_data, article_meta


def parse_ids_pubmed(subroot):
    """Returns parsed ids dict from given ET <subroot>"""
    ids = {}
    article_ids = subroot.findall('ArticleIdList/ArticleId')                                    # Article ids
    if article_ids is not None:
        for article_id in article_ids:
            if article_id.get('IdType') == 'pubmed':
                ids['pmid'] = article_id.text
            else:
                ids[article_id.get('IdType')] = article_id.text
    return ids


def parse_article_meta_pubmed(subroot):
    """Returns parsed dict with article meta from given ET <subroot>"""
    article_meta_dict = {}
    
    title = subroot.find('ArticleTitle')                                                        # Title
    if title is not None:
        article_meta_dict['title'] = title.text
    
    pages = subroot.find('Pagination/MedlinePgn')                                               # Pagination
    if pages is not None:
        article_meta_dict['pages'] = pages.text
    
    elocation_id = subroot.find('ELocationID')                                                  # Elocation ID
    if elocation_id is not None:
        article_meta_dict['elocation_id'] = elocation_id.text
        
    language = subroot.find('Language')                                                         # Language
    if language is not None:
        article_meta_dict['language'] = language.text
        
    pub_types = subroot.findall('PublicationTypeList/PublicationType')                          # Publication types
    if pub_types is not None:
        pub_types_list = [pub_type.text for pub_type in pub_types if isinstance(pub_type.text, str)]
        if pub_types_list:
            article_meta_dict['publication_type'] = '; '.join(pub_types_list)
    
    return article_meta_dict


def parse_authors_pubmed(subroot):
    """Returns parsed dict with authors found in given ET <subroot>"""
    authors_dict = {}
    authors_list = []
    affiliations_list = []
    
    authors = subroot.findall('AuthorList/Author')                                              # Authors
    if authors is not None:
        for author in authors:
            fullname = ''
            lastname = author.find('LastName')                                                  # Last name
            if (lastname is not None) and (lastname.text is not None):
                fullname += lastname.text
                forename = author.find('ForeName')                                              # First name
                if (forename is not None) and (forename.text is not None):
                    fullname += ' ' + forename.text
            if fullname:
                authors_list.append(fullname)

            affiliation = author.find('AffiliationInfo/Affiliation')                            # Affiliation
            if affiliation is not None:
                affiliation_text = extract_text(affiliation, '')
                if affiliation_text == '':
                    affiliation_text = 'Not defined'
            else:
                affiliation_text = 'Not defined'
            affiliations_list.append(affiliation_text)
    if authors_list:
        authors_dict['authors'] = '; '.join(authors_list)
    if affiliations_list:
        authors_dict['affiliations'] = ' // '.join(affiliations_list)
    
    return authors_dict


def parse_abstract_pubmed(subroot):
    """Returns parsed abstract from given ET <subroot>"""
    abstract_dict = {}
    abstract = ''
    abstract_meta = subroot.findall('Abstract/AbstractText')                                    # Abstract
    if abstract_meta is not None:
        if len(abstract_meta) > 1:
            for i in range(len(abstract_meta)):
                label = abstract_meta[i].get('Label', 'UNNAMED')
                abstract = abstract + label + ': ' + extract_text(abstract_meta[i], '') + ' '
        elif len(abstract_meta) == 1:
            abstract = extract_text(abstract_meta[0], '')
    abstract_dict['abstract'] = abstract
    abstract_dict['abstract_len'] = len(abstract)                                               # Abstract length
    
    copyright = subroot.find('Abstract/CopyrightInformation')                                   # Copyright information
    if (copyright is not None) and (copyright.text is not None):
        abstract_dict['copyright'] = copyright.text
    
    return abstract_dict


def parse_jounal_meta_pubmed(subroot):
    """Returns parsed dict with journal meta from given ET <subroot>"""
    journal_meta_dict = {}
    
    journal_meta = subroot.find('Journal')
    if journal_meta is None:        
        return journal_meta_dict
    
    issns = journal_meta.findall('ISSN')                                                        # ISSNs
    if issns is not None:
        for issn in issns:
            journal_meta_dict['issn_' + issn.attrib.get('IssnType', '').lower()] = issn.text
            
    journal_title = journal_meta.find('Title')                                                  # Journal title
    if (journal_title is not None) and (journal_title.text is not None):
        journal_meta_dict['journal_title'] = journal_title.text
        
    journal_iso_abbr = journal_meta.find('ISOAbbreviation')                                     # Journal ISO abbreviation
    if (journal_iso_abbr is not None) and (journal_iso_abbr.text is not None):
        journal_meta_dict['journal_iso_abbr'] = journal_iso_abbr.text
        
    journal_issue = journal_meta.find('JournalIssue')                                           # Journal issue
    if journal_issue is not None:
        volume = journal_issue.find('Volume')                                                   # Journal volume
        if (volume is not None) and (volume.text is not None):
            journal_meta_dict['volume'] = volume.text
            
        issue = journal_issue.find('Issue')                                                     # Journal issue
        if (issue is not None) and (issue.text is not None):
            journal_meta_dict['issue'] = issue.text
        
        pub_date = journal_issue.find('PubDate')                                                # Journal pub date
        if pub_date is not None:
            medline_date = pub_date.find('MedlineDate')
            if (medline_date is not None) and (medline_date.text is not None):  # Simple case
                journal_meta_dict['pub_date'] = medline_date.text
            else:                                                               # Complex case
                year  = pub_date.find('Year')
                month = pub_date.find('Month')
                day   = pub_date.find('Day')
                date  = ''  + year.text  if (year  is not None) and (year.text  is not None) else ''
                date += '-' + month.text if (month is not None) and (month.text is not None) else ''
                date += '-' + day.text   if (day   is not None) and (day.text   is not None) else ''
                if date:
                    journal_meta_dict['pub_date'] = date
    
    return journal_meta_dict


def parse_publisher_pubmed(root):
    """Returnes parsed dict with publisher information from given ET <root>"""
    publisher_dict = {}
    
    publisher = root.find('PubmedArticle/MedlineCitation/MedlineJournalInfo')
    if publisher is not None:
        name = publisher.find('MedlineTA')                                                     # Publisher name
        if (name is not None) and (name.text is not None):
            publisher_dict['publisher_name'] = name.text
            
        country = publisher.find('Country')                                                    # Publisher country
        if (country is not None) and (country.text is not None):
            publisher_dict['publisher_location'] = country.text
            
        nlm_id = publisher.find('NlmUniqueID')                                                 # Publisher NLM ID
        if (nlm_id is not None) and (nlm_id.text is not None):
            publisher_dict['publisher_nlm_id'] = nlm_id.text
            
        issn_linking = publisher.find('ISSNLinking')                                           # Publisher ISSN Linking
        if (issn_linking is not None) and (issn_linking.text is not None):
            publisher_dict['publisher_issn_linking'] = issn_linking.text
    
    return publisher_dict


def parse_mesh_terms_pubmed(root):
    """Returns parsed dict with all MeSH terms found in ET <root>"""
    mesh_dict = {}
    descriptors = quals_major = quals_minor = []
    
    meshes = root.findall('PubmedArticle/MedlineCitation/MeshHeadingList/MeshHeading')
    if meshes is not None:
        for mesh in meshes:
            descriptor = mesh.find('DescriptorName')                                            # MeSH descriptors
            if (descriptor is not None) and (descriptor.text is not None):
                descriptors.append(descriptor.text)
            
            qualifiers = mesh.findall('QualifierName')                                          # MeSH qualifiers
            if qualifiers is not None:
                for qualifier in qualifiers:
                    if qualifier.text is not None:
                        if qualifier.attrib.get('MajorTopicYN', '') == 'Y':                     # MeSH major qualifiers
                            quals_major.append(qualifier.text)
                        elif qualifier.attrib.get('MajorTopicYN', '') == 'N':                   # MeSH minor qualifiers
                            quals_minor.append(qualifier.text)
    if descriptors:
        mesh_dict['mesh_descriptors'] = '; '.join(set(descriptors))
    if quals_major:
        mesh_dict['mesh_quals_major'] = '; '.join(set(quals_major))
    if quals_minor:
        mesh_dict['mesh_quals_minor'] = '; '.join(set(quals_minor))
        
    keywords = root.findall('PubmedArticle/MedlineCitation/KeywordList/Keyword')                # Keywords
    if keywords is not None:
        keywords_list = [keyword.text for keyword in keywords if keyword.text is not None]
        if keywords_list:
            mesh_dict['keywords'] = '; '.join(keywords_list)
            
    
    return mesh_dict


def parse_element_tree_pubmed(root):
    """Returns parsed dict with all values found"""
    item, pubmed_data, article_meta = parse_top_level_subroots_pubmed(root)                     # Top-level subroots
    item.update(parse_ids_pubmed(pubmed_data))                                                  # Article ids
    item.update(parse_article_meta_pubmed(article_meta))                                        # Article meta-information
    item.update(parse_authors_pubmed(article_meta))                                             # Authors
    item.update(parse_abstract_pubmed(article_meta))                                            # Abstract
    item.update(parse_jounal_meta_pubmed(article_meta))                                         # Journal meta
    item.update(parse_publisher_pubmed(root))                                                   # Publisher information
    item.update(parse_mesh_terms_pubmed(root))                                                  # MeSH terms
    return item


def get_element_tree(filename):
    """Returns parsed ElementTree object of an article stored in <filename>"""
    if not os.path.exists(filename):
        return None
    
    with open(filename, 'r', encoding='utf-8') as f:
        data = f.read()        
    root = ET.fromstring(data)
    
    return root


def get_parsed_item(data, db):
    """Returns parsed article dict"""
    
    root = ET.fromstring(data)
    if db == 'pmc':
        item = parse_element_tree_pmc(root)
    elif db == 'pubmed':
        item = parse_element_tree_pubmed(root)
    return item


def generate_dataset(db, article_ids):
    """Returns articles DataFrame generated from MySQL database"""
    items_list = []
    items = pd.DataFrame(columns=columns[db])

    for i in tqdm.tqdm(range(len(article_ids))):
        result = session.query(PubmedArticle).filter_by(pmid=article_ids[i]).first()
        if result is not None:
            items_list.append(result.to_dict())
        else:
            continue
        if i % 5000 == 0:  # Just cache intermediate result
            items.to_csv('database/tmp.csv', sep='|', index=False)

    items = items.append(items_list)
    return items


def get_article_ids(query, db):
    """Returns all article ids found by <query>"""
    article_ids = []
    params = {
        'db'       : db,
        'api_key'  : api_key,
        'term'     : query,
        'retmax'   : max_results,
        'retstart' : 0,
        'retmode'  : retmode
    }
    count = params['retmax'] + 1
    
    while params['retstart'] < count:
        try:
            response = requests.get(url=url_search, headers=headers, params=params)
        except requests.RequestException:
            print('Problem has occured at retstart: {0}'.format(params['retstart']))
        else:
            root = ET.fromstring(response.text)
            for article_id in root.iter('Id'):
                article_ids.append(int(article_id.text))
            count = int(root.find('Count').text)
        finally:
            params['retstart'] += params['retmax']

    return article_ids


def save_to_database(item):
    """Sends MySQL query and saves <item> to database"""
    try:
        article = PubmedArticle(item)
        session.add(article) 
        session.commit()
    except MySQLdb._exceptions.IntegrityError:
        print('Integrity error, article id: {0}. Error info:\n'.format(article.pmid), sys.exc_info()[1])
        session.rollback()
    except Exception:
        print('MySQL error, article id: {0}. Error info:\n'.format(article.pmid), sys.exc_info()[1])
        session.rollback()
    finally:
        session.close()


def download_article(article_id, db, refresh=False, cache=False):
    """Downloads article query response with <article_id> identifier.
    Does nothing if an article is already in the MySQL database.
    If cache flag set to True then downloaded data will be saved to file too.
    """
    params = {
        'db'      : db,
        'id'      : article_id,
        'api_key' : api_key,
        'retmode' : retmode
    }

    result = session.query(PubmedArticle).filter_by(pmid=article_id).first()
    if (result is None) or (refresh):  # If not present in the database
        filename = os.path.join(db, str(article_id))
        if (os.path.exists(filename)) and (not refresh):  # If file exists, then read it first
            with open(filename, 'r', encoding='utf-8') as f:
                data = f.read() 
        else:                                             # Else send request to pubmed
            try:
                response = requests.get(url=url_fetch, headers=headers, params=params)
            except requests.RequestException:
                print('Problem has occured with {0} ID: {1}'.format(db, article_id))
            else:
                data = response.text
            if cache:
                with open(filename, 'w+', encoding='utf-8') as f:
                    f.write(data)
        item = get_parsed_item(data, db)
        save_to_database(item)
    else:  # Article is already in the database
        pass


def download_all_articles(query, db, refresh=False, cache=False):
    """Downloads all query responses got by <query>"""
    article_ids = get_article_ids(query, db)
    
    article_ids_db = session.query(PubmedArticle.pmid).all()
    article_ids_db = [id[0] for id in article_ids_db]
    session.close()

    intersection = list(set(article_ids) & set(article_ids_db))
    to_download = len(article_ids) - len(intersection)
    print('{0} articles found in {1} with query specified.'.format(len(article_ids), db))
    print('{0} articles are already stored in the database.'.format(len(intersection)))
    print('{0} articles will be downloaded from {1}.'.format(to_download, db))
    
    for i in tqdm.tqdm(range(len(article_ids))):
        download_article(article_ids[i], db, refresh, cache)
    
    article_ids_db = session.query(PubmedArticle.pmid).all()
    session.close()
    print('Total {0} articles stored in the database.'.format(len(article_ids_db)))
    return article_ids
