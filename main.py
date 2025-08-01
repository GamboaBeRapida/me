from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mapping of systems to repair codes
REPAIR_CODES = {
    "navigation": "NAV-01",
    "communications": "COM-02",
    "life_support": "LIFE-03",
    "engines": "ENG-04",
    "deflector_shield": "SHLD-05"
}

# Memory of the last damaged system (simulates persistence)
damaged_system = {"value": None}


@app.get("/status")
def get_status():
    system = random.choice(list(REPAIR_CODES.keys()))
    damaged_system["value"] = system
    return {"damaged_system": system}


@app.get("/repair-bay", response_class=HTMLResponse)
def get_repair_bay():
    system = damaged_system["value"]
    if system is None:
        return HTMLResponse(
            content="<html><body><div>No damaged system selected. Please call /status first.</div></body></html>",
            status_code=400,
        )

    code = REPAIR_CODES.get(system, "UNKNOWN")
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Repair</title>
    </head>
    <body>
        <div class="anchor-point">{code}</div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.post("/teapot")
def post_teapot():
    return Response(content="I'm a teapot", status_code=418)
