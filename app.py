"""
Breast Cancer Data Collection Tool - Hugging Face Spaces Version
===============================================================
Data capture tool for analysis of adherence patterns to chemotherapy and their 
association with recurrence-free survival among breast cancer patients at UCI.

Study Period: 2016 - 2018
Author: Data Collection Team
Date: October 2025

This version is configured for deployment on Hugging Face Spaces and uses /tmp/data
for file storage to avoid permission issues. For local development, use app_local.py

title: Breast Cancer Data Collection Tool
emoji: �
colorFrom: pink
colorTo: purple
sdk: streamlit
sdk_version: 1.28.0
app_file: app.py
pinned: false
"""

import streamlit as st
from datetime import datetime, date
import pandas as pd
import json
import os
import time
from typing import Dict, List, Optional


# =========================================
def render_linear_baseline_form(districts: List[str]) -> Dict:
    """Render the linear baseline form following exact PDF numbering"""
    st.header("Section 1: Baseline Data (Collected at First Visit Only)")
    st.markdown("---")
    
    # 1. Patient ID=========================================
# CONFIGURATION AND CONSTANTS
# ========================================================================================

class Config:
    """Application configuration constants"""
    STUDY_START_DATE = date(2016, 1, 1)
    STUDY_END_DATE = date(2025, 12, 31)
    DEFAULT_DATA_DIR = "/tmp/data"
    
    # Form options
    EDUCATION_OPTIONS = ["None", "Primary", "Secondary", "Tertiary", "Not captured"]
    MARITAL_OPTIONS = ["Single", "Married", "Divorced", "Widowed", "Not captured"]
    INCOME_OPTIONS = ["Farmer", "Business", "Professional", "Unemployed", "Other"]
    DIAGNOSIS_OPTIONS = [
        "Invasive ductal carcinoma",
        "Moderately differentiated invasive ductal carcinoma",
        "Moderately differentiated ductal carcinoma",
        "Ductal carcinoma in situ",
        "Infiltrating carcinoma",
        "Poorly differentiated adenocarcinoma",
        "Invasive adenocarcinoma",
        "Invasive lobular carcinoma",
        "Other"
    ]
    STAGE_OPTIONS = ["Stage 0", "Stage I", "Stage II", "Stage III", "Stage IV"]
    
    # Predefined medication options
    MEDICATION_OPTIONS = [
        "Adriamycin",
        "Cyclophosphamide", 
        "Doxorubicin",
        "Dexamethasone",
        "5-fluorouracil",
        "Ondansetron",
        "Ranitidine",
        "Metoclopramide",
        "Plasil",
        "Ifosfamide",
        "Mesna",
        "Paclitaxel",
        "Epirubicin",
        "Carboplatin",
        "Capecitabine (Xeloda)",
        "Docetaxel",
        "Epirubicin",
        "Promethazine",
        "Docetaxel",
        "Tamoxifen",
        "Anastrazole",
        "Ifosfamide",
        "Mesra",
        "Promethazine"
    ]
    
    IMMUNOHISTO_OPTIONS = [
        "ER-positive (ER+)",
        "PR-positive (PR+)", 
        "HR-positive (HR+)",
        "HR-negative (HR-)",
        "HER2-positive (HER2+)",
        "ER-negative (ER-)",
        "HER2-negative (HER2-)"
    ]
    
    REGIMEN_OPTIONS = [
        "AC (Doxorubicin + Cyclophosphamide)",
        "AC-T (Doxorubicin + Cyclophosphamide + Paclitaxel)",
        "CMF (Cyclophosphamide + Methotrexate + 5-Fluorouracil)",
        "FAC (5-Fluorouracil + Doxorubicin + Cyclophosphamide)",
        "FEC (5-Fluorouracil + Epirubicin + Cyclophosphamide)",
        "TC (Docetaxel + Cyclophosphamide)",
        "TCH (Docetaxel + Carboplatin + Trastuzumab)",
        "TAC (Docetaxel + Doxorubicin + Cyclophosphamide)",
        "EC-T (Epirubicin + Cyclophosphamide + Paclitaxel)",
        "Capecitabine (Xeloda) monotherapy",
        "Tamoxifen monotherapy",
        "Other"
    ]
    SIDE_EFFECTS_OPTIONS = ["Nausea", "Fatigue", "Vomiting", "Neuropathy", "None", "Other"]
    CONDITION_OPTIONS = ["Better", "Weaker", "Other"]


# ========================================================================================
# UTILITY FUNCTIONS
# ========================================================================================

def sanitize_patient_id(patient_id: str) -> str:
    """Sanitize patient ID for safe use in file paths"""
    # Replace forward slashes and other problematic characters with underscores
    return patient_id.replace("/", "_").replace("\\", "_").replace(":", "_").replace("*", "_").replace("?", "_").replace('"', "_").replace("<", "_").replace(">", "_").replace("|", "_")

def load_uganda_districts() -> List[str]:
    """Load Uganda districts from districts.txt file"""
    try:
        with open('districts.txt', 'r', encoding='utf-8') as f:
            districts = [line.strip() for line in f.readlines() if line.strip()]
        return sorted(districts)
    except FileNotFoundError:
        st.error("districts.txt file not found. Please ensure the file exists in the same directory.")
        return ["File not found - Please check districts.txt"]
    except Exception as e:
        st.error(f"Error loading districts: {str(e)}")
        return ["Error loading districts"]


