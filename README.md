# DQRuleDiscovery
This repository contains the code for the Data Quality Rule Discovery tool. It provides a simple FastAPI interface for submitting CSV files and receiving discovered rules in return. 


## Deployment Requirements
### Enviroment Variables 
The application currently does not require any mandatory environment variables.

### Volumes & Persistent Storage
In future versions, we plan to connect to the LTS external storage in Cyclops.
The DQRuleDiscovery application does not require any persistent storage or volumes.

### Network Configuration
The application exposes a FastAPI service on port 5000 by default, allowing clients to upload datasets and receive discovered Denial Constraints via HTTP.
In future versions, the system may interact with external components:
1. Input (LTS) – to automatically retrieve datasets from the Long-Term Storage system.
2. Output (IKB) – to annotate or store discovered Denial Constraints through an integration with the Integration Knowledge Base (IKB) API.
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

## Docker Setup Locally 

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

   

## Questions / Contact
Please reach out (aniol.bisquert@upc.edu) if you have any questions or need assistance with the DQRuleDiscovery tool.

## Notes

- DCs work with tuple pairs, meaning both time and memory usage scale quadratically.
- A dataset size of 2000 (2¹¹) tuples results in analyzing 4 million tuple pairs.
- The paper referenced uses 16000 (2¹⁴) tuples, requiring significantly more processing time.

## License

MIT.

