from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Literal, Annotated
import pickle
import pandas as pd

# importing the model
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

app = FastAPI()

# City Tier
tier_1_cities = ["Bangalore", "Chennai", "Delhi", "Hyderabad", "Mumbai"]

tier_2_cities = ["Mysore"]

tier_3_cities = ["Kota"]

# pydantic model to validate the input data
class UserInput(BaseModel):

    age: Annotated[int, Field(..., gt=0, lt=120, description="Age of user")]
    weight: Annotated[float, Field(..., gt=0, description="Weight of user")]
    height: Annotated[float, Field(..., gt=0, lt=2.5, description="Height of user")]
    income_lpa: Annotated[float, Field(..., gt=0, description="Income per annum of user")]
    smoker: Annotated[bool, Field(..., description="Smoker status of user")]
    city: Annotated[str, Field(..., description="City of user")]
    occupation: Annotated[Literal['government_job', 'private_job', 'retired', 'student', 'business'], Field(..., description="Occupation of user")]

    @computed_field
    @property
    def bmi(self) -> float:
        return self.weight / (self.height ** 2)
    
    @computed_field
    @property
    def lifestyle_risk(self) -> str:
        if self.smoker and self.bmi > 30:
            return 'high'
        elif self.smoker or self.bmi > 30:
            return 'medium'
        else:
            return 'low'
        
    @computed_field
    @property
    def age_group(self) -> str:
            if self.age < 25:
                return "young_adult"
            elif self.age < 45:
                return "adult"
            elif self.age < 60:
                return "middle_aged"
            return "senior"
    
    @computed_field
    @property
    def city_tier(self) -> str:
        if self.city in tier_1_cities:
            return 1
        elif self.city in tier_2_cities:
            return 2
        elif self.city in tier_3_cities:
            return 3
        
@app.post("/predict")
def predict(data: UserInput):
    input_data = pd.DataFrame([{
        "bmi": data.bmi,
        "age_group": data.age_group,
        "lifestyle_risk": data.lifestyle_risk,
        "city_tier": data.city_tier,
        "income_lpa": data.income_lpa,
        "occupation": data.occupation,
    }])

    prediction = model.predict(input_data)[0]

    return JSONResponse(status_code= 200 ,content={"Predicted_Category": prediction})