import sqlite3
from helpers.log_helper import add_logger, exception
from sqlalchemy import Column, String, ForeignKey, Integer, Index, Float, or_, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


logger = add_logger(__name__)


base = declarative_base()

class SongsList(base):
    __tablename__ = 'songs_list'

    song_id = Column(Integer, nullable=False, primary_key=True)
    song_name = Column(String, nullable=False)


class VoteLog(base):
    __tablename__ = 'vote_log'

    vote_id = Column(String, nullable=False, primary_key=True)
    song_name = Column(String, ForeignKey('songs_list.song_name'), nullable=False)
    voter_id = Column(String, nullable=False)
    __table_args__ = (
        Index('ix_vote_id', vote_id),
    )


string_to_class = {
    'VoteLog': VoteLog,
    'SongsList': SongsList
}

class SQLOperations():

    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        base.metadata.create_all(bind=self.engine)

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

    @exception(logger)
    def get_list(self):
        resp = self.session.execute('SELECT song_id, vote_log.song_name, COUNT(*) FROM vote_log LEFT JOIN songs_list ON vote_log.song_name = songs_list.song_name GROUP BY vote_log.song_name ORDER BY song_id').fetchall()
        return resp

    @exception(logger)
    def get_song_name_by_id(self, song_id):
        resp = self.session.execute('SELECT song_name FROM songs_list where song_id = {}'.format(song_id)).fetchone()
        return resp

    @exception(logger)
    def recant_vote(self, vote_id):
        self.session.execute("delete FROM vote_log where vote_id = '{}'".format(vote_id))
        self.session.commit()
        return None

 
