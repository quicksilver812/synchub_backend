from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Form, Body
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime
import pandas as pd
from io import StringIO
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, func
from models import Employee
from database import SessionLocal, get_db
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import Runnable
import csv
import io

import loaders.sap_loader
import loaders.workday_loader


from loaders.loader_registry import LOADER_REGISTRY
from loaders.csv_loader import CSVLoader
from schema import UnifiedEmployee
from field_mapper import fake_field_mappings
from llm_mapper import get_dynamic_field_mapping
from database import SessionLocal, engine
from models import Employee, QALog
from agent import sql_agent

QALog.metadata.create_all(bind=engine)
Employee.metadata.create_all(bind=engine)
app = FastAPI(
    title="SyncHub API",
    description="A backend platform to connect enterprise data sources, auto-map employee records with LLMs, and normalize everything into a unified schema.",
    version="1.0.0",
    contact={
        "name": "Allen Conroy Dsouza",
        "email": "allendsouza812@gmail.com",
    },
)

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
@app.get("/", summary="Health check")
def read_root():
    return{"message": "SyncHub API is alive!"}

@app.post("/connect-source", summary="Connect a data source")
def connect_source(source: Source):
    if source.name not in LOADER_REGISTRY:
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

@app.delete("/disconnect-source", summary="Disconnect a data source")
def disconnect_source(source: Source = Body(...)):
    global connected_sources
    initial_count = len(connected_sources)

    connected_sources = [
        s for s in connected_sources if s["name"] != source.name
    ]

    if len(connected_sources) == initial_count:
        raise HTTPException(status_code=404, detail=f"{source.name} was not connected.")
    
    return {"message": f"{source.name} disconnected successfully"}

@app.get("/get-data", summary="Get data from connected sources")
def get_data():
    all_data = []
    db: Session = next(get_db())

    for source in connected_sources:
        src_name = source["name"]
        source_data = LOADER_REGISTRY[src_name].load()

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


@app.get("/list-connected-sources", summary="List connected sources")
def list_sources():
    return {"connected_sources": connected_sources}

@app.get("/normalised-data", summary="Normalise data into a unified format")
def get_normalised_data():
    all_records = []
    for source_name, loader in LOADER_REGISTRY.items():
        records = loader.load()
        for record in records:
            try:
                unified = normalise_employee_record(record, source_name)
                all_records.append(unified.model_dump())
            except Exception as e:
                print(f"Failed to normalize from {source_name}: {e}")
    
    return {"normalized_records": all_records}

@app.get("/field-mapping/{source_name}", summary="Get field mapping from original to normalised")
def get_field_mapping(source_name: str):
    if source_name not in LOADER_REGISTRY:
        raise HTTPException(status_code=404, detail="Source not found.")
    
    sample_record = LOADER_REGISTRY[source_name].load()[0]
    try:
        mapping = get_dynamic_field_mapping(source_name, list(sample_record.keys()))
        return {"source": source_name, "field_mapping": mapping}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mapping failed: {str(e)}")
    
@app.post("/upload-csv", summary="Upload CSV files")
async def upload_csv(source_name: str = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.content_type != 'text/csv':
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    content = await file.read()
    decoded = content.decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded))
    rows = list(reader)

    if not rows:
        raise HTTPException(status_code=400, detail="CSV is empty")

    # Create or update the CSV loader
    csv_loader = CSVLoader()
    csv_loader.set_data(source_name, rows)
    LOADER_REGISTRY[source_name] = csv_loader

    # LLM field mapping
    field_mapping = get_dynamic_field_mapping(source_name, list(rows[0].keys()))

    saved = 0
    for record in rows:
        unified_kwargs = {}
        for src_field, unified_field in field_mapping.items():
            unified_kwargs[unified_field] = record.get(src_field)

        employee = Employee(**unified_kwargs)

        existing = db.query(Employee).filter_by(employee_id=employee.employee_id).first()
        if existing:
            for key, value in unified_kwargs.items():
                setattr(existing, key, value)
        else:
            db.add(employee)
        saved += 1

    db.commit()
    return {"message": f"{saved} records processed and saved from {source_name}"}

@app.get("/employees", summary="Display all data records")
def list_employees(db: Session = Depends(get_db)):
    try:
        employees = db.query(Employee).all()
        return {"count": len(employees), "employees": [e.to_dict() for e in employees]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/ask", summary="Ask questions to the database")
def ask_question(request: AskRequest, db: Session = Depends(get_db)):
    question = request.question.strip()
    
    if not question:
        raise HTTPException(status_code=400, detail="Empty question")

    try:
        # Raw SQL response from agent
        raw_answer = sql_agent.invoke(question)
        
        # Format output
        if isinstance(raw_answer, str):
            formatted = raw_answer.strip()
        else:
            formatted = str(raw_answer)

        # Log to DB
        log = QALog(question=question, answer=formatted)
        db.add(log)
        db.commit()
        db.refresh(log)

        return {
            "question": question,
            "answer": formatted
        }

    except Exception as e:
        return {
            "question": question,
            "error": str(e)
        }
    
@app.get("/logs", summary="Logs of prior queries and answers")
def get_logs(db: Session = Depends(get_db)):
    logs = db.query(QALog).order_by(QALog.asked_at.desc()).limit(20).all()
    return {
        "logs": [
            {
                "id": log.id,
                "question": log.question,
                "answer": log.answer,
                "asked_at": log.asked_at
            }
            for log in logs
        ]
    }

@app.get("/stats", summary="Overall statistics of database")
def get_stats(db: Session = Depends(get_db)):
    try:
        # Total employees
        total_employees = db.query(func.count(Employee.id)).scalar()

        # Count by department
        dept_counts = db.query(Employee.department, func.count()).group_by(Employee.department).all()
        department_stats = {dept or "Unknown": count for dept, count in dept_counts}

        # Count by location
        loc_counts = db.query(Employee.location, func.count()).group_by(Employee.location).all()
        location_stats = {loc or "Unknown": count for loc, count in loc_counts}

        # Count by connected source
        source_stats = {
            source["name"]: len(LOADER_REGISTRY[source["name"]].load())
            for source in connected_sources
        }

        return {
            "total_employees": total_employees,
            "connected_sources": len(connected_sources),
            "source_wise_records": source_stats,
            "by_department": department_stats,
            "by_location": location_stats,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/source-schema/{source_name}", summary="Check schema of source for debugging")
def source_schema(source_name: str):
    if source_name not in LOADER_REGISTRY:
        raise HTTPException(status_code=404, detail="Source not found")

    records = LOADER_REGISTRY[source_name].load()
    if not records:
        return {"source": source_name, "fields": [], "sample": None}

    first = records[0]
    return {
        "source": source_name,
        "fields": list(first.keys()),
        "sample": first
    }
