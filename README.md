# DQRuleDiscovery
This repository contains the code for the Data Quality Rule Discovery tool. It provides a simple FastAPI interface for submitting CSV files and receiving discovered rules in return. 

## Requirements

- Python (3.11)
    - List of packages in `requirements.txt` (install with `pip install -r requirements.txt`)
- MinIO Server (optional, for fetching files from MinIO)
- Metadata Manager (optional, for annotating discovered rules)
- Docker (optional, for running the application in a container)

## Repository Structure
```bash
├── test_data/                     # Example input data
│   └── input.csv
├── core/                          # Main discovery logic
│   ├── main.py
│   ├── utils.py
│   ├── operator_predicate.py
│   ├── denialconstraints.py
│   └── dataset.py
├── app/                           # REST API server
│   └── api.py
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker container definition
├── README.md
├── LICENSE
├── DQRuleDiscovery.ipynb         # Optional notebook-based demo
└── .gitignore
```

## API
The easiest way to interact with the system and explore everything it has to offer is via the API defined in the 
[`app`](./app) directory. To run it, follow the instructions below to set up the Docker container and run the FastAPI server.

### Endpoints
- **POST /discover-all**  
  Upload CSV → Return all denial constraints.

- **POST /discover-unique**  
  Upload CSV → Return unique denial constraints.

- **POST /discover-all-from-minio**  
  Provide `bucket` & `object_key` → Fetch CSV from MinIO → Return all DCs.

- **POST /discover-unique-from-minio**  
  Provide `bucket` & `object_key` → Fetch file from MinIO → Return unique DCs.

- **POST /discover-all-and-annotate**  
  Upload CSV → Discover DCs → Annotate in Metadata Manager.

### Docs

- Swagger UI: `GET /docs`  
- ReDoc: `GET /redoc`


## Usage
To use the DQRuleDiscovery tool, you can either run it locally or inside a Docker container. Below are the instructions for both methods.
### Local Setup
1. Clone the repository:
   ```bash
   git clone https://gitlab.com/cyclops4100006/dqrulediscovery.git
   cd dqrulediscovery
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables (if using MinIO and Metadata Manager):

4. Running the application
    Start the server using Uvicorn:
    ```bash
    uvicorn api:app --host 0.0.0.0 --port 5050 --reload
    ```
5. Test the API
   You can test the API using a tool like Postman or cURL. Here's an example of how to use cURL to send a POST request with a CSV file:

   ```bash
   curl -X POST "http://localhost:5050/discover-all" \
   -F "file=@/path/to/your/input.csv"
   ```
    Replace `/path/to/your/input.csv` with the path to your CSV file.
    [test_data/input.csv](./test_data/input.csv) is provided as an example input file.

### Docker Setup
To run the project inside a Docker container, you can follow these steps:

1. **Build the Docker image**:

   In the root directory of the repository, build the Docker image with the following command:

   ```bash
   docker build -t dq-discovery .
    ```
2. **Run the Docker container:**
After building the image, run the following command to start the container. This will mount your local output folder (/Users/anbipa/Desktop/DTIM/Cyclops) to the container’s /app/outputs directory:

   ```bash
   docker run -p 5050:5000 dq-discovery 
   ```
   - -p: specifies the local:docker ports

    Run the following command if Minio is running at port 9000 and metadata manager is running at port 8080:

   ```bash
   docker run -p 5050:5000 \
   --network long-term-storage_default \
   -e MINIO_ENDPOINT=minio:9200 \
   -e MINIO_ACCESS_KEY=minioadmin \
   -e MINIO_SECRET_KEY=minioadmin123 \
   dq-discovery
   
   docker network connect ontopicsuite_application dq-discovery
   ```

3. **Test the API:**
   You can test the API using a tool like Postman or cURL. Here's an example of how to use cURL to send a POST request with a CSV file:

   ```bash
   curl -X POST "http://localhost:5050/discover-all" \
   -F "file=@/path/to/your/input.csv"
   ```
    Replace `/path/to/your/input.csv` with the path to your CSV file.

    If minio is running, use the following command:
    ```bash
    curl -X POST http://localhost:5050/discover-from-minio \
    -H "Content-Type: application/json" \
    -d '{"bucket": "data-quality-rules-discovery", "object_key": "input.csv"}' 
    ```
    Replace `input.csv` with the name of your CSV file in Minio.
   

## Deployment Requirements
### Enviroment Variables 
Set the following in your environment or via Docker if a MinIO server and Metadata Manager server are running:

```bash
MINIO_ENDPOINT       # e.g. "localhost:9200"
MINIO_ACCESS_KEY     # e.g. "minioadmin"
MINIO_SECRET_KEY     # e.g. "minioadmin123"
METADATA_MANAGER_ENDPOINT  # e.g. "metadata-manager:8080"
METADATA_USER        # e.g. "test"
METADATA_PASS        # e.g. "test"
```

### Volumes & Persistent Storage
The DQRuleDiscovery application does not require any persistent storage or volumes.

### Network Configuration
The application exposes a FastAPI service on port 5000 by default, allowing clients to upload datasets and receive discovered Denial Constraints via HTTP.
The system can interact with external components:
1. Input (LTS) – to automatically retrieve datasets from the Long-Term Storage system. Network configuration is required to connect to the MinIO server.
2. Output (IKB) – to annotate or store discovered Denial Constraints through an integration with the Integration Knowledge Base (IKB) API. Network configuration is required to connect to the Metadata Manager server.
No additional network configuration is required for local deployments.


## Infrastructure Setup & Resource Allocation
### CPU & Memory Requirements
CPU usage is high, but can increase/decrease depending on the size of the dataset file.

### Storage Considerations
- Disk space:
   - Base image size: ~ 350 MB
### External Service Dependencies
- Future: LTS and IKB services for data retrieval and annotation.

### Service Scaling & Load
- The application is designed to run on a single instance.

## Security & Access Credentials
### Authentication & Authorization 
- The application does not require authentication or authorization mechanisms in this version.
### TLS/SSL Requirements
- The application does not require TLS/SSL in this version.



## Questions / Contact
Please reach out (aniol.bisquert@upc.edu) if you have any questions or need assistance with the DQRuleDiscovery tool.

## Notes

- DCs work with tuple pairs, meaning both time and memory usage scale quadratically.
- A dataset size of 2000 (2¹¹) tuples results in analyzing 4 million tuple pairs.
- The paper referenced uses 16000 (2¹⁴) tuples, requiring significantly more processing time.

## License

MIT.

