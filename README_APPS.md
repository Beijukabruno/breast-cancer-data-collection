# Breast Cancer Data Collection Tool

This repository contains a Streamlit application for collecting breast cancer treatment data.

## Files Overview

### App Versions

- **`app.py`** - Production version for Hugging Face Spaces deployment
  - Uses `/tmp/data` directory for file storage (required for Hugging Face)
  - Configured with Hugging Face metadata
  - Includes patient ID sanitization for safe file paths

- **`app_local.py`** - Local development version
  - Uses local `data/` directory for file storage
  - Optimized for local development and testing
  - Full functionality without cloud deployment constraints

### Supporting Files

- **`requirements.txt`** - Python dependencies
- **`districts.txt`** - Uganda districts list
- **`Dockerfile`** - Container configuration for Hugging Face Spaces
- **`.github/workflows/deploy.yml`** - CI/CD pipeline for automatic deployment

## Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the local version
streamlit run app_local.py
```

### Hugging Face Spaces Deployment
The main `app.py` is automatically deployed via GitHub Actions to Hugging Face Spaces when changes are pushed to the main branch.

## Features

- **Baseline Data Collection**: Patient demographics, diagnosis, and treatment planning
- **Treatment Cycle Management**: Progressive cycle data entry with dynamic medication tracking
- **Data Validation**: Comprehensive form validation and error handling
- **JSON Export**: Structured data storage for analysis
- **Patient ID Support**: Handles special characters safely (e.g., "1275/17")

## Data Storage

- **Local**: Data saved to `./data/patient_[sanitized_id]/` directory
- **Hugging Face**: Data saved to `/tmp/data/patient_[sanitized_id]/` directory
- **Format**: JSON files with baseline data and treatment cycles

## Development Notes

Patient IDs with special characters (like "1275/17") are automatically sanitized for file paths while preserving the original ID in the data.

Both versions include the same functionality - the only difference is the data storage location to accommodate different deployment environments.