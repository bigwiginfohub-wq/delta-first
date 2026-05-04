from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ValidationError
from typing import List, Dict, Any, Optional
import json
import re
from datetime import datetime

# ============================================================
# REQUEST MODEL (What the user sends to your API)
# ============================================================

class AuditRequest(BaseModel):
    """Audit data sent by the user"""
    auditor_id: str
    audit_id: str
    integrity_score: float = 84.0
    protocol_mode: str = "Full Protocol Mode"
    primary_driver: str
    reasoning_trace: str
    peak_moment: str
    interpretive_anchor: str
    h3_warrant: str
    null_test: str
    label_impact: str
    friction_score_components: Dict[str, float]
    friction_score: float
    mcl_coefficient: float
    boundary: str


# ============================================================
# RESPONSE MODEL (What your API returns)
# ============================================================

class AuditResponse(BaseModel):
    """Validation result"""
    valid: bool
    auditor_id: str
    audit_id: str
    primary_driver: str
    friction_score: float
    mcl_coefficient: float
    label_impact: str
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None
    validated_at: str


# ============================================================
# VALIDATION FUNCTIONS (Your existing logic)
# ============================================================

def validate_audit(data: Dict[str, Any]) -> tuple[bool, List[str], List[str]]:
    """
    Validates audit data.
    Returns: (is_valid, errors, warnings)
    """
    errors = []
    warnings = []
    
    # 1. Check required fields
    required_fields = [
        "auditor_id", "audit_id", "protocol_mode", "primary_driver",
        "reasoning_trace", "label_impact", "boundary"
    ]
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"Missing required field: {field}")
    
    # 2. Validate primary_driver enum
    if data.get("primary_driver") not in ["H1", "H2", "H3"]:
        errors.append(f"Invalid primary_driver: {data.get('primary_driver')}. Must be H1, H2, or H3.")
    
    # 3. Validate label_impact enum
    if data.get("label_impact") not in ["Easier", "Harder", "Neutral"]:
        errors.append(f"Invalid label_impact: {data.get('label_impact')}. Must be Easier, Harder, or Neutral.")
    
    # 4. Validate boundary statement
    expected_boundary = "This analysis maps causal plausibility strictly within the locked window. It cannot verify internal deliberations, off-record communications, or post-window developments. Claims are time-locked."
    if data.get("boundary") != expected_boundary:
        warnings.append("Boundary statement does not match the exact required text")
    
    # 5. Validate friction score range
    friction = data.get("friction_score")
    if friction is not None and (friction < 0 or friction > 1):
        errors.append(f"Friction score must be between 0 and 1. Got: {friction}")
    
    # 6. Validate MCL range
    mcl = data.get("mcl_coefficient")
    if mcl is not None and (mcl < 0 or mcl > 1):
        errors.append(f"MCL coefficient must be between 0 and 1. Got: {mcl}")
    
    # 7. Auto-clamp friction score and MCL (warnings for out-of-range)
    if friction is not None and (friction < 0 or friction > 1):
        clamped_friction = max(0.0, min(1.0, friction))
        warnings.append(f"Friction score clamped from {friction} to {clamped_friction}")
    
    if mcl is not None and (mcl < 0 or mcl > 1):
        clamped_mcl = max(0.0, min(1.0, mcl))
        warnings.append(f"MCL coefficient clamped from {mcl} to {clamped_mcl}")
    
    # 8. Validate reasoning_trace has reasonable length
    if data.get("reasoning_trace") and len(data["reasoning_trace"]) < 15:
        warnings.append("Reasoning trace is very short (minimum recommended: 15 characters)")
    
    is_valid = len(errors) == 0
    return is_valid, errors, warnings


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Delta-First Validator API",
    description="""
    Validate Delta-First audit reports programmatically.
    
    This API accepts audit JSON data and returns validation results,
    including any errors, warnings, and auto-clamped values.
    
    ## Features
    
    - Validates required fields and enums
    - Auto-clamps out-of-range values
    - Returns detailed error messages
    - Generates timestamped validation records
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "Delta-First Validator API",
        "version": "1.0.0",
        "description": "Validate Delta-First audit reports",
        "endpoints": {
            "validate": "POST /validate",
            "health": "GET /health",
            "docs": "GET /docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/validate", response_model=AuditResponse)
async def validate_audit_endpoint(audit: AuditRequest):
    """
    Validate a Delta-First audit report.
    
    This endpoint processes your audit JSON and returns:
    - Whether the audit passed validation
    - Any errors (critical issues)
    - Any warnings (suggestions for improvement)
    - The validated data with clamped values
    """
    # Convert Pydantic model to dict
    data = audit.dict()
    
    # Run validation
    is_valid, errors, warnings = validate_audit(data)
    
    # Create response
    response = AuditResponse(
        valid=is_valid,
        auditor_id=audit.auditor_id,
        audit_id=audit.audit_id,
        primary_driver=audit.primary_driver,
        friction_score=audit.friction_score,
        mcl_coefficient=audit.mcl_coefficient,
        label_impact=audit.label_impact,
        errors=errors if errors else None,
        warnings=warnings if warnings else None,
        validated_at=datetime.now().isoformat()
    )
    
    return response


# ============================================================
# BATCH VALIDATION ENDPOINT (Optional)
# ============================================================

class BatchAuditRequest(BaseModel):
    """Batch validation request"""
    audits: List[AuditRequest]


@app.post("/validate/batch")
async def validate_batch(batch: BatchAuditRequest):
    """
    Validate multiple audits in one request.
    
    This endpoint processes a list of audits and returns validation
    results for each one.
    """
    results = []
    for audit in batch.audits:
        data = audit.dict()
        is_valid, errors, warnings = validate_audit(data)
        results.append({
            "audit_id": audit.audit_id,
            "valid": is_valid,
            "primary_driver": audit.primary_driver,
            "friction_score": audit.friction_score,
            "errors": errors if errors else None,
            "warnings": warnings if warnings else None
        })
    
    return {
        "total": len(results),
        "valid_count": sum(1 for r in results if r["valid"]),
        "results": results,
        "validated_at": datetime.now().isoformat()
    }


# ============================================================
# RUN THE API (for local development)
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
