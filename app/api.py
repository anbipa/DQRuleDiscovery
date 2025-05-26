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
from requests.auth import HTTPBasicAuth
import re

from core.unique_dc_discovery import discover_unique_constraints

# Environment variables (set via Docker)
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9200")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin123")
MINIO_SECURE = False  # set to True if using HTTPS

METADATA_MANAGER_ENDPOINT = os.getenv("METADATA_MANAGER_ENDPOINT", "metadata-manager:8080")

AUTH_USER = os.getenv("METADATA_USER", "test")
AUTH_PASS = os.getenv("METADATA_PASS", "test")

app = FastAPI()

@app.post("/discover-all")
async def discover_all(file: UploadFile = File(...)):
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

@app.post("/discover-unique")
async def discover_unique(file: UploadFile = File(...)):
    temp_filename = f"/tmp/{uuid.uuid4()}.csv"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result = discover_unique_constraints(temp_filename)
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



@app.post("/discover-all-from-minio")
async def discover_all_from_minio(
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

@app.post("/discover-unique-from-minio")
async def discover_unique_from_minio(
    bucket: str = Body(...),
    object_key: str = Body(...)
):
    try:
        file_ext = os.path.splitext(object_key)[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            s3 = boto3.client(
                "s3",
                endpoint_url=f"http{'s' if MINIO_SECURE else ''}://{MINIO_ENDPOINT}",
                aws_access_key_id=MINIO_ACCESS_KEY,
                aws_secret_access_key=MINIO_SECRET_KEY,
            )
            s3.download_fileobj(bucket, object_key, tmp_file)
            tmp_file_path = tmp_file.name

        result = discover_unique_constraints(tmp_file_path)
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

@app.post("/discover-all-and-annotate")
async def discover_all_and_annotate(file: UploadFile = File(...)):
    dataset_id = "dqrulediscovery_annotations"

    # Create annotation_id based on sanitized input filename
    base_name = os.path.basename(file.filename)
    name_part = os.path.splitext(base_name)[0]
    name_clean = re.sub(r"[^a-zA-Z0-9_-]", "", name_part).lower() or "unnamed"
    annotation_id = f"{name_clean}_{uuid.uuid4().hex[:8]}"

    temp_filename = f"/tmp/{annotation_id}.csv"

    try:
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        dc_result = discover_dcs(temp_filename)

        payload = {
            "regularDatasetId": name_clean,
            "denialConstraints": dc_result
        }

        url = f"http://{METADATA_MANAGER_ENDPOINT}/metadata-manager/annotation-dataset/{dataset_id}/{annotation_id}"
        response = requests.put(url, json=payload, auth=HTTPBasicAuth(AUTH_USER, AUTH_PASS))

        return {
            "dataset_id": dataset_id,
            "annotation_id": annotation_id,
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