def initialize_session_state() -> None:
    """Initialize Streamlit session state variables"""
    if 'patient_data' not in st.session_state:
        st.session_state.patient_data = {}
    if 'data_directory' not in st.session_state:
        st.session_state.data_directory = Config.DEFAULT_DATA_DIR
    if 'current_patient_id' not in st.session_state:
        st.session_state.current_patient_id = None
    if 'baseline_completed' not in st.session_state:
        st.session_state.baseline_completed = False
    if 'current_cycle' not in st.session_state:
        st.session_state.current_cycle = 0
    if 'show_final_followup' not in st.session_state:
        st.session_state.show_final_followup = False


def clear_form_fields() -> None:
    """Clear all form input fields"""
    # Clear text inputs
    for key in ['patient_id', 'income_other', 'immunohisto_other_specify', 'commodities_other', 'treatment_not_started_reason']:
        if key in st.session_state:
            del st.session_state[key]
    
    # Clear numeric inputs
    for key in ['age_input', 'chemo_cycles']:
        if key in st.session_state:
            del st.session_state[key]
    
    # Clear radio button selections
    for key in ['education_level', 'marital_status', 'income_source', 'immunohisto_present', 'disease_stage', 'treatment_started']:
        if key in st.session_state:
            del st.session_state[key]
    
    # Clear dropdown selections  
    for key in ['district', 'initial_diagnosis', 'regimen_prescribed']:
        if key in st.session_state:
            del st.session_state[key]
    
    # Clear checkboxes
    checkbox_keys = ['diabetes', 'hypertension', 'hiv', 'none_captured', 'other_comorbidities',
                    'er_positive', 'er_negative', 'pr_positive', 'hr_positive', 'hr_negative', 
                    'her2_positive', 'her2_negative', 'immunohisto_other_check']
    for key in checkbox_keys:
        if key in st.session_state:
            del st.session_state[key]
    
    # Reset date to default
    if 'date_admitted' in st.session_state:
        del st.session_state['date_admitted']


def validate_form_data(form_data: Dict) -> Optional[str]:
    """Validate form data and return error message if any"""
    patient_id = form_data.get("patient_id", "")
    age = form_data.get("age", 0)
    
    if not patient_id or patient_id.strip() == "":
        return "Patient ID is required!"
    
    if age <= 0:
        return "Please enter a valid age!"
    
    if len(patient_id.strip()) < 3:
        return "Patient ID must be at least 3 characters long!"
    
    # Check required radio button selections
    if form_data.get("education_level") is None:
        return "Please select an education level!"
    
    if form_data.get("marital_status") is None:
        return "Please select a marital status!"
    
    if form_data.get("income_source") is None:
        return "Please select an income source!"
    
    # Check dropdown selections (placeholder check)
    if form_data.get("district", "").startswith("-- Select"):
        return "Please select a district!"
    
    if form_data.get("initial_diagnosis", "").startswith("-- Select"):
        return "Please select an initial diagnosis!"
    
    if form_data.get("immunohisto_present") is None:
        return "Please select if immunohistochemistry results are present!"
    
    if form_data.get("disease_stage") is None:
        return "Please select a disease stage!"
    
    # Check chemotherapy fields
    if form_data.get("chemo_cycles_prescribed", 0) <= 0:
        return "Please enter the number of chemotherapy cycles prescribed!"
    
    if form_data.get("regimen_prescribed", "").startswith("-- Select"):
        return "Please select a prescribed regimen!"
    
    if form_data.get("treatment_started") is None:
        return "Please select if the patient started treatment!"
    
    return None


def save_patient_data(data: Dict, data_type: str = "baseline") -> tuple[bool, str]:
    """Save patient data to JSON file"""
    try:
        # Create directory structure
        base_dir = os.path.expanduser(st.session_state.data_directory)
        sanitized_patient_id = sanitize_patient_id(data['patient_id'])
        patient_folder = os.path.join(base_dir, f"patient_{sanitized_patient_id}")
        
        os.makedirs(base_dir, exist_ok=True)
        os.makedirs(patient_folder, exist_ok=True)
        
        # Main patient file
        main_filename = os.path.join(patient_folder, f"patient_{sanitized_patient_id}.json")
        
        # Load existing data or create new structure
        if os.path.exists(main_filename):
            with open(main_filename, "r") as f:
                patient_data = json.load(f)
        else:
            patient_data = {
                "patient_id": data['patient_id'],
                "baseline_data": {},
                "treatment_cycles": [],
                "final_followup": {}
            }
        
        if data_type == "baseline":
            patient_data["baseline_data"] = data
        elif data_type == "cycle":
            # Add or update cycle data
            cycle_num = data.get("cycle_number", 1)
            # Check if cycle already exists
            existing_cycle = next((c for c in patient_data["treatment_cycles"] if c.get("cycle_number") == cycle_num), None)
            if existing_cycle:
                # Update existing cycle
                existing_cycle.update(data)
            else:
                # Add new cycle
                patient_data["treatment_cycles"].append(data)
        elif data_type == "final_followup":
            patient_data["final_followup"] = data
        
        # Save updated data
        with open(main_filename, "w") as f:
            json.dump(patient_data, f, indent=4, default=str)
        
        return True, main_filename
    
    except Exception as e:
        return False, str(e)


def load_patient_data(patient_id: str) -> Dict:
    """Load patient data from JSON file"""
    try:
        base_dir = os.path.expanduser(st.session_state.data_directory)
        sanitized_patient_id = sanitize_patient_id(patient_id)
        patient_folder = os.path.join(base_dir, f"patient_{sanitized_patient_id}")
        filename = os.path.join(patient_folder, f"patient_{sanitized_patient_id}.json")
        
        if os.path.exists(filename):
            with open(filename, "r") as f:
                return json.load(f)
        else:
            return {
                "patient_id": patient_id,
                "baseline_data": {},
                "treatment_cycles": [],
                "final_followup": {}
            }
    except Exception as e:
        return {
            "patient_id": patient_id,
            "baseline_data": {},
            "treatment_cycles": [],
            "final_followup": {}
        }


