"""
This defines SQLAlchemy models for two database tables: Person and Vehicle.
SQLAlchemy is an Object-Relational Mapping (ORM) library for Python that simplifies database interaction
by allowing you to work with databases using Python classes and objects instead of writing raw SQL queries.
"""

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

"""
declarative_base() is a function provided by SQLAlchemy that creates a base class for all your database models. 
It's a common practice to define this base class to share common configuration among your models
"""

Base = declarative_base()


class Person(Base):
    __tablename__ = 'person'

    id = Column(Integer, primary_key=True)
    person_name = Column(String, nullable=False)
    visitor_type = Column(String, nullable=False)

    # Defining relationship with Vehicle and Duration
    vehicle = relationship('Vehicle')
    duration = relationship('Duration')

    '''__init__ method is added to the 'Person' class so that it accepts the 
    attributes of a person as keyword arguments and sets them as instance attributes.
    This allows us to create a new Person object by passing these arguments during initialization'''

    def __init__(self, person_name, visitor_type):
        self.person_name = person_name
        self.visitor_type = visitor_type


class Vehicle(Base):
    __tablename__ = 'vehicle'

    id = Column(Integer, primary_key=True)
    vehicle_type = Column(String, nullable=False)
    vehicle_number = Column(String, nullable=False, unique=True)
    person_id = Column(Integer, ForeignKey('person.id'), nullable=False)

    # Defining relationship with Person and Duration
    person = relationship('Person')
    duration = relationship('Duration')

    def __init__(self, vehicle_type, vehicle_number, person_id):
        self.vehicle_type = vehicle_type
        self.vehicle_number = vehicle_number
        self.person_id = person_id


class Duration(Base):
    __tablename__ = 'duration'

    id = Column(Integer, primary_key=True)
    stay_duration = Column(String, nullable=False)
    person_id = Column(Integer, ForeignKey('person.id'), nullable=False)
    vehicle_id = Column(Integer, ForeignKey('vehicle.id'), nullable=False)

    # Defining relationship with Person and Vehicle
    person = relationship('Person')
    vehicle = relationship('Vehicle')

    def __init__(self, stay_duration, person_id, vehicle_id):
        self.stay_duration = stay_duration
        self.person_id = person_id
        self.vehicle_id = vehicle_id


"""
The 'relationship' attribute is used to define the relationship between the 'Vehicle' and 'Person' models.
It specifies that there is a bidirectional relationship between them.
This allows you to access a person's vehicles through the person attribute of the Vehicle model and vice versa.
"""
