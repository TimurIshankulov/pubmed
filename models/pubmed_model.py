import os, sys, inspect
from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from config import conn_string

Base = declarative_base()

class PubmedArticle(Base):

    def __init__(self, values):
        self.pmid               = values.get('pmid')
        self.pmc                = values.get('pmc')
        self.pii                = values.get('pii')
        self.mid                = values.get('mid')
        self.doi                = values.get('doi')
        self.elocation_id       = values.get('elocation_id')
        self.language           = values.get('language')
        self.title              = values.get('title')
        self.authors            = values.get('authors')
        self.affiliations       = values.get('affiliations')
        self.article_type       = values.get('article_type')
        self.publication_type   = values.get('publication_type')
        self.journal_title      = values.get('journal_title')
        self.volume             = values.get('volume')
        self.issue              = values.get('issue')
        self.pages              = values.get('pages')
        self.pub_date           = values.get('pub_date')
        self.issn_electronic    = values.get('issn_electronic')
        self.issn_print         = values.get('issn_print')
        self.journal_iso_abbr   = values.get('journal_iso_abbr')
        self.publisher_name     = values.get('publisher_name')
        self.publisher_location = values.get('publisher_location')
        self.publisher_nlm_id   = values.get('publisher_nlm_id')
        self.publisher_issn_linking = values.get('publisher_issn_linking')
        self.abstract_len       = values.get('abstract_len')
        self.abstract           = values.get('abstract')
        self.copyright          = values.get('copyright')
        self.mesh_quals_major   = values.get('mesh_quals_major')
        self.mesh_quals_minor   = values.get('mesh_quals_minor')
        self.mesh_descriptors   = values.get('mesh_descriptors')
        self.keywords           = values.get('keywords')

    
    def __str__(self):
        return '[{self.pmid}] Title: {self.title}'.format(self=self)

    
    def to_dict(self):
        article_dict = {}
        article_dict['pmid']               = self.pmid
        article_dict['pmc']                = self.pmc
        article_dict['pii']                = self.pii
        article_dict['mid']                = self.mid
        article_dict['doi']                = self.doi
        article_dict['elocation_id']       = self.elocation_id
        article_dict['language']           = self.language
        article_dict['title']              = self.title
        article_dict['authors']            = self.authors
        article_dict['affiliations']       = self.affiliations
        article_dict['article_type']       = self.article_type
        article_dict['publication_type']   = self.publication_type
        article_dict['journal_title']      = self.journal_title
        article_dict['volume']             = self.volume
        article_dict['issue']              = self.issue
        article_dict['pages']              = self.pages
        article_dict['pub_date']           = self.pub_date
        article_dict['issn_electronic']    = self.issn_electronic
        article_dict['issn_print']         = self.issn_print
        article_dict['journal_iso_abbr']   = self.journal_iso_abbr
        article_dict['publisher_name']     = self.publisher_name
        article_dict['publisher_location'] = self.publisher_location
        article_dict['publisher_nlm_id']   = self.publisher_nlm_id
        article_dict['publisher_issn_linking'] = self.publisher_issn_linking
        article_dict['abstract_len']       = self.abstract_len
        article_dict['abstract']           = self.abstract
        article_dict['copyright']          = self.copyright
        article_dict['mesh_quals_major']   = self.mesh_quals_major
        article_dict['mesh_quals_minor']   = self.mesh_quals_minor
        article_dict['mesh_descriptors']   = self.mesh_descriptors
        article_dict['keywords']           = self.keywords
        return article_dict

    #====== Table options ======#

    __tablename__ = 'pubmed'

    pmid               = Column(Integer(), primary_key=True, nullable=False)
    pmc                = Column(String(50))
    pii                = Column(Text())
    mid                = Column(String(50))
    doi                = Column(String(150))
    elocation_id       = Column(String(150))
    language           = Column(String(20))
    title              = Column(Text())
    authors            = Column(Text())
    affiliations       = Column(MEDIUMTEXT())
    article_type       = Column(String(30))
    publication_type   = Column(Text())
    journal_title      = Column(Text())
    volume             = Column(String(100))
    issue              = Column(String(100))
    pages              = Column(String(150))
    pub_date           = Column(String(100))
    issn_electronic    = Column(String(30))
    issn_print         = Column(String(30))
    journal_iso_abbr   = Column(String(150))
    publisher_name     = Column(String(150))
    publisher_location = Column(String(100))
    publisher_nlm_id   = Column(String(30))
    publisher_issn_linking = Column(String(30))
    abstract_len       = Column(Integer())
    abstract           = Column(MEDIUMTEXT())
    copyright          = Column(Text())
    mesh_quals_major   = Column(Text())
    mesh_quals_minor   = Column(Text())
    mesh_descriptors   = Column(Text())
    keywords           = Column(Text())


