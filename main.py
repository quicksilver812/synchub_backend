from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Form
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime
import pandas as pd
from io import StringIO
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from models import Employee
from database import SessionLocal, get_db
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import Runnable
import csv
import io


from mock_sources import fake_data_sources
from schema import UnifiedEmployee
from field_mapper import fake_field_mappings
from llm_mapper import get_dynamic_field_mapping
from database import SessionLocal, engine
from models import Employee
from agent import sql_agent

Employee.metadata.create_all(bind=engine)
app = FastAPI()

# In-memory storage for now
connected_sources = []

# --- Models ---
class Source(BaseModel):
    name: str # e.g. FakeSAP, FakeWorkday

class AskRequest(BaseModel):
    question: str

def normalise_employee_record(record:dict, source_name:str) -> UnifiedEmployee:

    field_map = get_dynamic_field_mapping(source_name, list[record.keys()])
    
    # field_map = fake_field_mappings[source_name]

    unified_kwargs = {}
    for src_field, unified_field in field_map.items():
        unified_kwargs[unified_field] = record.get(src_field)

    return UnifiedEmployee(**unified_kwargs)

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
    db: Session = next(get_db())

    for source in connected_sources:
        src_name = source["name"]
        source_data = fake_data_sources[src_name]

        for record in source_data:
            unified = normalise_employee_record(record, src_name)
            data = unified.model_dump()

            existing = db.scalar(select(Employee).where(Employee.employee_id == data["employee_id"]))

            if existing:
                for key, value in data.items():
                    setattr(existing, key, value)
            else:
                new_emp = Employee(**data)
                db.add(new_emp)

            all_data.append(data)

    try:
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    return {"sources_connected": connected_sources, "data": all_data}


@app.get("/list-connected-sources")
def list_sources():
    return {"connected_sources": connected_sources}

@app.get("/normalised-data")
def get_normalised_data():
    all_records = []
    for source_name, records in fake_data_sources.items():
        for record in records:
            try:
                unified = normalise_employee_record(record, source_name)
                all_records.append(unified.model_dump())
            except Exception as e:
                print(f"Failed to normalize from {source_name}: {e}")
    
    return {"normalized_records": all_records}

@app.get("/field-mapping/{source_name}")
def get_field_mapping(source_name: str):
    if source_name not in fake_data_sources:
        raise HTTPException(status_code=404, detail="Source not found.")
    
    sample_record = fake_data_sources[source_name][0]
    try:
        mapping = get_dynamic_field_mapping(source_name, list(sample_record.keys()))
        return {"source": source_name, "field_mapping": mapping}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mapping failed: {str(e)}")
    
@app.post("/upload-csv")
async def upload_csv(source_name: str = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.content_type != 'text/csv':
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    content = await file.read()
    decoded = content.decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded))
    rows = list(reader)

    if not rows:
        raise HTTPException(status_code=400, detail="CSV is empty")

    field_mapping = get_dynamic_field_mapping(source_name, list(rows[0].keys()))

    saved = 0
    for record in rows:
        unified_kwargs = {}
        for src_field, unified_field in field_mapping.items():
            unified_kwargs[unified_field] = record.get(src_field)

        employee = Employee(**unified_kwargs)

        # Upsert logic
        existing = db.query(Employee).filter_by(employee_id=employee.employee_id).first()
        if existing:
            for key, value in unified_kwargs.items():
                setattr(existing, key, value)
        else:
            db.add(employee)
        saved += 1

    db.commit()
    return {"message": f"{saved} records processed and saved from {source_name}"}

@app.get("/employees")
def list_employees(db: Session = Depends(get_db)):
    try:
        employees = db.query(Employee).all()
        return {"count": len(employees), "employees": [e.to_dict() for e in employees]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/ask")
def ask_question(request: AskRequest):
    question = request.question.strip()
    
    if not question:
        raise HTTPException(status_code=400, detail="Empty question")

    try:
        response = sql_agent.invoke(question)
        return {
            "question": question,
            "answer": response
        }
    except Exception as e:
        return {
            "question": question,
            "error": str(e)
        }