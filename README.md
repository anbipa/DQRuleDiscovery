# DQRuleDiscovery Demo
This repository contains the code for demonstrating the Data Quality Rule Discovery tool. The python notebook serves as a demo and showcases the funnctionality of discovering valid denial constraints given a dataset.

## Requirements

Ensure you have the following installed before running the notebook:

### Dependencies

This project requires the following Python libraries:

- `pandas` - Data manipulation and analysis
- `numpy` (version 2.0) - For bitwise count operations and numerical computing
- `operator` - Standard Python operators as functions
- `itertools` - Efficient looping constructs
- `re` - Regular expressions for pattern matching

### Installation

To install the required dependencies, run:

```bash
pip install pandas numpy operator itertools
```

(Note: `operator` and `itertools` are built-in Python modules and do not require installation.)

## Usage

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

## Notes

- DCs work with tuple pairs, meaning both time and memory usage scale quadratically.
- A dataset size of 2000 (2¹¹) tuples results in analyzing 4 million tuple pairs.
- The paper referenced uses 16000 (2¹⁴) tuples, requiring significantly more processing time.

## License

MIT.