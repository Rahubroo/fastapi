from typing import Annotated,Literal
from fastapi import FastAPI, HTTPException,Path,Query
from pydantic import BaseModel,Field,computed_field,Json
import json

from starlette.responses import JSONResponse 

app=FastAPI()

class Patient(BaseModel):
    id:Annotated[str, Field(..., description='Id of the patient', examples=['P001'])]
    name:Annotated[str, Field(...,description='Name of the patient')]
    city:Annotated[str, Field(...,description='City of the patient')]
    age:Annotated[int, Field(...,gt=0,lt=120,description='Age of the patient')]
    gender:Annotated[Literal['male','female','others'], Field(...,description='Gender of the patient')]
    height:Annotated[float, Field(...,gt=0,description='Height of the patient in mtrs')]
    weight:Annotated[float, Field(...,gt=0,description='Weight of the patient in kgs')]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = self.weight / (self.height ** 2)
        return bmi
    
    @computed_field
    @property
    def verdict(self) -> str:
        # bmi_value = self.weight / (self.height ** 2)
        if self.bmi< 18.5:
            return 'Underweight'
        elif self.bmi < 25:
            return 'Normal'
        elif self.bmi < 30:
            return 'Overweight'
        else:
            return 'Obese'
        


def load_data():
    with open('patients.json', 'r') as f:
        data=json.load(f)
    return data 

def save_data(data):
    with open('patients.json', 'w') as f:
        json.dump(data, f)

@app.get('/')
def hello():
    return {'message':'Patient management system Api'}

@app.get('/about')
def about():
    return {'message':'This is a Patient management system backend '}

@app.get('/view')
def show():
    data=load_data()
    return data 

@app.get('/patient/{patient_id}')
def view_patient(patient_id: str = Path(...,description='ID of the Patient in the DB ', example='P001')):

    data=load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404 , detail="Patient not found ")

@app.get('/sort')
def sort_patient(sort_by: str = Query(...,description='sort on the basis of height,weight,bmi '), order: str = Query('asc', description='sort in asc or desc order ')):
    
    valid_fields=['height','weight','bmi','bmi_category']

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400,detail=f'Invalid field select from {valid_fields}')

    if order not in ['asc','desc']:
        raise HTTPException(status_code=400,detail='Invalid  order select between asc and desc ')
    
    data=load_data()

    sort_order=False if order=='asc' else True

    sorted_data=sorted(data.values(),key=lambda x:x.get(sort_by,0), reverse=sort_order)

    return sorted_data

@app.post('/create')
def create_patient(patient: Patient):
    data = load_data()
    
    if patient.id in data:
        raise HTTPException(status_code=400, detail='patient already exists')
    
    data[patient.id] = patient.model_dump(exclude=['id'])
    
    save_data(data)
    
    return JSONResponse(status_code=201,content={"message": "Patient created successfully"})