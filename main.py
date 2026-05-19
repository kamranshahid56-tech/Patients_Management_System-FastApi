from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
import json

app = FastAPI()

# Define the Patient model using Pydantic for data validation and serialization and documentation
# This model is used to add data to the JSON file.
class Patient(BaseModel):

    id: Annotated[str, Field(..., description="ID of the patient", examples=["P001"])]
    name: Annotated[str, Field(..., description="Name of the patient", examples=["John Doe"])]
    city: Annotated[str, Field(..., description="City of residence", examples=["Karachi"])]
    age: Annotated[int, Field(..., gt=0, lt=120, description="Age of the patient", examples=[30])]
    gender: Annotated[Literal["Male", "Female"], Field(..., description="Gender of the patient", examples=["Male"])]
    height: Annotated[float, Field(..., gt=0, description="Height of the patient in cm", examples=[175.5])]
    weight: Annotated[float, Field(..., gt=0, description="Weight of the patient in kg", examples=[75.0])]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = self.weight / (self.weight)**2
        return round(bmi, 2)
    
    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif 18.5 <= self.bmi < 25:
            return "Normal weight"
        elif 25 <= self.bmi < 30:
            return "Overweight"
        else:
            return "Obese" 
        
class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0, lt=120)]
    gender: Annotated[Optional[Literal["Male", "Female"]], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]


def load_data():
    with open("patients.json", "r") as f:
        data = json.load(f)
    return data

def save_data(data):
    with open("patients.json", "w") as f:
        json.dump(data, f)

@app.get("/", response_class=HTMLResponse)
async def root():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>FastAPI</title>
    </head>
    <body>
        <h1>Welcome to FastApi</h1>
    </body>
    <button onclick="window.location.href='/about'">About</button>
    <button onclick="window.location.href='/view'">View Patients</button>
    </html>
    """
    return html_content

@app.get("/about", response_class=HTMLResponse)
async def about():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>FastAPI</title>
    </head>
    <body>
        <h1>About FastApi</h1>
    </body>
    </html>
    """
    return html_content


@app.get("/view")
async def view():
    data = load_data()
    return data


@app.get("/view/{patient_id}")
async def view_patient(patient_id: str = Path(..., description="ID of the patient", examples=["P001"])):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail="Patient not found")


@app.get("/sort")
async def sort_patients(sort_by:str = Query(..., description="Field to sort by", examples=["age"]), order: str = Query("asc", description="Sort order: 'asc' or 'desc'", examples=["asc"])):
    sorting_List = ["age","gender","bloodType"]
    if sort_by not in sorting_List:
        raise HTTPException(status_code=400, detail=f"Invalid sort_by value. Must be one of: {', '.join(sorting_List)}")
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid order value. Must be 'asc' or 'desc'")
    data = load_data()

    sort_order = True if order == "desc" else False
    return sorted(data.values(), key=lambda x: x.get(sort_by,0), reverse= sort_order)

@app.post("/create")
def create_patient(patient: Patient):

    #load existing data
    data = load_data()
    # check if patient ID already exists
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient ID already exists")

    # add new patient to data
    data[patient.id] = patient.model_dump(exclude = ['id'])

    # save updated data
    save_data(data)

    return JSONResponse(status_code=201, content={"message": "Patient created successfully"})


@app.put("/update/{patient_id}")
def update_patient(patient_id: str, patient_update: PatientUpdate):

    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    patient_data = data[patient_id]
    update_data = patient_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        if value is not None:
            patient_data[key] = value

    #patient_data -> pydantic object -> updated bmi+verdict
    patient_data['id'] = patient_id
    patient_data_pydantic_obj = Patient(**patient_data)
    patient_data = patient_data_pydantic_obj.model_dump(exclude=['id'])


    #but it will not change the bmi and verdict
    data[patient_id] = patient_data

    save_data(data)

    return JSONResponse(status_code=200, content={"message": "Patient updated successfully"})


@app.delete("/delete/{patient_id}")
def delete_patient(patient_id: str):
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    del data[patient_id]

    save_data(data)

    return JSONResponse(status_code=200, content={"message": "Patient deleted successfully"})