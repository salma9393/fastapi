
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = None
    origin: str

# In-memory store for items
items_db = {1:"hello",2:"python"}



class Student():
    name: str
    age: int
    grade: str

@app.get("/students/")
def get_all_students():
    return [{"name": "Dheeraj23", "age": 20, "grade": "A++"}, {"name": "Sashi", "age": 22, "grade": "B++"}]   

#Homework to add post method to add student and simulate without pydantic class
@app.post("/items")
def func(item: Student):
     return {"StudentOBJ"}


@app.get("/items/")
def get_all_items():
    return list(items_db.values())

@app.post("/items/")
def create_item(item: Item):
    items_db[item.name] = item
    return item

@app.get("/items/{name}")
def get_item(name: str):
    result = items_db.get(name)
    if result:
        return result
    return {"error": "Item not found"}

@app.put("/items/{name}")
def update_item(name: str, item: Item):
    items_db[name] = item
    return item

#Homework Add delete method for items
@app.delete("/items/")
def delete_item(name: str):
    if name in items_db:
        del items_db[name]
        return {"message": f"Item '{name}' deleted successfully"}
    return {"error": "Item not found"}


#Homework add docs for all methods
from typing import list
@app.get("/items/",response_model=list[Student])
def get_all_items():
    return list(items_db.values())


#Homework  add pytdantic for student class and add post method to add student to list and get method to get all students
student_db={}
class student(BaseModel):
    name: str
    age: int
    grade: str

@app.post("/students/")
def add_student(student: student):
    items_db[student.student_id]=student
    return {"message": "Student added successfully", "student": student}

@app.get("/students/",response_model=list[student])
def get_students():
    return {"students data successfully executed"}
