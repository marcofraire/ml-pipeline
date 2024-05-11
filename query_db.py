import pandas as pd
from sqlalchemy import create_engine
from abc import ABC, abstractmethod  


class Query:

    def __init__(self, db_details: dict):
        self.user = db_details['USER']
        self.password = db_details['PASSWORD']
        self.host = db_details['HOST']
        self.port = db_details['PORT']
        self.name = db_details['NAME']

    @property
    def engine(self):
        return create_engine(
            f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}")

    @abstractmethod
    def compose_query(self):
        pass

    def query_db(self):
        df = pd.read_sql(self.compose_query(), self.engine)
        return df


class QueryMLBooks(Query):

    def __init__(self, db_details: dict, edition_id: str):
        super().__init__(db_details)
        self.edition_id = edition_id

    def compose_query(self):
        return f"SELECT * FROM bbourse.ml_books WHERE 1=1 and edition_id = {self.edition_id}"

class QueryEbaySalesLinks(Query):

    def __init__(self, db_details: dict, edition_id: str):
        super().__init__(db_details)
        self.edition_id = edition_id

    def compose_query(self):
        return f"SELECT img_id as img_id_db  FROM bbourse.ebay_sales WHERE 1=1 and edition_id = {self.edition_id}"

class QueryEbayListings(Query):

    def __init__(self, db_details: dict, edition_id: str):
        super().__init__(db_details)
        self.edition_id = edition_id

    def compose_query(self):
        return f"SELECT * FROM bbourse.ebay_listings WHERE 1=1 and edition_id = {self.edition_id}"
    
class QueryBookEditionNoFeature(Query):
    def compose_query(self):
        return """SELECT 
                    edition_id
                    ,(edition_details::json) ->>'image' as image_link 
                FROM bbourse.book_editions 
                WHERE 1=1 
                    and edition_id NOT IN (SELECT edition_id from bbourse.image_features)"""
    
class QueryAllEditionImageLinks(Query):
    def compose_query(self):
        return """select (edition_details::json) ->>'image' as image_link  from bbourse.book_editions be """
    
class QueryImageFeatures(Query):
    def compose_query(self):
        return """select * from bbourse.image_features """
    
class QueryListingsMissingEdition(Query):
    def compose_query(self):
        return """select img_id, img_link, title from bbourse.book_listings where edition_id is null """