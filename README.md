# DQRuleDiscovery Demo
This repository contains the code for demonstrating the Data Quality Rule Discovery tool. The python notebook serves as a demo and showcases the funnctionality of discovering valid denial constraints given a dataset.

## Requirements

Ensure you have the following installed before running the notebook:

### Dependencies

This project requires the following Python libraries:

- `pandas` - Data manipulation and analysis
- `numpy` (version 2.0) - For bitwise count operations and numerical computing

### Installation

To install the required dependencies, run:

```bash
pip install pandas numpy
```

## Usage
### Python Notebook 
1. Clone the repository:

   ```bash
   git clone <repository_url>
   cd <repository_name>
   ```

2. Open the Jupyter Notebook:

   ```bash
   jupyter notebook notebook_name.ipynb
   ```

3. Modify the dataset path as needed:
   - Set the dataset path in the `dataset` variable.
   - Ensure the number of rows is a multiple of 8 (preferably a power of 2).

4. Run all cells to extract and analyze Denial Constraints (DCs).

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
   docker run -d -v /path/to/local/outputs:/app/outputs --name dq-container dq-discovery
   ```
   - -d: Runs the container in detached mode (in the background).

   - -v /path/to/local/outputs:/app/outputs: Mounts the local directory to the container, so the output files will be saved locally.

   - --name dq-container: Names the container for easy reference.

   - dq-discovery: The Docker image name.
## Notes

- DCs work with tuple pairs, meaning both time and memory usage scale quadratically.
- A dataset size of 2000 (2¹¹) tuples results in analyzing 4 million tuple pairs.
- The paper referenced uses 16000 (2¹⁴) tuples, requiring significantly more processing time.

## License

MIT.