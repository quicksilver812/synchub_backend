from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime

from mock_sources import fake_data_sources

app = FastAPI()

# In-memory storage for now
connected_sources = []

# --- Models ---
class Source(BaseModel):
    name: str # e.g. FakeSAP, FakeWorkday

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
    for s in connected_sources:
        src = s["name"]
        all_data.extend(fake_data_sources[src])
    return {"sources_connected": connected_sources, "data": all_data}

@app.get("/list-connected-sources")
def list_sources():
    return {"connected_sources": connected_sources}