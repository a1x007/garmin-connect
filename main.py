from fastapi import FastAPI
from garminconnect import Garmin
import datetime
import os

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Garmin FastAPI is running!"}

@app.get("/steps")
def get_steps():
    try:
        # Login to Garmin
        api = Garmin(os.environ["GARMIN_USER"], os.environ["GARMIN_PASS"])
        api.login()
        
        today = datetime.date.today().isoformat()
        steps = api.get_steps_data(today)
        return {"steps": steps}
    except Exception as e:
        return {"error": str(e)}
