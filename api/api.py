# api.py
from fastapi import FastAPI, File, UploadFile
from src.main import discover_dcs
import shutil
import os
import uuid

app = FastAPI()

@app.post("/discover")
async def discover(file: UploadFile = File(...)):
    temp_filename = f"/tmp/{uuid.uuid4()}.csv"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result = discover_dcs(temp_filename)
        return {"denial_constraints": result}
    finally:
        os.remove(temp_filename)
