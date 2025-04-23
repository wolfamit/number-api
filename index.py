from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from datetime import datetime
import uuid
from time import sleep
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()
# Define the proxy
proxy = {
    "http": os.getenv("PROXY_HTTP"),
    "https": os.getenv("PROXY_HTTPS")
}

header = {
    "sec-ch-ua": "\"Not:A-Brand\";v=\"24\", \"Google Chrome\";v=\"134\", \"Chromium\";v=\"134\"",
    "Accept-Language": "en-US,en;q=0.0",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "greq": "GQ:"+str(uuid.uuid4()),
    "Content-Language": "en",
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json, text/plain, */*",
    "bmirak": "webbm",
    "Referer": "https://www.irctc.co.in/nget/profile/user-signup",
    "sec-ch-ua-platform": "\"Windows\""
}

def is_mobile_available(mobile_number: str, isd_code: str = "91", retries: int = 100, delay: int = 1) -> bool:
    print(f"Waiting for availability...")
    url = f"{os.getenv('AVAILABILITY_URL')}{mobile_number}&isd={isd_code}"
    for attempt in range(1, retries + 1):
        try:
            responsemob = requests.get(url, headers=header, proxies=proxy,timeout=10, verify=False)
            responsemob.raise_for_status()
            response_data = responsemob.json()
            mobile_available = response_data.get("mobileAvailable")
            if mobile_available == "FALSE":
                return False
            if mobile_available == "TRUE":
                return True
        except requests.exceptions.RequestException as e:
            print(e)
        except ValueError:
            pass
        if attempt < retries:
            sleep(delay)
    return False

class PhoneNumber(BaseModel):
    phone_number: int

@app.get('/')
def root():
    return {"message" : "HELLO WORLD"} 

@app.post("/getNumber/")
async def get_number(request: PhoneNumber):
    # Verify phone number with external service
    available = is_mobile_available(str(request.phone_number))
    return {"success": available, "PhoneNumber": request.phone_number}
    

# Create a handler for the serverless functi