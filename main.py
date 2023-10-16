from models import Base
from schema import type_def
from fastapi import FastAPI, Form, HTTPException, Query, Request
from ariadne import ObjectType, make_executable_schema
from models import Person as PersonModel, Vehicle as VehicleModel, Duration as DurationModel
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from ariadne.asgi import GraphQL
from fastapi.staticfiles import StaticFiles


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


@query.field("getPerson")
def resolve_getPerson(*_, id):
    getPerson = session.query(PersonModel).where(PersonModel.id == id).first()
    return getPerson


@query.field("getVehicle")
def resolve_getVehicle(*_, id):
    getVehicle = session.query(VehicleModel).where(VehicleModel.id == id).first()
    return getVehicle


@query.field("getDuration")
def resolve_getDuration(*_, id):
    getDuration = session.query(DurationModel).where(DurationModel.id == id).first()
    return getDuration


# Mutation for creating new entries
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
        # Fetch related Vehicle records
        vehicles = session.query(VehicleModel).filter_by(person_id=id).all()

        # Fetch related Duration records
        durations = session.query(DurationModel).filter_by(person_id=id).all()

        # Delete related Vehicle records
        for vehicle in vehicles:
            session.delete(vehicle)

        # Delete related Duration records
        for duration in durations:
            session.delete(duration)

        # Delete the Person record
        session.delete(person)
        session.commit()
        return person


# Defining route to handle form submission
@app.post("/submit-entry")
async def submit_entry(
        full_name: str = Form(...),
        visitor_type: str = Form(...),
        vehicle_type: str = Form(...),
        stay_duration: str = Form(...),
        vehicle_number: str = Form(...)
):
    # Check if a vehicle with the same number already exists
    existing_vehicle = session.query(VehicleModel).filter_by(vehicle_number=vehicle_number).first()

    if existing_vehicle:
        # If the vehicle exists, return an error message
        raise HTTPException(status_code=400, detail="Can't create an entry. Vehicle with this number already exists.")

    # Creating and inserting data into the database
    new_person = PersonModel(person_name=full_name, visitor_type=visitor_type)
    session.add(new_person)
    session.commit()

    # Get the ID of the newly created person
    person_id = new_person.id

    # Create a new vehicle
    new_vehicle = VehicleModel(vehicle_type=vehicle_type, vehicle_number=vehicle_number, person_id=person_id)
    session.add(new_vehicle)
    session.commit()

    # Get the ID of the newly created vehicle
    vehicle_id = new_vehicle.id

    # Create the duration record with both person_id and vehicle_id
    new_duration = DurationModel(stay_duration=stay_duration, person_id=person_id, vehicle_id=vehicle_id)
    session.add(new_duration)

    # Commit the duration record to the database
    session.commit()

    return {"message": "Successfully added an entry"}


@app.get("/search-person")
async def search_person(person_id: int = Query(...)):
    # Query the person by ID
    person = session.query(PersonModel).filter_by(id=person_id).first()

    if person:
        # Query the related vehicle by person_id
        vehicle = session.query(VehicleModel).filter_by(person_id=person_id).first()

        # Query the related duration by person_id
        duration = session.query(DurationModel).filter_by(person_id=person_id).first()

        if vehicle and duration:
            # Return the data as JSON
            return {
                "person_id": person.id,
                "person_name": person.person_name,
                "visitor_type": person.visitor_type,
                "vehicle_id": vehicle.id,
                "vehicle_type": vehicle.vehicle_type,
                "vehicle_number": vehicle.vehicle_number,
                "duration_id": duration.id,
                "stay_duration": duration.stay_duration,
            }
        else:
            raise HTTPException(status_code=404, detail="Vehicle or Duration data not found for the person.")
    else:
        raise HTTPException(status_code=404, detail="Person with entered ID does not exist")


@app.delete("/delete-person")
async def delete_person(person_id: int = Query(...)):

    # Fetching the Person record to be deleted
    person = session.query(PersonModel).filter_by(id=person_id).first()

    if person:

        try:
            # Fetching the related Vehicle record
            vehicles = session.query(VehicleModel).filter_by(person_id=person_id).all()

            # Fetching the related Duration record
            durations = session.query(DurationModel).filter_by(person_id=person_id).all()

            # Deleting the Vehicle record
            for vehicle in vehicles:
                vehicle.person_id = None  # Set the person_id to None
                session.delete(vehicle)

            # Deleting the Duration record
            for duration in durations:
                session.delete(duration)

            # Deleting the Person record
            session.delete(person)
            session.commit()
            return {"message": "Person entry deleted successfully."}

        except Exception as e:
            session.rollback()
            return {"error": str(e)}

    else:
        raise HTTPException(status_code=404, detail="Person with entered ID does not exist")


# Create executable schema instance
schema = make_executable_schema(type_def, query, mutate)

app.mount("/graphql/", GraphQL(schema, debug=True))

app.mount("/static", StaticFiles(directory="static"), name="static")