def render_dynamic_medications(cycle_num: int) -> List[Dict]:
    """Render dynamic medication input fields with dropdown selection"""
    st.markdown("**Medications & Dosages:**")
    
    # Initialize medications in session state
    med_key = f"cycle_{cycle_num}_medications"
    if med_key not in st.session_state:
        st.session_state[med_key] = [{"name": "", "dose": "", "unit": "mg"}]
    
    medications = []
    
    for i, med in enumerate(st.session_state[med_key]):
        col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
        
        with col1:
            # Medication dropdown with search
            medication_options = ["-- Select Medication --"] + Config.MEDICATION_OPTIONS + ["Other (specify)"]
            selected_med = st.selectbox(
                f"Medication {i+1}:",
                medication_options,
                index=0 if not med.get("name") else (
                    medication_options.index(med.get("name")) if med.get("name") in medication_options else 0
                ),
                key=f"med_name_{cycle_num}_{i}"
            )
            
            # If "Other" is selected, show text input
            if selected_med == "Other (specify)":
                med_name = st.text_input(
                    "Specify medication:",
                    value=med.get("custom_name", ""),
                    key=f"med_custom_{cycle_num}_{i}",
                    placeholder="Enter medication name"
                )
            else:
                med_name = selected_med if not selected_med.startswith("-- Select") else ""
        
        with col2:
            med_dose = st.text_input(
                f"Dose:",
                value=med.get("dose", ""),
                key=f"med_dose_{cycle_num}_{i}",
                placeholder="e.g., 60, 1.5"
            )
        
        with col3:
            med_unit = st.selectbox(
                f"Unit:",
                ["mg", "mg/m2", "g", "mL", "tabs", "IU"],
                index=0 if med.get("unit", "mg") == "mg" else ["mg", "mg/m2", "g", "mL", "tabs", "IU"].index(med.get("unit", "mg")),
                key=f"med_unit_{cycle_num}_{i}"
            )
        
        with col4:
            if len(st.session_state[med_key]) > 1:
                if st.button("Remove", key=f"remove_med_{cycle_num}_{i}", help="Remove medication"):
                    st.session_state[med_key].pop(i)
                    st.rerun()
        
        # Only add to medications list if a medication is actually selected
        if med_name and not med_name.startswith("-- Select"):
            medications.append({
                "name": med_name,
                "dose": med_dose,
                "unit": med_unit
            })
    
    # Add medication button
    if st.button("Add Medication", key=f"add_med_{cycle_num}"):
        st.session_state[med_key].append({"name": "", "dose": "", "unit": "mg"})
        st.rerun()
    
    return medications


