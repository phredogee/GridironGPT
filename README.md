![Python](https://img.shields.io/badge/Python-3.11-blue)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)

# 🏈 GridironGPT — ESPN Pipeline CLI

**Gridiron GPT** is a specialized toolkit for fetching, processing, and auditing fantasy football data. It features an ESPN-style player pipeline with dry-run diagnostics and semantic auditing to ensure data integrity before ingestion.

## 🚀 Quick Start

### Installation
Ensure you are in your virtual environment (`phredenv`):
```bash
pip install -r requirements.txt
```

### Running the Pipeline
Use the provided shell script for standard ESPN dry-runs:
```bash
./run_zodiac.sh --year 2025
```

For more granular control, run the module directly:
```bash
python -m gridiron_gpt.cli.draft --season 2025 --dry-run
```

## 🏗 Project Structure
* **`gridiron_gpt/`**: Core logic including fetchers, embeddings, and the CLI.
* **`modules/`**: Predictor and pipeline logic.
* **`scripts/`**: Utility scripts for testing and environment management.
* **`tests/`**: Suite for validating pipeline flow and import integrity.

## 🧪 Development & Testing
Run the test suite to verify the environment and data logic:
```bash
export PYTHONPATH=$(pwd)
pytest gridiron_gpt/tests/
```

## 🛠 Features
* **Dry-Run Mode**: Validate data alignment without writing to the database.
* **Semantic Auditing**: Integrated checks for player bio and embedding consistency.
* **Flexible Fetchers**: Modular components for retrieving ESPN data.
