from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId

app = FastAPI()

# Connect to MongoDB Atlas
client = MongoClient("mongodb://localhost:27017")
db = client["library_management"]
students_collection = db["students"]

class Address(BaseModel):
    city: str
    country: str

class Student(BaseModel):
    name: str
    age: int
    address: Address

@app.post("/students", status_code=201)
async def create_student(student: Student):
    result = students_collection.insert_one(student.dict())
    return {"id": str(result.inserted_id)}

@app.get("/students", response_model=list[Student])
async def list_students(country: str = None, age: int = None):
    query = {}
    if country:
        query["address.country"] = country
    if age:
        query["age"] = {"$gte": age}
    students = list(students_collection.find(query, {"_id": 0}))
    return students

@app.get("/students/{id}", response_model=Student)
async def get_student(id: str):
    student = students_collection.find_one({"_id": ObjectId(id)}, {"_id": 0})
    if student:
        return student
    else:
        raise HTTPException(status_code=404, detail="Student not found")

@app.patch("/students/{id}", status_code=204)
async def update_student(id: str, student: Student):
    updated_student = student.dict(exclude_unset=True)
    result = students_collection.update_one({"_id": ObjectId(id)}, {"$set": updated_student})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    else:
        return

@app.delete("/students/{id}", status_code=200)
async def delete_student(id: str):
    result = students_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    else:
        return {"message": "Student deleted successfully"}