def render_cycle_form(patient_id: str, cycle_number: int) -> Dict:
    """Render Chemotherapy Treatment Cycle form for any cycle number"""
    st.header(f"Chemotherapy Treatment Cycle {cycle_number}")
    st.markdown("---")
    
    # Prescribed regimen for this cycle
    regimen_options = ["-- Select Regimen --"] + Config.REGIMEN_OPTIONS
    regimen_prescribed = st.selectbox(
        "Prescribed regimen for this cycle:",
        regimen_options,
        key=f"cycle{cycle_number}_regimen_prescribed",
        index=None,
        help="Select the chemotherapy regimen prescribed for this treatment cycle"
    )
    
    # Prescription date
    prescription_date = st.date_input(
        "Chemotherapy prescription date:",
        value=date(2017, 7, 1),
        min_value=Config.STUDY_START_DATE,
        max_value=Config.STUDY_END_DATE,
        key=f"cycle{cycle_number}_prescription_date"
    )
    
    # Dynamic medications
    medications = render_dynamic_medications(cycle_number)
    
    # Date chemotherapy received
    chemo_received_date = st.date_input(
        "Date chemotherapy received:",
        value=date(2017, 7, 1),
        min_value=Config.STUDY_START_DATE,
        max_value=Config.STUDY_END_DATE,
        key=f"cycle{cycle_number}_chemo_received_date"
    )
    
    # Laboratory values
    st.markdown("**Laboratory Results:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        wbc = st.number_input(
            "Total WBC:",
            min_value=0.0,
            max_value=50000.0,
            step=100.0,
            key=f"cycle{cycle_number}_wbc",
            help="White Blood Cell count"
        )
    
    with col2:
        hemoglobin = st.number_input(
            "Hemoglobin:",
            min_value=0.0,
            max_value=25.0,
            step=0.1,
            key=f"cycle{cycle_number}_hemoglobin",
            help="Hemoglobin level (g/dL)"
        )
    
    with col3:
        platelets = st.number_input(
            "Platelets:",
            min_value=0,
            max_value=1000000,
            step=1000,
            key=f"cycle{cycle_number}_platelets",
            help="Platelet count"
        )
    
    # Was chemotherapy received on prescription day?
    st.markdown("**Was chemotherapy received on the day of prescription?**")
    chemo_on_prescription_day = st.radio(
        "Select option:",
        ["Yes", "No"],
        key=f"cycle{cycle_number}_chemo_on_prescription_day",
        horizontal=True,
        label_visibility="collapsed",
        index=None
    )
    
    # Conditional reason if No
    chemo_delay_reason = ""
    if chemo_on_prescription_day == "No":
        chemo_delay_reason = st.text_input(
            "If No, Why?:",
            key=f"cycle{cycle_number}_chemo_delay_reason",
            placeholder="Please specify reason..."
        )
    
    # Side effects
    st.markdown("**Documented side effects post treatment:**")
    side_effects_present = st.radio(
        "Are there documented side effects?",
        ["Yes", "No"],
        key=f"cycle{cycle_number}_side_effects_present",
        horizontal=True,
        index=None
    )
    
    # Side effects checkboxes
    side_effects = []
    side_effects_other = ""
    if side_effects_present == "Yes":
        st.markdown("Select side effects:")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            if st.checkbox("Nausea", key=f"cycle{cycle_number}_nausea"):
                side_effects.append("Nausea")
        with col2:
            if st.checkbox("Fatigue", key=f"cycle{cycle_number}_fatigue"):
                side_effects.append("Fatigue")
        with col3:
            if st.checkbox("Vomiting", key=f"cycle{cycle_number}_vomiting"):
                side_effects.append("Vomiting")
        with col4:
            if st.checkbox("Neuropathy", key=f"cycle{cycle_number}_neuropathy"):
                side_effects.append("Neuropathy")
        with col5:
            if st.checkbox("None", key=f"cycle{cycle_number}_none_side_effects"):
                side_effects.append("None")
        with col6:
            if st.checkbox("Other", key=f"cycle{cycle_number}_other_side_effects"):
                side_effects.append("Other")
                side_effects_other = st.text_input(
                    "Specify other side effects:",
                    key=f"cycle{cycle_number}_side_effects_other",
                    placeholder="Please specify..."
                )
    
    # Patient condition
    st.markdown("**What is the general condition of the patient at the time of the clinic visit?**")
    patient_condition = st.radio(
        "Select condition:",
        Config.CONDITION_OPTIONS,
        key=f"cycle{cycle_number}_patient_condition",
        horizontal=True,
        label_visibility="collapsed",
        index=None
    )
    
    # Conditional input for "Other" condition
    condition_other = ""
    if patient_condition == "Other":
        condition_other = st.text_input(
            "Specify other condition:",
            key=f"cycle{cycle_number}_condition_other",
            placeholder="Please specify..."
        )
    
    # Hospitalization
    st.markdown("**Was there any hospitalization between this cycle and the previous cycle?**")
    hospitalization = st.radio(
        "Select option:",
        ["Yes", "No"],
        key=f"cycle{cycle_number}_hospitalization",
        horizontal=True,
        label_visibility="collapsed",
        index=None
    )
    
    # Conditional reason for hospitalization
    hospitalization_reason = ""
    if hospitalization == "Yes":
        hospitalization_reason = st.text_input(
            "If yes, specify the reason:",
            key=f"cycle{cycle_number}_hospitalization_reason",
            placeholder="Please specify reason..."
        )
    
    # Return cycle data
    return {
        "cycle_number": cycle_number,
        "patient_id": patient_id,
        "regimen_prescribed": regimen_prescribed if regimen_prescribed and not regimen_prescribed.startswith("-- Select") else None,
        "prescription_date": prescription_date.strftime("%Y-%m-%d"),
        "medications": medications,
        "chemo_received_date": chemo_received_date.strftime("%Y-%m-%d"),
        "laboratory": {
            "wbc": wbc,
            "hemoglobin": hemoglobin,
            "platelets": platelets
        },
        "chemo_on_prescription_day": chemo_on_prescription_day,
        "chemo_delay_reason": chemo_delay_reason if chemo_on_prescription_day == "No" else None,
        "side_effects_present": side_effects_present,
        "side_effects": side_effects if side_effects_present == "Yes" else [],
        "side_effects_other": side_effects_other if "Other" in side_effects else None,
        "patient_condition": patient_condition,
        "condition_other": condition_other if patient_condition == "Other" else None,
        "hospitalization": hospitalization,
        "hospitalization_reason": hospitalization_reason if hospitalization == "Yes" else None
    }


