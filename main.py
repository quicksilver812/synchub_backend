from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime

from mock_sources import fake_data_sources
from schema import UnifiedEmployee

app = FastAPI()

# In-memory storage for now
connected_sources = []

# --- Models ---
class Source(BaseModel):
    name: str # e.g. FakeSAP, FakeWorkday

def normalise_employee_record(record:dict, source_name:str) -> UnifiedEmployee:
    if source_name == "FakeSAP":
        return UnifiedEmployee(
            employee_id=record["emp_id"],
            name=record["emp_name"],
            salary=record.get("emp_sal"),
            email=record.get("emp_email_id"),
            department=record.get("emp_dept"),
            location=record.get("emp_work_location")
        )

    elif source_name == "FakeWorkday":
        return UnifiedEmployee(
            employee_id=record["id"],
            name=record["name"],
            salary=record.get("sal"),
            email=record.get("email_id"),
            department=record.get("dept"),
            location=record.get("work_location")
        )
    else:
        return ValueError("Unknown Source")

# --- Routes ---
@app.get("/")
def read_root():
    return{"message": "SyncHub API is alive!"}

@app.post("/connect-source")
def connect_source(source: Source):
    if source.name not in fake_data_sources:
        raise HTTPException(status_code=404, detail = 'Source not supported yet')
    
    for s in connected_sources:
        if s["name"] == source.name:
            return {"message": f"{source.name} already connected"}
    
    connected_sources.append({
            "name": source.name,
            "connected_at": datetime.now().isoformat()
        }
    )
    return {"message": f"{source.name} connected successfully"}

@app.get("/get-data")
def get_data():
    all_data = []
    for source in connected_sources:
        src_name = source["name"]
        source_data = fake_data_sources[src_name]

        for record in source_data:
            unified = normalise_employee_record(record, src_name)
            all_data.append(unified.model_dump())
    return {"sources_connected": connected_sources, "data": all_data}

@app.get("/list-connected-sources")
def list_sources():
    return {"connected_sources": connected_sources}