from fastapi import FastAPI, Request, Response, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import random

from pydantic import BaseModel

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




class PhaseDiagram(BaseModel):
    specific_volume_liquid: float
    specific_volume_vapor: float

# Known “anchor” points from the PV dome (from your sketch):
P_MIN = 0.05    # MPa
VL_MIN = 0.00105  # m³/kg (sat. liquid at P_MIN)
VV_MIN = 30.00    # m³/kg (sat. vapor at P_MIN)

P_CRIT = 10.0     # MPa
V_CRIT = 0.0035   # m³/kg (both phases at critical)

def interp(x, x0, y0, x1, y1):
    """Simple linear interpolation/extrapolation."""
    return y0 + (y1 - y0)*( (x - x0) / (x1 - x0) )

@app.get("/phase-change-diagram", response_model=PhaseDiagram)
async def phase_change_diagram(pressure: float = Query(..., gt=0, description="Pressure in MPa")):
    """
    Return approximate saturated liquid & vapor specific volumes at given pressure.
    Uses linear interpolation between:
      • (0.05 MPa, 0.00105 m³/kg & 30.00 m³/kg)
      • (10 MPa,   0.0035 m³/kg & 0.0035 m³/kg)
    Pressures outside [0.05,10] are linearly extrapolated; at ≥10 MPa both volumes = 0.0035.
    """
    if pressure >= P_CRIT:
        return PhaseDiagram(specific_volume_liquid=V_CRIT,
                            specific_volume_vapor= V_CRIT)

    # interpolate (or extrapolate) between P_MIN and P_CRIT
    v_liq = interp(pressure, P_MIN, VL_MIN, P_CRIT, V_CRIT)
    v_vap = interp(pressure, P_MIN, VV_MIN, P_CRIT, V_CRIT)

    # Sanity check
    if v_liq < 0 or v_vap < 0:
        raise HTTPException(422, f"Computed negative volume for P={pressure}")

    return PhaseDiagram(
        specific_volume_liquid=round(v_liq, 6),
        specific_volume_vapor=round(v_vap, 6)
    )