def render_final_followup_form(patient_id: str) -> Dict:
    """Render the Final Follow-Up Visit form"""
    st.header("Recurrence-Free Survival and Outcomes (Final Follow-Up Visit)")
    st.markdown("---")
    
    # Last recorded review date
    st.markdown("**Last recorded review date:**")
    last_review_date = st.date_input(
        "Review Date",
        value=date.today(),
        min_value=Config.STUDY_START_DATE,
        max_value=Config.STUDY_END_DATE,
        help="Select the date of the last follow-up visit"
    )
    
    # General condition
    st.markdown("**What was the general condition of the patient on the last visit?**")
    general_condition = st.text_area(
        "General Condition",
        placeholder="Describe the patient's general condition...",
        help="Enter details about the patient's overall condition during the last visit"
    )
    
    # Follow-up attendance
    st.markdown("**Did the patient come back for follow up?**")
    followup_attendance = st.radio(
        "Follow-up Attendance",
        options=["Yes", "No"],
        index=None,
        help="Select whether the patient attended follow-up visits"
    )
    
    # Conditional: Why no follow-up
    no_followup_reason = None
    if followup_attendance == "No":
        st.markdown("**If No, why?**")
        no_followup_reason = st.text_area(
            "Reason for no follow-up",
            placeholder="Explain why the patient did not come for follow-up...",
            help="Provide details about why follow-up was missed"
        )
    
    # Comorbidities developed
    st.markdown("**List of any comorbidities developed (you can select multiple):**")
    
    # Create checkboxes in a grid layout
    comorbidities_developed = []
    other_comorbidity = None
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.checkbox("Diabetes", key="followup_diabetes"):
            comorbidities_developed.append("Diabetes")
    
    with col2:
        if st.checkbox("Hypertension", key="followup_hypertension"):
            comorbidities_developed.append("Hypertension")
    
    with col3:
        if st.checkbox("HIV", key="followup_hiv"):
            comorbidities_developed.append("HIV")
    
    with col4:
        if st.checkbox("None captured", key="followup_none_captured"):
            comorbidities_developed.append("None captured")
    
    with col5:
        if st.checkbox("Other", key="followup_other_comorbidity"):
            comorbidities_developed.append("Other")
            other_comorbidity = st.text_input(
                "Specify other comorbidity:",
                placeholder="Specify the other comorbidity...",
                help="Enter details about the other comorbidity"
            )
    
    # Breast cancer recurrence
    st.markdown("**Has the patient developed breast cancer recurrence?**")
    recurrence = st.radio(
        "Breast Cancer Recurrence",
        options=["No", "Yes"],
        index=None,
        help="Select whether breast cancer recurrence was detected"
    )
    
    # Conditional: Recurrence date
    recurrence_date = None
    if recurrence == "Yes":
        st.markdown("**If Yes, on what date was the recurrence confirmed?**")
        recurrence_date = st.date_input(
            "Recurrence Confirmation Date",
            value=date.today(),
            min_value=Config.STUDY_START_DATE,
            max_value=Config.STUDY_END_DATE,
            help="Select the date when recurrence was confirmed"
        )
    
    # Patient status
    st.markdown("**Is the patient still alive at last follow-up?**")
    patient_status = st.radio(
        "Patient Status",
        options=["Alive", "Deceased"],
        index=None,
        help="Select the patient's vital status at last follow-up"
    )
    
    # Conditional: Death details
    death_date = None
    death_cause = None
    if patient_status == "Deceased":
        st.markdown("**Date of death if the patient passed away:**")
        death_date = st.date_input(
            "Date of Death",
            value=date.today(),
            min_value=Config.STUDY_START_DATE,
            max_value=Config.STUDY_END_DATE,
            help="Select the date when the patient passed away"
        )
        
        st.markdown("**Primary cause of death:**")
        death_cause = st.text_area(
            "Primary Cause of Death",
            placeholder="Describe the primary cause of death...",
            help="Enter the primary cause of death"
        )
    
    # Return final follow-up data
    return {
        "patient_id": patient_id,
        "last_review_date": last_review_date.strftime("%Y-%m-%d"),
        "general_condition": general_condition,
        "followup_attendance": followup_attendance,
        "no_followup_reason": no_followup_reason,
        "comorbidities_developed": comorbidities_developed,
        "other_comorbidity": other_comorbidity,
        "recurrence": recurrence,
        "recurrence_date": recurrence_date.strftime("%Y-%m-%d") if recurrence_date else None,
        "patient_status": patient_status,
        "death_date": death_date.strftime("%Y-%m-%d") if death_date else None,
        "death_cause": death_cause
    }


# ========================================================================================
# UI COMPONENTS
# ========================================================================================

def render_page_header() -> None:
    """Render the main page header and description"""
    st.set_page_config(page_title="Breast Cancer Data Collection", layout="centered")
    st.title("Data Capture Tool for Analysis of Adherence Patterns to Chemotherapy")
    st.markdown("---")

def render_data_storage_config() -> None:
    """Render data storage configuration in sidebar"""
    with st.sidebar:
        st.header("Settings")
        data_dir = st.text_input(
            "Data Storage Directory",
            value=st.session_state.data_directory,
            help="Enter the path where you want to store the data files"
        )
        if data_dir != st.session_state.data_directory:
            st.session_state.data_directory = data_dir
        
        st.markdown("---")
        st.markdown("**Quick Stats**")
        if os.path.exists(st.session_state.data_directory):
            try:
                patient_folders = [d for d in os.listdir(st.session_state.data_directory) 
                                 if d.startswith('patient_') and os.path.isdir(os.path.join(st.session_state.data_directory, d))]
                st.metric("Patients Recorded", len(patient_folders))
            except:
                st.metric("Patients Recorded", "0")
        else:
            st.metric("Patients Recorded", "0")


