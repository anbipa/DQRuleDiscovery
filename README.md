# DQRuleDiscovery Demo
This repository contains the code for the Data Quality Rule Discovery tool. 


## Deployment Requirements
### Enviroment Variables 
The application currently does not require any mandatory environment variables.

### Volumes & Persistent Storage
In this initial version, our tool uses docker volumes to allow users to provide their input files and access outputs.
- **Input Volume**: The input volume is mounted to the container's `/app/data` directory. Users can place their input files in this directory.
- **Output Volume**: The output volume is mounted to the container's `/app/outputs` directory. The application will save its output files in this directory.

In future versions, we plan to connect to the LTS external storage in Cyclops.

The DQRuleDiscovery application does not require any persistent storage or volumes. In this initial version, the tool reads the input data from a input.csv file located in a local specified directory. Seamasly, The output file is saved in a specified output directory.
### Network Configuration
The application does not require any specific network configuration. It runs locally and does not expose any ports.
In the future, main may communicate with:
1. (input) the LTS to retrieve the dataset to be scrutinized. 
2. (output) the IKB to annotate the discovered DC through a provided API.


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
├── data
│   └── input.csv
├── outputs
├── src
│   ├── main.py
│   ├── utils.py
│   ├── operator_predicate.py
│   ├── denialconstraints.py
│   └── dataset.py
├── requirements.txt
├── Dockerfile
├── README.md
├── LICENSE
├── DQRuleDiscovery.ipynb
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
   docker run -v /path/to/local/input.csv:/app/data/input.csv -v /path/to/local/outputs:/app/outputs --name dq-container dq-discovery
   ```
   - -d: Runs the container in detached mode (in the background).
   - -v /path/to/local/input.csv:/app/data/input.csv: Mounts the local input.csv file to the container's /app/data/input.csv.
   - -v /path/to/local/outputs:/app/outputs: Mounts the local directory to the container, so the output files will be saved locally.
   - --name dq-container: Names the container for easy reference.
   - dq-discovery: The Docker image name.

   

## Questions / Contact
Please reach out (aniol.bisquert@upc.edu) if you have any questions or need assistance with the DQRuleDiscovery tool.

## Notes

- DCs work with tuple pairs, meaning both time and memory usage scale quadratically.
- A dataset size of 2000 (2¹¹) tuples results in analyzing 4 million tuple pairs.
- The paper referenced uses 16000 (2¹⁴) tuples, requiring significantly more processing time.

## License

MIT.

