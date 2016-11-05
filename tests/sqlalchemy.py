"""Base SQLAlchemy test case module."""
from datetime import datetime

from sqlalchemy import create_engine, event, ForeignKey
from sqlalchemy import Column, Date, DateTime, Enum, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from unittest import TestCase


Base = declarative_base()


class Category(Base):
    """Mock category table."""

    __tablename__ = "category"

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('category.id'))
    name = Column(String)

    category = relationship(
        'Category', backref='categories', remote_side=[id], uselist=False)


class Product(Base):
    """Mock product table."""

    __tablename__ = "product"

    id = Column(Integer, primary_key=True)
    primary_category_id = Column(Integer, ForeignKey('category.id'))
    secondary_category_id = Column(Integer, ForeignKey('category.id'))
    name = Column(String)

    primary_category = relationship(
        'Category', backref='primary_products',
        foreign_keys=[primary_category_id])
    secondary_category = relationship(
        'Category', backref='secondary_products',
        foreign_keys=[secondary_category_id])


class Person(Base):
    """Mock person table."""

    __tablename__ = "person"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    birth_date = Column(Date)
    status = Column(Enum('active', 'inactive'), default='inactive')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Student(Base):
    """Mock 'through' table for `School` and `Person` models."""

    __tablename__ = "student"

    id = Column(Integer, primary_key=True)
    school_id = Column(Integer, ForeignKey('school.id'))
    person_id = Column(Integer, ForeignKey('person.id'))

    school = relationship('School', backref='student')
    person = relationship('Person', backref='student')


class School(Base):
    """Mock school table."""

    __tablename__ = "school"

    id = Column(Integer, primary_key=True)
    name = Column(String)


class BaseSQLAlchemyTestCase(TestCase):
    """Base SQLAlchemy test case.

    For each unittest class, create a database, start a session, run
    the tests, rollback the session after each test, and finally drop
    the database once all tests have completed.
    """

    def setUp(self):
        """Create a save point and start the session."""
        self.engine = engine
        self.session = sessionmaker(bind=engine)()
        self.session.begin_nested()

    def tearDown(self):
        """Close the session and rollback to the previous save point."""
        self.session.rollback()
        self.session.close()

    @classmethod
    def setUpClass(cls):
        """Create the database."""
        global engine

        engine = create_engine('sqlite:///sqlalchemy.db')

        @event.listens_for(engine, "connect")
        def do_connect(dbapi_connection, connection_record):
            dbapi_connection.isolation_level = None

        @event.listens_for(engine, "begin")
        def do_begin(conn):
            conn.execute("BEGIN")

        Base.metadata.create_all(engine)

    @classmethod
    def tearDownClass(cls):
        """Destroy the database."""
        engine.dispose()
