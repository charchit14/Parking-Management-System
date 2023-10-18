from models import Base
from schema import type_def
from fastapi import FastAPI, Form, HTTPException, Query, Request
from ariadne import ObjectType, make_executable_schema
from ariadne.exceptions import HttpError
from models import Person as PersonModel, Vehicle as VehicleModel, Duration as DurationModel
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from ariadne.asgi import GraphQL
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

query = ObjectType("Query")
mutate = ObjectType("Mutation")

# Mounting Ariadne GraphQL as sub-application for Starlette
app = FastAPI(debug=True)

DATABASE_URL = "postgresql://postgres:pass123@localhost/parking_management_system"
engine = create_engine(DATABASE_URL)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


# Querying data
@query.field("getAllPeople")
def resolve_getAllPeople(*_):
    getAllPerson = session.query(PersonModel)
    return getAllPerson


@query.field("getAllVehicles")
def resolve_getAllVehicles(*_):
    getAllVehicles = session.query(VehicleModel)
    return getAllVehicles


@query.field("getAllDuration")
def resolve_getAllDuration(*_):
    getAllDuration = session.query(DurationModel)
    return getAllDuration


# This has been used to search data
@query.field("getPerson")
def resolve_getPerson(*_, id):
    getPerson = session.query(PersonModel).get(id)
    getVehicle = session.query(VehicleModel).where(VehicleModel.person_id == id).first()
    getDuration = session.query(DurationModel).where(DurationModel.person_id == id).first()
    return {
        "user": getPerson,
        "vehicle": getVehicle,
        "duration": getDuration
    }


@query.field("getVehicle")
def resolve_getVehicle(*_, id):
    getVehicle = session.query(VehicleModel).where(VehicleModel.id == id).first()
    return getVehicle


@query.field("getDuration")
def resolve_getDuration(*_, id):
    getDuration = session.query(DurationModel).where(DurationModel.id == id).first()
    return getDuration


# Mutation for creating new entries
@mutate.field("addEntry")
def resolve_addEntry(*_, person_name, visitor_type, vehicle_type, vehicle_number, stay_duration):

    vehicle = session.query(VehicleModel).where(VehicleModel.vehicle_number==vehicle_number).first()
    if vehicle:
        return False

    dataperson = PersonModel(person_name, visitor_type)
    session.add(dataperson)
    session.flush()

    datavehicle = VehicleModel(vehicle_type, vehicle_number, dataperson.id)
    session.add(datavehicle)
    session.flush()

    dataduration = DurationModel(stay_duration, dataperson.id, datavehicle.id)
    session.add(dataduration)
    session.commit()
    return True


@mutate.field("createPerson")
def resolve_createPerson(*_, person_name, visitor_type):
    data = PersonModel(person_name, visitor_type)
    session.add(data)
    session.commit()
    return data


@mutate.field("createVehicle")
def resolve_createVehicle(*_, vehicle_type, vehicle_number, person_id):
    data = VehicleModel(vehicle_type, vehicle_number, person_id)
    session.add(data)
    session.commit()
    return data


@mutate.field("createDuration")
def resolve_createDuration(*_, stay_duration, person_id, vehicle_id):
    data = DurationModel(stay_duration, person_id, vehicle_id)
    session.add(data)
    session.commit()
    return data


# Mutation for updating entry
@mutate.field("updateEntry")
def resolve_updateEntry(*_, id, updates):

    # Person
    persondata = session.query(PersonModel).filter(PersonModel.id == id)

    if persondata:
        if "person_name" in updates:
            persondata.update({PersonModel.person_name: updates["person_name"]})

        if "visitor_type" in updates:
            persondata.update({PersonModel.visitor_type: updates["visitor_type"]})

    # Vehicle
    vehicledata = session.query(VehicleModel).filter(VehicleModel.person_id == id)

    if vehicledata:
        if "vehicle_type" in updates:
            vehicledata.update({VehicleModel.vehicle_type: updates["vehicle_type"]})

        if "vehicle_number" in updates:
            vehicledata.update({VehicleModel.vehicle_number: updates["vehicle_number"]})

    # Duration
    durationdata = session.query(DurationModel).filter(DurationModel.person_id == id)

    if durationdata:
        if "stay_duration" in updates:
            durationdata.update({DurationModel.stay_duration: updates["stay_duration"]})

    session.commit()
    return True


@mutate.field("updatePerson")
def resolve_updatePerson(*_, id, updates):
    data = session.query(PersonModel).where(PersonModel.id == id)

    if "person_name" in updates:
        data.update({PersonModel.person_name: updates["person_name"]})


    if "visitor_type" in updates:
        data.update({PersonModel.visitor_type: updates["visitor_type"]})

    session.commit()
    return data.first()


@mutate.field("updateVehicle")
def resolve_updateVehicle(*_id, updates):
    data = session.query(VehicleModel).where(VehicleModel.id == id)

    if "vehicle_type" in updates:
        data.update({VehicleModel.vehicle_type: updates["vehicle_type"]})

    if "vehicle_number" in updates:
        data.update({PersonModel.vehicle_number: updates["vehicle_number"]})

    session.commit()
    return data.first()


@mutate.field("updateDuration")
def resolve_updateDuration(*_id, updates):
    data = session.query(DurationModel).where(DurationModel.id == id)

    if "stay_duration" in updates:
        data.update({PersonModel.stay_duration: updates["stay_duration"]})

    session.commit()
    return data.first()


# Mutation for deleting an entry
@mutate.field("deletePerson")
def resolve_deletePerson(*_, id):
    # Fetch the Person record to be deleted
    person = session.query(PersonModel).filter_by(id=id).first()

    if person:

        try:
            # Fetch related Vehicle records
            vehicles = session.query(VehicleModel).filter_by(person_id=id).all()

            # Fetch related Duration records
            durations = session.query(DurationModel).filter_by(person_id=id).all()

            # Delete related Vehicle records
            for vehicle in vehicles:
                vehicle.person_id = None  # Set the person_id to None
                session.delete(vehicle)

            # Delete related Duration records
            for duration in durations:
                session.delete(duration)

            # Delete the Person record
            session.delete(person)
            session.commit()
            return person

        except Exception as e:
            session.rollback()
            return {"error": str(e)}


# Create executable schema instance
schema = make_executable_schema(type_def, query, mutate)

app.mount("/graphql/", GraphQL(schema, debug=True))

app.mount("/static", StaticFiles(directory="static"), name="static")
