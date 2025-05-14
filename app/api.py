# api.py
import traceback

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

from core.dc_discovery import discover_dcs
import shutil
import os
import uuid
import uvicorn

app = FastAPI()

@app.post("/discover")
async def discover(file: UploadFile = File(...)):
    temp_filename = f"/tmp/{uuid.uuid4()}.csv"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result = discover_dcs(temp_filename)
        return {"denial_constraints": result}
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)