from fastapi import FastAPI
from garminconnect import Garmin, GarminConnectAuthenticationError
import datetime
import os

app = FastAPI()

garmin_client = None
login_error = None

def login_garmin():
    global garmin_client, login_error
    try:
        garmin_client = Garmin(os.environ["GARMIN_USER"], os.environ["GARMIN_PASS"])
        garmin_client.login()
        login_error = None
    except Exception as e:
        garmin_client = None
        login_error = str(e)

@app.on_event("startup")
def startup_event():
    login_garmin()

def safe_garmin_call(func, *args, **kwargs):
    global garmin_client
    if garmin_client is None:
        login_garmin()
        if garmin_client is None:
            raise Exception(f"Login failed: {login_error}")
    try:
        return func(*args, **kwargs)
    except GarminConnectAuthenticationError:
        # Session expired or auth error - retry login once
        login_garmin()
        if garmin_client is None:
            raise Exception(f"Login failed: {login_error}")
        return func(*args, **kwargs)  # Retry the call after re-login

@app.get("/")
async def root():
    return {"message": "Garmin FastAPI is running!"}

@app.get("/login_status")
def login_status():
    if garmin_client:
        return {"status": "logged_in"}
    else:
        return {"status": "not_logged_in", "error": login_error}

@app.get("/username")
def get_username():
    try:
        profile = safe_garmin_call(garmin_client.get_full_name)
        return {"username": profile}
    except Exception as e:
        return {"error": str(e)}

@app.get("/steps")
def get_steps():
    try:
        today = datetime.date.today().isoformat()
        steps = safe_garmin_call(garmin_client.get_steps_data, today)
        return {"steps": steps}
    except Exception as e:
        return {"error": str(e)}
