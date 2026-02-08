# from fastapi import FastAPI, HTTPException, Depends
# from pydantic import BaseModel, Field
# from typing import List, Literal, Optional
# # from LLM.compliance_reasoner import check_compliance
# check_engine = None

# app = FastAPI(
#     title="VeriClause API",
#     description="Policy Compliance Decision Engine",
#     version="1.0"
# )

# # -----------------------------
# # Security (simple API key)
# # -----------------------------
# API_KEY = "dev-secret-key"  # move to env later
# @app.on_event("startup")
# def load_engine():
#     global check_engine
#     from LLM.compliance_reasoner import check_compliance
#     check_engine = check_compliance

# def verify_api_key(api_key: str):
#     if api_key != API_KEY:
#         raise HTTPException(status_code=401, detail="Unauthorized")

# # -----------------------------
# # Request / Response Models
# # -----------------------------
# class ComplianceRequest(BaseModel):
#     scenario: str = Field(
#         ..., 
#         min_length=10,
#         description="User action or scenario to evaluate"
#     )

# class Violation(BaseModel):
#     clause: str
#     text: str

# class Justification(BaseModel):
#     description: str

# class ComplianceResponse(BaseModel):
#     status: Literal["COMPLIANT", "NON_COMPLIANT", "NEEDS_REVIEW"]
#     violations: List[Violation]
#     justification: List[str]
#     confidence: float = Field(..., ge=0.0, le=1.0)

# # -----------------------------
# # API Endpoint
# # -----------------------------
# @app.post("/check-compliance", response_model=ComplianceResponse)
# def check_policy(
#     payload: ComplianceRequest,
#     api_key: str = Depends(verify_api_key)
# ):
#     return check_engine(payload.scenario)

#     return ComplianceResponse(
#         status=result["status"],
#         violations=result.get("violations", []),
#         justification=result.get("justification", []),
#         confidence=result["confidence"]
#     )

# AFTER CHANGING THE ENGINES

from fastapi import FastAPI
from pydantic import BaseModel
from core import engine

app = FastAPI(title="VeriClause API")

@app.on_event("startup")
def startup_event():
    from core.loader import load_engine
    engine.engine = load_engine()

@app.get("/")
def health():
    return {"status": "ok"}

class ComplianceRequest(BaseModel):
    scenario: str

@app.post("/check-compliance")
def check(payload: ComplianceRequest):
    if engine.engine is None:
        return {"error": "Engine not ready"}
    return engine.engine(payload.scenario)
