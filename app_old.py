import streamlit as st
from datetime import datetime, date
import pandas as pd
import json
import os

def text_clear():
    st.session_state.patient_id = ""
    if 'income_other' in st.session_state:
        st.session_state.income_other = ""
    if 'immunohisto_specify' in st.session_state:
        st.session_state.immunohisto_specify = ""
    if 'commodities_other' in st.session_state:
        st.session_state.commodities_other = ""

def number_clear():
    st.session_state.age_input = 0

def date_clear():
    if 'date_admitted' in st.session_state:
        st.session_state.date_admitted = date.today()

def load_uganda_districts():
    """Load Uganda districts from districts.txt file"""
    try:
        with open('districts.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract district names, removing the categories and file counts
        districts = []
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            # Skip empty lines and single letter headers
            if line and len(line) > 1 and not line in ['A', 'B', 'D', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'R', 'S', 'T', 'W', 'Y', 'Z']:
                # Extract district name before any parentheses
                if '(' in line:
                    district_name = line.split('(')[0].strip()
                else:
                    district_name = line.strip()
                
                # Remove leading spaces and bullet points
                district_name = district_name.lstrip(' •-')
                
                if district_name and district_name not in districts:
                    districts.append(district_name)
        
        return sorted(districts)
    except FileNotFoundError:
        st.error("districts.txt file not found. Please ensure the file exists in the same directory.")
        return ["File not found - Please check districts.txt"]
    except Exception as e:
        st.error(f"Error loading districts: {str(e)}")
        return ["Error loading districts"]

def master_clear():
    text_clear()
    number_clear()
    date_clear()

st.set_page_config(page_title="Breast Cancer Data Collection", layout="centered")
st.title("🎗️ Data Capture Tool for Analysis of Adherence Patterns to Chemotherapy")
st.markdown("### Association with Recurrence-Free Survival Among Breast Cancer Patients at UCI")
st.markdown("---")
st.markdown("""
**Purpose**: This data capture tool will be used to collect patient data from admission records, treatment files, 
medical records, and laboratory test results of patients who had chemotherapy as part of their treatment plan 
at the Uganda Cancer Institute between 2016 - 2018.
""")
st.markdown("---")

# --- SESSION STATE INIT ---
if 'patient_data' not in st.session_state:
    st.session_state.patient_data = {}
if 'data_directory' not in st.session_state:
    st.session_state.data_directory = "data"

# --- DATA STORAGE CONFIGURATION ---
with st.sidebar:
    st.header("Settings")
    data_dir = st.text_input(
        "Data Storage Directory",
        value=st.session_state.data_directory,
        help="Enter the path where you want to store the data files. Use absolute path for different drives (e.g., C:/MyData)"
    )
    if data_dir != st.session_state.data_directory:
        st.session_state.data_directory = data_dir


# --- SECTION 1: BASELINE DATA ---
st.header("📋 Section 1: Baseline Data (Collected at First Visit Only)")

# Load Uganda districts
uganda_districts = load_uganda_districts()

# Basic patient information
col1, col2, col3 = st.columns(3)

with col1:
    patient_id = st.text_input("1. Patient ID", help="Enter unique patient identifier", key="patient_id")

with col2:
    age = st.number_input("2. Age (years)", min_value=0, max_value=120, step=1, key="age_input")

with col3:
    # Date range for breast cancer study (2016-2018)
    min_date = date(2016, 1, 1)
    max_date = date(2018, 12, 31)
    date_admitted = st.date_input(
        "Date Admitted",
        value=date(2017, 1, 1),
        min_value=min_date,
        max_value=max_date,
        key="date_admitted",
        help="Select date between 2016-2018"
    )

# Education level dropdown
education_options = ["None", "Primary", "Secondary", "Tertiary", "Not captured"]
education_level = st.selectbox("3. Highest level of education", education_options, key="education_level")

# Marital status dropdown
marital_options = ["Single", "Married", "Divorced", "Widowed", "Not captured"]
marital_status = st.selectbox("4. Current marital status", marital_options, key="marital_status")

# Income source with conditional text input
income_options = ["Farmer", "Business", "Professional", "Unemployed", "Other"]
income_source = st.selectbox("5. Main source of income", income_options, key="income_source")

# Conditional text input for "Other" income source
income_other = ""
if income_source == "Other":
    income_other = st.text_input("Specify other source of income:", key="income_other")

# District of residence dropdown
district = st.selectbox("6. District of residence", uganda_districts, key="district")

# Initial diagnosis dropdown
diagnosis_options = ["Initial screening", "Inflammatory breast cancer", "Invasive ductal carcinoma", 
                    "Invasive lobular carcinoma", "Ductal carcinoma in situ", "Lobular carcinoma in situ", 
                    "Triple-negative breast cancer", "HER2-positive breast cancer", "Other"]
initial_diagnosis = st.selectbox("7. Initial diagnosis", diagnosis_options, key="initial_diagnosis")

# Immunohistochemistry results
immunohisto_present = st.radio("8. Immunohistochemistry results present", ["Yes", "No"], key="immunohisto_present")

# Conditional text input for immunohistochemistry specification
immunohisto_specify = ""
if immunohisto_present == "Yes":
    immunohisto_specify = st.text_area("Specify immunohistochemistry results:", key="immunohisto_specify")

# Disease stage dropdown
stage_options = ["Stage I", "Stage II", "Stage III", "Stage IV"]
disease_stage = st.selectbox("9. Disease stage at first diagnosis", stage_options, key="disease_stage")

# Comorbidities with multiple selection
st.write("10. List of other comorbidities:")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    diabetes = st.checkbox("Diabetes", key="diabetes")
with col2:
    hypertension = st.checkbox("Hypertension", key="hypertension")
with col3:
    hiv = st.checkbox("HIV", key="hiv")
with col4:
    none_captured = st.checkbox("None captured", key="none_captured")
with col5:
    other_commodities = st.checkbox("Other", key="other_commodities")

# Conditional text input for "Other" comorbidities
commodities_other = ""
if other_commodities:
    commodities_other = st.text_input("Specify other comorbidities:", key="commodities_other")

# --- FORM SUBMISSION ---
if st.button("💾 Save Baseline Data", type="primary"):
    # Collect all form data
    baseline_data = {
        "patient_id": patient_id,
        "age": age,
        "date_admitted": date_admitted.strftime("%Y-%m-%d"),
        "education_level": education_level,
        "marital_status": marital_status,
        "income_source": income_source,
        "income_other": income_other if income_source == "Other" else None,
        "district": district,
        "initial_diagnosis": initial_diagnosis,
        "immunohisto_present": immunohisto_present,
        "immunohisto_specify": immunohisto_specify if immunohisto_present == "Yes" else None,
        "disease_stage": disease_stage,
        "comorbidities": {
            "diabetes": diabetes,
            "hypertension": hypertension,
            "hiv": hiv,
            "none_captured": none_captured,
            "other": other_commodities,
            "other_specify": commodities_other if other_commodities else None
        },
        "collection_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Validation
    if not patient_id:
        st.error("❌ Patient ID is required!")
    elif age <= 0:
        st.error("❌ Please enter a valid age!")
    else:
        # Save data
        try:
            # Use the configured data directory
            base_dir = os.path.expanduser(st.session_state.data_directory)
            foldername = os.path.join(base_dir, f"patient_{patient_id}")
            
            if not os.path.exists(base_dir):
                os.makedirs(base_dir, exist_ok=True)
            if not os.path.exists(foldername):
                os.makedirs(foldername, exist_ok=True)

            filename = os.path.join(foldername, f"baseline_data_{patient_id}.json")
            
            with open(filename, "w") as f:
                json.dump(baseline_data, f, indent=4, default=str)

            st.success(f"✅ Baseline data for Patient {patient_id} saved successfully!")
            st.success(f"📁 File saved to: {filename}")
            
            # Store in session state for potential future use
            st.session_state.patient_data = baseline_data
            
        except Exception as e:
            st.error(f"❌ Error saving data: {str(e)}")

# --- CLEAR FORM BUTTON ---
if st.button("🔄 Clear Form", on_click=master_clear):
    st.success("🎉 Form cleared and ready for next patient!")
    st.session_state.patient_data = {}


# --- FOOTER ---
st.markdown("---")
st.header("📊 Data Collection Information")
st.write("This data capture tool is designed for collecting baseline patient data for the breast cancer chemotherapy adherence study at UCI.")
st.write("**Study Period:** 2016 - 2018")
st.write("**Data Sources:** Admission records, treatment files, medical records, and laboratory test results")
st.write("**Note:** Please ensure all information is accurate before submission. Use 'Not captured' for missing information.")