def render_linear_baseline_form(districts: List[str]) -> Dict:
    """Render the linear baseline form following exact PDF numbering"""
    st.header("Section 1: Baseline Data (Collected at First Visit Only)")
    st.markdown("---")
    
    # 1. Patient ID
    patient_id = st.text_input(
        "1. Patient ID:",
        help="Enter unique patient identifier",
        key="patient_id",
        placeholder="e.g., WMJ11"
    )
    
    # 2. Age and Date Admitted (on same line conceptually but separate inputs)
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input(
            "2. Age (years):",
            min_value=0,
            max_value=120,
            step=1,
            key="age_input"
        )
    
    with col2:
        date_admitted = st.date_input(
            "Date Admitted:",
            value=date(2017, 1, 1),
            min_value=Config.STUDY_START_DATE,
            max_value=Config.STUDY_END_DATE,
            key="date_admitted",
            help="Select date between 2016-2025"
        )
    
    # 3. Education Level
    st.markdown("**3. Highest level of education:**")
    education_level = st.radio(
        "Select education level:",
        Config.EDUCATION_OPTIONS,
        key="education_level",
        horizontal=True,
        label_visibility="collapsed",
        index=None  # No default selection
    )
    
    # 4. Marital Status  
    st.markdown("**4. Current marital status:**")
    marital_status = st.radio(
        "Select marital status:",
        Config.MARITAL_OPTIONS,
        key="marital_status",
        horizontal=True,
        label_visibility="collapsed",
        index=None  # No default selection
    )
    
    # 5. Income Source
    st.markdown("**5. Main source of income:**")
    income_source = st.radio(
        "Select income source:",
        Config.INCOME_OPTIONS,
        key="income_source",
        horizontal=True,
        label_visibility="collapsed",
        index=None  # No default selection
    )
    
    # Conditional input for "Other" income source
    income_other = ""
    if income_source == "Other":
        income_other = st.text_input(
            "Specify other source of income:",
            key="income_other",
            placeholder="Please specify..."
        )
    
    # 6. District of residence
    district_options = ["-- Select District --"] + districts
    district = st.selectbox(
        "6. District of residence:",
        options=district_options,
        key="district",
        help=f"Select from {len(districts)} Uganda districts",
        index=None  # No default selection
    )
    
    # 7. Initial diagnosis
    diagnosis_options = ["-- Select Initial Diagnosis --"] + Config.DIAGNOSIS_OPTIONS
    initial_diagnosis = st.selectbox(
        "7. Initial diagnosis:",
        diagnosis_options,
        key="initial_diagnosis",
        index=None  # No default selection
    )
    
    # 8. Immunohistochemistry results
    st.markdown("**8. Immunohistochemistry results present:**")
    immunohisto_present = st.radio(
        "Select option:",
        ["Yes", "No"],
        key="immunohisto_present",
        horizontal=True,
        label_visibility="collapsed",
        index=None  # No default selection
    )
    
    # Conditional multiselect for immunohistochemistry results
    immunohisto_results = []
    immunohisto_other = ""
    if immunohisto_present == "Yes":
        st.markdown("**Select immunohistochemistry results (you can select multiple):**")
        
        # Create checkboxes in a grid layout
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.checkbox("ER-positive (ER+)", key="er_positive"):
                immunohisto_results.append("ER-positive (ER+)")
            if st.checkbox("ER-negative (ER-)", key="er_negative"):
                immunohisto_results.append("ER-negative (ER-)")
        
        with col2:
            if st.checkbox("PR-positive (PR+)", key="pr_positive"):
                immunohisto_results.append("PR-positive (PR+)")
            if st.checkbox("PR-negative (PR-)", key="pr_negative"):
                immunohisto_results.append("PR-negative (PR-)")
            if st.checkbox("HR-positive (HR+)", key="hr_positive"):
                immunohisto_results.append("HR-positive (HR+)")
        
        with col3:
            if st.checkbox("HR-negative (HR-)", key="hr_negative"):
                immunohisto_results.append("HR-negative (HR-)")
            if st.checkbox("HER2-positive (HER2+)", key="her2_positive"):
                immunohisto_results.append("HER2-positive (HER2+)")
        
        with col4:
            if st.checkbox("HER2-negative (HER2-)", key="her2_negative"):
                immunohisto_results.append("HER2-negative (HER2-)")
            if st.checkbox("Other", key="immunohisto_other_check"):
                immunohisto_results.append("Other")
                immunohisto_other = st.text_input(
                    "Specify other results:",
                    key="immunohisto_other_specify",
                    placeholder="Please specify..."
                )
    
    # 9. Disease stage
    st.markdown("**9. Disease stage at first diagnosis:**")
    disease_stage = st.radio(
        "Select stage:",
        Config.STAGE_OPTIONS,
        key="disease_stage",
        horizontal=True,
        label_visibility="collapsed",
        index=None  # No default selection
    )
    
    # 10. Comorbidities
    st.markdown("**10. List of other comorbidities:**")
    
    # Create checkboxes in horizontal layout
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
        other_comorbidities = st.checkbox("Other", key="other_comorbidities")
    
    # Conditional input for "Other" comorbidities
    commodities_other = ""
    if other_comorbidities:
        commodities_other = st.text_input(
            "Specify other comorbidities:",
            key="commodities_other",
            placeholder="Please specify..."
        )
    
    # 11. Chemotherapy cycles prescribed
    chemo_cycles = st.number_input(
        "11. How many chemotherapy cycles have been prescribed:",
        min_value=0,
        max_value=50,
        step=1,
        key="chemo_cycles",
        help="Enter the number of prescribed cycles"
    )
    
    # 12. Regimen prescribed
    regimen_options = ["-- Select Regimen --"] + Config.REGIMEN_OPTIONS
    regimen_prescribed = st.selectbox(
        "12. Which regimen was prescribed:",
        regimen_options,
        key="regimen_prescribed",
        index=None  # No default selection
    )
    
    # 13. Treatment start status
    st.markdown("**13. Did the patient start treatment:**")
    treatment_started = st.radio(
        "Select option:",
        ["Yes", "No"],
        key="treatment_started",
        horizontal=True,
        label_visibility="collapsed",
        index=None  # No default selection
    )
    
    # Conditional input for "No" treatment start
    treatment_not_started_reason = ""
    treatment_not_started_other = ""
    if treatment_started == "No":
        st.markdown("**If No, why?**")
        reason_options = [
            "Physical toll (fear of side effects)",
            "Fear of Long-term damage", 
            "Financial / cost barriers",
            "Distance and access",
            "Late diagnosis",
            "Social / family factors",
            "Older age, existing illnesses, or weak health",
            "Other"
        ]
        
        treatment_not_started_reason = st.selectbox(
            "Select reason:",
            ["-- Select Reason --"] + reason_options,
            key="treatment_not_started_reason_select",
            index=0
        )
        
        # If "Other" is selected, show text input
        if treatment_not_started_reason == "Other":
            treatment_not_started_other = st.text_input(
                "Please specify other reason:",
                key="treatment_not_started_other",
                placeholder="Enter specific reason..."
            )
    
    # Return all collected data
    return {
        "patient_id": patient_id,
        "age": age,
        "date_admitted": date_admitted.strftime("%Y-%m-%d"),
        "education_level": education_level,
        "marital_status": marital_status,
        "income_source": income_source,
        "income_other": income_other if income_source == "Other" else None,
        "district": district if district and not district.startswith("-- Select") else None,
        "initial_diagnosis": initial_diagnosis if initial_diagnosis and not initial_diagnosis.startswith("-- Select") else None,
        "immunohisto_present": immunohisto_present,
        "immunohisto_results": immunohisto_results if immunohisto_present == "Yes" else [],
        "immunohisto_other": immunohisto_other if "Other" in immunohisto_results else None,
        "disease_stage": disease_stage,
        "comorbidities": {
            "diabetes": diabetes,
            "hypertension": hypertension,
            "hiv": hiv,
            "none_captured": none_captured,
            "other": other_comorbidities,
            "other_specify": commodities_other if other_comorbidities else None
        },
        "chemo_cycles_prescribed": chemo_cycles,
        "regimen_prescribed": regimen_prescribed if regimen_prescribed and not regimen_prescribed.startswith("-- Select") else None,
        "treatment_started": treatment_started,
        "treatment_not_started_reason": treatment_not_started_reason if treatment_started == "No" and not treatment_not_started_reason.startswith("-- Select") else None,
        "treatment_not_started_other": treatment_not_started_other if treatment_not_started_reason == "Other" else None
    }


