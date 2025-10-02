---
title: Breast Cancer Data Collection Tool
emoji: 🎗️
colorFrom: pink
colorTo: purple
sdk: docker
app_port: 8501
pinned: false
license: apache-2.0
---

# Breast Cancer Data Collection Tool

A comprehensive Streamlit web application for collecting and analyzing adherence patterns to chemotherapy treatment among breast cancer patients at UCI (2016-2018).

## Features

- **Progressive Treatment Cycle System**: Baseline data collection followed by sequential treatment cycle tracking
- **Dynamic Medication Management**: Add/remove medications with dosage tracking
- **Comprehensive Data Collection**: Patient demographics, medical history, treatment details, side effects, and outcomes
- **Data Export Ready**: JSON structure designed for easy Excel/CSV export and analysis
- **Form Validation**: Robust validation ensuring data quality and completeness

## Study Period
2016 - 2018

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd breast-cancer-data-collection
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## Usage

1. **Baseline Data**: Complete patient baseline information (demographics, diagnosis, initial treatment plan)
2. **Treatment Cycles**: Add sequential treatment cycles with:
   - Prescribed regimen tracking
   - Medication administration details
   - Laboratory values
   - Side effects monitoring
   - Patient condition assessment

## Data Structure

- **JSON Storage**: Each patient has a unified JSON file with baseline_data and treatment_cycles arrays
- **Progressive Data**: Treatment cycles are added incrementally to existing patient files
- **Export Ready**: Data structure optimized for research analysis and reporting

## Contributing

This tool was developed for research purposes at UCI. Please ensure patient data privacy and comply with institutional guidelines.

## License

Research use only - UCI Institutional Guidelines Apply