from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime
import pandas as pd
from io import StringIO

from mock_sources import fake_data_sources
from schema import UnifiedEmployee
from field_mapper import fake_field_mappings
from llm_mapper import get_dynamic_field_mapping

app = FastAPI()

# In-memory storage for now
connected_sources = []

# --- Models ---
class Source(BaseModel):
    name: str # e.g. FakeSAP, FakeWorkday

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
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")
    
    # Read CSV content
    contents = await file.read()
    df = pd.read_csv(StringIO(contents.decode("utf-8")))

    fields = df.columns.tolist()
    try:
        mapping = get_dynamic_field_mapping("UploadedCSV", fields)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get field mapping: {str(e)}")
    
    unified_records = []
    for _, row in df.iterrows():
        record = row.to_dict()
        unified_kwargs = {}
        for src_field, unified_field in mapping.items():
            value = record.get(src_field)
            # Ensure employee_id is a string
            if unified_field == "employee_id" and value is not None:
                value = str(value)
            unified_kwargs[unified_field] = value
        
        try:
            unified = UnifiedEmployee(**unified_kwargs)
            unified_records.append(unified.model_dump())
        except Exception as e:
            print(f"Failed to normalize row: {record}, Error: {e}")
    
    return {
        "mapped_fields": mapping,
        "unified_records": unified_records
    }