def render_cycle_actions(cycle_data, cycle_number):
    """Render action buttons for cycle forms"""
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if st.button("Save Cycle", type="primary", use_container_width=True):
            if validate_cycle_data(cycle_data):
                # Save cycle data
                success, result = save_patient_data(cycle_data, data_type='cycle')
                if success:
                    st.success(f"Treatment Cycle {cycle_number} data saved successfully!")
                    # Reset current cycle to go back to cycle management
                    st.session_state.current_cycle = 0
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"Failed to save cycle data: {result}")
            else:
                st.error("Please fill in all required fields before saving.")
    
    with col2:
        if st.button("Cancel Cycle", use_container_width=True):
            st.session_state.current_cycle = 0
            st.rerun()
    
    with col3:
        if st.button("Clear", help="Clear form", use_container_width=True):
            clear_form_fields()
            st.rerun()


def validate_cycle_data(cycle_data):
    """Validate cycle form data"""
    if not cycle_data:
        return False
    
    # Check required fields for cycle 1
    required_fields = ['regimen_prescribed', 'prescription_date']
    
    for field in required_fields:
        if field not in cycle_data or not cycle_data[field]:
            return False
    
    # Validate medications
    medications = cycle_data.get('medications', [])
    if not medications:
        return False
    
    for med in medications:
        if not med.get('name') or not med.get('dose'):
            return False
    
    return True


def render_final_followup_actions(followup_data):
    """Render action buttons for final follow-up form"""
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if st.button("Save Complete Record", type="primary", use_container_width=True):
            if validate_final_followup_data(followup_data):
                # Save final follow-up data
                success, result = save_patient_data(followup_data, data_type='final_followup')
                if success:
                    st.success("Complete patient record saved successfully!")
                    st.balloons()
                    # Reset all session state for new patient
                    st.session_state.baseline_completed = False
                    st.session_state.current_patient_id = None
                    st.session_state.current_cycle = 0
                    st.session_state.show_final_followup = False
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(f"Failed to save final follow-up data: {result}")
            else:
                st.error("Please fill in all required fields before saving.")
    
    with col2:
        if st.button("Back to Cycles", use_container_width=True):
            st.session_state.show_final_followup = False
            st.rerun()
    
    with col3:
        if st.button("Clear", help="Clear form", use_container_width=True):
            # Clear final follow-up form fields
            st.rerun()


def validate_final_followup_data(followup_data):
    """Validate final follow-up form data"""
    if not followup_data:
        return False
    
    # Check required fields
    required_fields = ['last_review_date', 'general_condition', 'followup_attendance', 'patient_status']
    
    for field in required_fields:
        if field not in followup_data or not followup_data[field]:
            return False
    
    # Additional validation for conditional fields
    if followup_data.get('followup_attendance') == 'No' and not followup_data.get('no_followup_reason'):
        return False
    
    if followup_data.get('recurrence') == 'Yes' and not followup_data.get('recurrence_date'):
        return False
    
    if followup_data.get('patient_status') == 'Deceased':
        if not followup_data.get('death_date') or not followup_data.get('death_cause'):
            return False
    
    return True


