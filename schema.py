# Schemas for my database
# Here, I define my database type what type of operations can be performed on it

type_def = """

    type Person {
        id: Int!
        person_name: String!
        visitor_type: String!
    }

    type Vehicle {
        id: Int!
        vehicle_type: String!
        vehicle_number: String! 
        person_id: Int!
    }

    type Duration {
        id: Int!
        stay_duration: String!
        person_id: Int!
        vehicle_id: Int!
    }
    
    type UserInfo {
        user: Person
        vehicle: Vehicle
        duration: Duration
    }
    
    type Query {
        getPerson(id: Int!): UserInfo
        getVehicle(id: Int!): Vehicle
        getDuration(id: Int!): Duration
        getAllPeople: [Person!]!
        getAllVehicles: [Vehicle!]!
        getAllDuration: [Duration!]!
    }

    type Mutation {
        
        addEntry(
            person_name: String!
            visitor_type: String!
            vehicle_type: String!
            vehicle_number: String!
            stay_duration: String!
    ) : Boolean
        
        createPerson(
            person_name: String!
            visitor_type: String!
        ): Person

        createVehicle(
            vehicle_type: String!
            vehicle_number: String!
            person_id: Int!
        ): Vehicle

        createDuration(
            stay_duration: String!
            person_id: Int!
            vehicle_id: Int!
        ): Duration
        
        updateEntry(
        id: Int!, updates: UpdateEntry!
        ): Boolean
        
        updatePerson(        
        id: Int!, updates: UpdatePerson!
        ): Person

        updateVehicle(
        id: Int!, updates: UpdateVehicle!
        ): Vehicle

        updateDuration(
        id: Int!, updates: UpdateDuration!
        ): Duration

        deletePerson(id: Int!): Person
    } 

    input UpdatePerson{
        person_name: String
        visitor_type: String
    }

    input UpdateVehicle{
        vehicle_type: String
        vehicle_number: String
    }

    input UpdateDuration{
        stay_duration: String
    }
    
    input UpdateEntry{
        person_name: String
        visitor_type: String
        vehicle_type: String
        vehicle_number: String
        stay_duration: String
    }
    
"""

#  : Person indicates the return type of the mutation.
# Meaning after the mutation is executed, it will return a Person object representing the updated state of the person
