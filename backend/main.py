from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ussd_flow import process_ussd_request

app = FastAPI(title="NdalamaLite USSD Simulator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class USSDRequest(BaseModel):
    sessionId: str
    phoneNumber: str
    networkCode: str
    serviceCode: str
    text: str

@app.post("/ussd")
async def ussd_callback(request: USSDRequest):
    """
    Main webhook for USSD requests.
    Expects standard Africa's Talking style schema loosely.
    For this simulator, `text` will just be the latest user input.
    """
    
    # Process the request through our state machine
    response_text = process_ussd_request(request.phoneNumber, request.text)
    
    # Custom notification parsing for the simulation
    notification = None
    if "[NOTIFY]" in response_text:
        parts = response_text.split("[NOTIFY]")
        response_text = parts[0].strip()
        notification = parts[1].strip()
    
    # Return response formatted for USSD (CON = continue, END = end session)
    if "0. Back" in response_text or "0. Main Menu" in response_text or "1." in response_text:
        res = {"response": f"CON {response_text}"}
    else:
        res = {"response": f"END {response_text}"}
        
    if notification:
        res["notification"] = notification
        
    return res

from fastapi.staticfiles import StaticFiles
import os

# Ensure the path resolves correctly whether run from backend or root
frontend_path = os.path.join(os.path.dirname(__file__), "../frontend")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
