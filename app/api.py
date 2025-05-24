# api.py
import traceback

from fastapi import FastAPI, File, UploadFile, Body
from fastapi.responses import JSONResponse

from core.dc_discovery import discover_dcs
import shutil
import os
import uuid
import uvicorn

import tempfile
import boto3
from botocore.exceptions import BotoCoreError, ClientError

import requests

# Environment variables (set via Docker)
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9200")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin123")
MINIO_SECURE = False  # set to True if using HTTPS

METADATA_MANAGER_HOST = os.getenv("METADATA_MANAGER_HOST", "metadata-manager")
METADATA_MANAGER_PORT = os.getenv("METADATA_MANAGER_PORT", "8080")


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


@app.post("/discover-from-minio")
async def discover_from_minio(
    bucket: str = Body(...),
    object_key: str = Body(...)
):
    try:
        s3 = boto3.client(
            "s3",
            endpoint_url=f"http{'s' if MINIO_SECURE else ''}://{MINIO_ENDPOINT}",
            aws_access_key_id=MINIO_ACCESS_KEY,
            aws_secret_access_key=MINIO_SECRET_KEY,
        )

        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
            s3.download_fileobj(bucket, object_key, tmp_file)
            tmp_file_path = tmp_file.name

        result = discover_dcs(tmp_file_path)
        return {"denial_constraints": result}
    except (BotoCoreError, ClientError) as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": f"MinIO error: {str(e)}"})
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)


@app.post("/discover-and-annotate")
async def discover_and_annotate(file: UploadFile = File(...)):
    temp_filename = f"/tmp/{uuid.uuid4()}.csv"
    dataset_id = str(uuid.uuid4())

    try:
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        dc_result = discover_dcs(temp_filename)

        payload = {
            "name": f"Dataset {dataset_id}",
            "description": "Discovered and annotated by dqrulediscovery",
            "rules": dc_result
        }

        url = f"http://{METADATA_MANAGER_HOST}:{METADATA_MANAGER_PORT}/metadata-manager/annotation-dataset/{dataset_id}"
        response = requests.put(url, json=payload)

        return {
            "dataset_id": dataset_id,
            "metadata_manager_status": response.status_code,
            "metadata_manager_response": response.json()
        }

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)