def render_form_actions(form_data: Dict) -> None:
    """Render form submission and action buttons"""
    st.markdown("---")
    
    # Check if treatment was started
    treatment_started = form_data.get("treatment_started")
    
    if treatment_started == "No":
        # Patient did not start treatment - show end option
        st.warning("Patient did not start treatment. Data collection will be completed and saved.")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if st.button("Save Baseline & End Data Collection", type="primary", use_container_width=True):
                # Validate form data
                error_msg = validate_form_data(form_data)
                
                if error_msg:
                    st.error(f"{error_msg}")
                else:
                    # Save data
                    success, result = save_patient_data(form_data, "baseline")
                    
                    if success:
                        st.success(f"Baseline data for Patient {form_data['patient_id']} saved successfully!")
                        st.success(f"File saved to: {result}")
                        st.info(f"Patient {form_data['patient_id']} - Treatment did not start. Data collection complete.")
                        
                        # Show success metrics
                        with st.expander("Saved Data Summary", expanded=True):
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.metric("Patient ID", form_data['patient_id'])
                                st.metric("Age", form_data['age'])
                                st.metric("District", form_data['district'] or "Not selected")
                            with col_b:
                                st.metric("Education", form_data['education_level'] or "Not selected")
                                st.metric("Diagnosis", form_data['initial_diagnosis'] or "Not selected")
                                st.metric("Treatment Status", "Not Started")
                        
                        # Reset session state to start new patient
                        st.session_state.baseline_completed = False
                        st.session_state.current_patient_id = None
                        st.session_state.current_cycle = 0
                        st.session_state.show_final_followup = False
                        clear_form_fields()
                        
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"Error saving data: {result}")
        
        with col2:
            if st.button("Clear Form", use_container_width=True):
                clear_form_fields()
                st.rerun()
    
    else:
        # Treatment started or not selected yet - show normal continue option
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if st.button("Save Baseline Data & Continue", type="primary", use_container_width=True):
                # Validate form data
                error_msg = validate_form_data(form_data)
                
                if error_msg:
                    st.error(f"{error_msg}")
                else:
                    # Save data
                    success, result = save_patient_data(form_data, "baseline")
                    
                    if success:
                        st.success(f"Baseline data for Patient {form_data['patient_id']} saved successfully!")
                        st.success(f"File saved to: {result}")
                        
                        # Update session state
                        st.session_state.patient_data = form_data
                        st.session_state.current_patient_id = form_data['patient_id']
                        st.session_state.baseline_completed = True
                        st.session_state.current_cycle = 0
                        
                        # Show success metrics
                        with st.expander("Saved Data Summary", expanded=True):
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.metric("Patient ID", form_data['patient_id'])
                                st.metric("Age", form_data['age'])
                                st.metric("District", form_data['district'] or "Not selected")
                            with col_b:
                                st.metric("Education", form_data['education_level'] or "Not selected")
                                st.metric("Diagnosis", form_data['initial_diagnosis'] or "Not selected")
                                st.metric("Stage", form_data['disease_stage'] or "Not selected")
                        
                        st.rerun()  # Refresh to show cycle options
                    else:
                        st.error(f"Error saving data: {result}")
        
        with col2:
            if st.button("Clear Form", use_container_width=True):
                clear_form_fields()
                st.rerun()


def render_footer() -> None:
    """Render application footer"""
    st.markdown("---")
    st.info(" **Note**: Please ensure all information is accurate before submission. Use 'Not captured' for missing information. Data will be exported to Excel/CSV for analysis.")


# ========================================================================================
# MAIN APPLICATION
# ========================================================================================

def main():
    """Main application function"""
    # Initialize session state
    initialize_session_state()
    
    # Render page header
    render_page_header()
    
    # Render sidebar configuration
    render_data_storage_config()
    
    # Load districts data
    uganda_districts = load_uganda_districts()
    
    # Check if baseline is completed
    if not st.session_state.baseline_completed:
        # Show baseline form
        form_data = render_linear_baseline_form(uganda_districts)
        render_form_actions(form_data)
    else:
        # Baseline completed - show cycle management
        st.success(f"Baseline data completed for Patient {st.session_state.current_patient_id}")
        
        # Load patient data to check existing cycles
        patient_data = load_patient_data(st.session_state.current_patient_id)
        existing_cycles = len(patient_data.get("treatment_cycles", []))
        
        st.markdown("---")
        st.subheader("Treatment Cycles Management")
        
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            st.metric("Patient ID", st.session_state.current_patient_id)
        with col2:
            st.metric("Completed Cycles", existing_cycles)
        with col3:
            if st.button("New Patient", help="Start with a new patient"):
                # Reset session state
                st.session_state.baseline_completed = False
                st.session_state.current_patient_id = None
                st.session_state.current_cycle = 0
                st.session_state.show_final_followup = False
                clear_form_fields()
                st.rerun()
        
        # Show cycle addition buttons
        next_cycle = existing_cycles + 1
        
        if next_cycle == 1:
            st.markdown("### Ready to add Treatment Cycle 1")
            if st.button(f"Add Treatment Cycle 1", type="primary", use_container_width=True):
                st.session_state.current_cycle = 1
                st.rerun()
        else:
            st.markdown(f"### Ready to add Treatment Cycle {next_cycle}")
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button(f"Add Treatment Cycle {next_cycle}", type="primary", use_container_width=True):
                    st.session_state.current_cycle = next_cycle
                    st.rerun()
            with col_b:
                if st.button("Final Follow-Up Visit", use_container_width=True):
                    st.session_state.show_final_followup = True
                    st.session_state.current_cycle = 0
                    st.rerun()
        
        # Show cycle form if current_cycle is set
        if st.session_state.current_cycle > 0:
            cycle_data = render_cycle_form(st.session_state.current_patient_id, st.session_state.current_cycle)
            render_cycle_actions(cycle_data, st.session_state.current_cycle)
    
    # Show final follow-up form if requested
    if st.session_state.show_final_followup:
        final_followup_data = render_final_followup_form(st.session_state.current_patient_id)
        render_final_followup_actions(final_followup_data)
    
    # Footer
    render_footer()


if __name__ == "__main__":
    main()