class PMCArticle(Base):

    def __init__(self, values):
        self.pmid           = values.get('pmid')
        self.pmc            = values.get('pmc')
        self.pii            = values.get('pii')
        self.doi            = values.get('doi')
        self.art_access_id  = values.get('art-access-id')
        self.sici           = values.get('sici')
        self.pmc_scan       = values.get('pmc-scan')
        self.medline        = values.get('medline')
        self.manuscript     = values.get('manuscript')
        self.other          = values.get('other')
        self.title          = values.get('title')
        self.authors        = values.get('authors')
        self.affiliations   = values.get('affiliations')
        self.article_type   = values.get('article-type')
        self.category       = values.get('category')
        self.journal_title  = values.get('journal_title')
        self.volume         = values.get('volume')
        self.issue          = values.get('issue')
        self.pages          = values.get('pages')
        self.pub_date       = values.get('pub_date')
        self.issn_epub      = values.get('issn_epub')
        self.issn_ppub      = values.get('issn_ppub')
        self.publisher_name = values.get('publisher_name')
        self.publisher_loc  = values.get('publisher_loc')
        self.publisher_id   = values.get('publisher-id')
        self.elocation_id   = values.get('elocation-id')
        self.publisher_manuscript      = values.get('publisher-manuscript')
        self.journal_id_nlm_ta         = values.get('journal-id_nlm-ta')
        self.journal_id_pubmed_jr_id   = values.get('journal-id_pubmed-jr-id')
        self.journal_id_issn           = values.get('journal-id_issn')
        self.journal_id_pmc            = values.get('journal-id_pmc')
        self.journal_id_doi            = values.get('journal-id_doi')
        self.journal_id_coden          = values.get('journal-id_coden')
        self.journal_id_publisher_id   = values.get('journal-id_publisher-id')
        self.journal_id_hwp            = values.get('journal-id_hwp')
        self.journal_id_nlm_journal_id = values.get('journal-id_nlm-journal-id')
        self.journal_id_iso_abbrev     = values.get('journal-id_iso-abbrev')
        self.abstract_len   = values.get('abstract_len')
        self.abstract       = values.get('abstract')
        self.full_text_len  = values.get('full_text_len')
        self.full_text      = values.get('full_text')
        self.license_type   = values.get('license-type')
        self.license        = values.get('license')
        self.copyright      = values.get('copyright')
        self.keywords       = values.get('keywords')

    
    def __str__(self):
        return '[{self.pmid}] Title: {self.title}'.format(self=self)

    
    def to_dict(self):
        article_dict = {}
        article_dict['pmid']           = self.pmid
        article_dict['pmc']            = self.pmc
        article_dict['pii']            = self.pii
        article_dict['doi']            = self.doi
        article_dict['art-access-id']  = self.art_access_id
        article_dict['sici']           = self.sici
        article_dict['pmc-scan']       = self.pmc_scan
        article_dict['medline']        = self.medline
        article_dict['manuscript']     = self.manuscript
        article_dict['other']          = self.other
        article_dict['title']          = self.title
        article_dict['authors']        = self.authors
        article_dict['affiliations']   = self.affiliations
        article_dict['article-type']   = self.article_type
        article_dict['category']       = self.category
        article_dict['journal_title']  = self.journal_title
        article_dict['volume']         = self.volume
        article_dict['issue']          = self.issue
        article_dict['pages']          = self.pages
        article_dict['pub_date']       = self.pub_date
        article_dict['issn_epub']      = self.issn_epub
        article_dict['issn_ppub']      = self.issn_ppub
        article_dict['publisher_name'] = self.publisher_name
        article_dict['publisher_loc']  = self.publisher_loc
        article_dict['publisher-id']   = self.publisher_id
        article_dict['elocation-id']   = self.elocation_id
        article_dict['publisher-manuscript']      = self.publisher_manuscript
        article_dict['journal-id_nlm-ta']         = self.journal_id_nlm_ta  
        article_dict['journal-id_pubmed-jr-id']   = self.journal_id_pubmed_jr_id
        article_dict['journal-id_issn']           = self.journal_id_issn
        article_dict['journal-id_pmc']            = self.journal_id_pmc
        article_dict['journal-id_doi']            = self.journal_id_doi
        article_dict['journal-id_coden']          = self.journal_id_coden
        article_dict['journal-id_publisher-id']   = self.journal_id_publisher_id
        article_dict['journal-id_hwp']            = self.journal_id_hwp
        article_dict['journal-id_nlm-journal-id'] = self.journal_id_nlm_journal_id
        article_dict['journal-id_iso-abbrev']     = self.journal_id_iso_abbrev
        article_dict['abstract_len']   = self.abstract_len
        article_dict['abstract']       = self.abstract
        article_dict['full_text_len']  = self.full_text_len
        article_dict['full_text']      = self.full_text
        article_dict['license-type']   = self.license_type
        article_dict['license']        = self.license
        article_dict['copyright']      = self.copyright
        article_dict['keywords']       = self.keywords
        return article_dict

    #====== Table options ======#

    __tablename__ = 'pmc'

    pmid           = Column(Integer())
    pmc            = Column(Integer(), primary_key=True, nullable=False)
    pii            = Column(Text())
    doi            = Column(String(150))
    art_access_id  = Column(String(50))
    sici           = Column(String(100))
    pmc_scan       = Column(String(100))
    medline        = Column(String(50))
    manuscript     = Column(String(50))
    other          = Column(String(100))
    title          = Column(Text())
    authors        = Column(Text())
    affiliations   = Column(Text())
    article_type   = Column(String(50))
    category       = Column(Text())
    journal_title  = Column(Text())
    volume         = Column(String(100))
    issue          = Column(String(60))
    pages          = Column(String(100))
    pub_date       = Column(String(100))
    issn_epub      = Column(String(30))
    issn_ppub      = Column(String(30))
    publisher_name = Column(Text())
    publisher_loc  = Column(Text())
    publisher_id   = Column(String(150))
    elocation_id   = Column(Text())
    publisher_manuscript      = Column(String(100))
    journal_id_nlm_ta         = Column(String(200))
    journal_id_pubmed_jr_id   = Column(String(30))
    journal_id_issn           = Column(String(30))
    journal_id_pmc            = Column(String(150))
    journal_id_doi            = Column(String(150))
    journal_id_coden          = Column(String(50))
    journal_id_publisher_id   = Column(String(150))
    journal_id_hwp            = Column(String(150))
    journal_id_nlm_journal_id = Column(String(30))
    journal_id_iso_abbrev     = Column(String(200))
    abstract_len   = Column(Integer())
    abstract       = Column(MEDIUMTEXT())
    full_text_len  = Column(Integer())
    full_text      = Column(MEDIUMTEXT())
    license_type   = Column(String(150))
    license        = Column(Text())
    copyright      = Column(Text())
    keywords       = Column(Text())


engine = create_engine(conn_string)
Base.metadata.create_all(engine)