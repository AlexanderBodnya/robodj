import sqlite3
from helpers.log_helper import add_logger, exception
from sqlalchemy import Column, String, ForeignKey, Integer, Index, Float, or_, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


logger = add_logger(__name__)


base = declarative_base()


class VoteLog(base):
    __tablename__ = 'vote_log'

    vote_id = Column(String, nullable=False)
    song_name = Column(String, nullable=False)
    voter_name = Column(String, nullable=False)
    __table_args__ = (
        Index('ix_vote_id', vote_id),
    )


string_to_class = {
    'VoteLog': VoteLog
}

class SQLOperations():

    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    @exception(logger)
    def destroy_session(self):
        self.session.close()

    @exception(logger)
    def add_data(self, tablename, **kwargs):
        __data__ = string_to_class[tablename](**kwargs)
        self.session.merge(__data__)
        self.session.commit()

    @exception(logger)
    def create_database(self):
        base.metadata.create_all(bind=self.engine)

    @exception(logger)
    def drop_database(self):
        base.metadata.reflect(bind=self.engine)
        base.metadata.drop_all(bind=self.engine)

 
