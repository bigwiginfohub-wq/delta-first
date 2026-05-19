from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from validator import DeltaFirstV501
import time

app = FastAPI()

# CORS (frontend compatibility)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# Health Check
# -----------------------
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"status": "ok", "service": "delta-first-api"}

# -----------------------
# Validate Endpoint
# -----------------------
@app.post("/validate")
def validate(payload: dict):
    try:
        data = DeltaFirstV501(**payload)

        # Core rules (your business logic)
        valid = (
            data.integrity_score >= 70.0 and
            data.friction_score <= 0.70 and
            data.mcl_coefficient >= 0.50 and
            data.primary_driver in ["H1", "H2", "H3"] and
            data.boundary.strip() != ""
        )

        return {
            "valid": valid,
            "audit_id": data.audit_id,
            "primary_driver": data.primary_driver,
            "mcl_coefficient": data.mcl_coefficient,
            "friction_score": data.friction_score,
            "validated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "warnings": [] if valid else ["Threshold conditions not fully met"]
        }

    except ValidationError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Invalid payload",
                "errors": e.errors()
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Server error", "error": str(e)}
        )
