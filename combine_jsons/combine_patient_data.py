#!/usr/bin/env python3
"""
Script to combine patient JSON files into a single CSV/Excel file.
Handles nested structures and variable numbers of treatment cycles.
"""

import json
import pandas as pd
from pathlib import Path
import sys

def flatten_dict(d, parent_key='', sep='_'):
    """Flatten nested dictionary with separator."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list) and v and isinstance(v[0], str):
            # Handle list of strings (like side_effects, immunohisto_results)
            items.append((new_key, '; '.join(v)))
        elif isinstance(v, list):
            # Skip list of objects (will handle separately)
            pass
        else:
            items.append((new_key, v))
    return dict(items)

def process_patient_file(json_path):
    """Process a single patient JSON file and extract all data."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    patient_id = data.get('patient_id')
    
    # Flatten baseline data
    baseline = flatten_dict(data.get('baseline_data', {}), parent_key='baseline')
    
    # Flatten final followup data
    followup = flatten_dict(data.get('final_followup', {}), parent_key='followup')
    
    # Process treatment cycles
    treatment_cycles = data.get('treatment_cycles', [])
    
    rows = []
    
    if treatment_cycles:
        # Create a row for each treatment cycle
        for cycle in treatment_cycles:
            row = {
                'patient_id': patient_id,
                'source_file': json_path.name
            }
            
            # Add baseline data
            row.update(baseline)
            
            # Flatten cycle data
            cycle_data = {}
            for key, value in cycle.items():
                if key == 'medications':
                    # Handle medications list
                    med_names = []
                    med_doses = []
                    med_units = []
                    for med in value:
                        med_names.append(med.get('name', ''))
                        med_doses.append(str(med.get('dose', '')))
                        med_units.append(med.get('unit', ''))
                    cycle_data['medications_names'] = '; '.join(med_names)
                    cycle_data['medications_doses'] = '; '.join(med_doses)
                    cycle_data['medications_units'] = '; '.join(med_units)
                elif key == 'laboratory':
                    # Flatten laboratory data
                    for lab_key, lab_value in value.items():
                        cycle_data[f'lab_{lab_key}'] = lab_value
                elif key == 'side_effects' and isinstance(value, list):
                    # Handle side effects list
                    cycle_data['side_effects'] = '; '.join(value)
                else:
                    cycle_data[key] = value
            
            row.update(cycle_data)
            
            # Add followup data
            row.update(followup)
            
            rows.append(row)
    else:
        # Patient has no treatment cycles, create one row with baseline and followup
        row = {
            'patient_id': patient_id,
            'source_file': json_path.name
        }
        row.update(baseline)
        row.update(followup)
        rows.append(row)
    
    return rows

def main():
    # Get the script directory
    script_dir = Path(__file__).parent
    data_dir = script_dir / 'data'
    
    if not data_dir.exists():
        print(f"Error: Data directory not found at {data_dir}")
        sys.exit(1)
    
    print(f"Scanning for patient files in: {data_dir}")
    
    # Find all patient JSON files
    json_files = list(data_dir.glob('patient_*/patient_*.json'))
    
    if not json_files:
        print("Error: No patient JSON files found!")
        sys.exit(1)
    
    print(f"Found {len(json_files)} patient files")
    
    # Process all patient files
    all_rows = []
    errors = []
    
    for json_path in sorted(json_files):
        try:
            print(f"Processing: {json_path.name}")
            rows = process_patient_file(json_path)
            all_rows.extend(rows)
        except Exception as e:
            error_msg = f"Error processing {json_path.name}: {str(e)}"
            print(f"  ⚠️  {error_msg}")
            errors.append(error_msg)
    
    if not all_rows:
        print("Error: No data extracted from patient files!")
        sys.exit(1)
    
    # Create DataFrame
    df = pd.DataFrame(all_rows)
    
    # Sort columns: patient_id, source_file, baseline columns, cycle columns, followup columns
    cols = df.columns.tolist()
    priority_cols = ['patient_id', 'source_file']
    baseline_cols = [c for c in cols if c.startswith('baseline_')]
    cycle_cols = [c for c in cols if not c.startswith('baseline_') and not c.startswith('followup_') and c not in priority_cols]
    followup_cols = [c for c in cols if c.startswith('followup_')]
    
    ordered_cols = priority_cols + sorted(baseline_cols) + sorted(cycle_cols) + sorted(followup_cols)
    df = df[ordered_cols]
    
    # Save to CSV
    csv_output = script_dir / 'combined_patient_data.csv'
    df.to_csv(csv_output, index=False, encoding='utf-8-sig')
    print(f"\n✅ CSV file saved: {csv_output}")
    print(f"   Total rows: {len(df)}")
    print(f"   Total columns: {len(df.columns)}")
    
    # Save to Excel
    try:
        excel_output = script_dir / 'combined_patient_data.xlsx'
        df.to_excel(excel_output, index=False, engine='openpyxl')
        print(f"✅ Excel file saved: {excel_output}")
    except ImportError:
        print("⚠️  Excel export skipped (install openpyxl: pip install openpyxl)")
    
    # Print summary statistics
    print("\n📊 Summary:")
    print(f"   Unique patients: {df['patient_id'].nunique()}")
    print(f"   Treatment cycle records: {len(df)}")
    print(f"   Null values per column:")
    null_counts = df.isnull().sum()
    null_counts = null_counts[null_counts > 0].sort_values(ascending=False)
    if len(null_counts) > 0:
        for col, count in null_counts.head(10).items():
            print(f"     - {col}: {count} ({count/len(df)*100:.1f}%)")
    else:
        print("     No null values!")
    
    if errors:
        print(f"\n⚠️  {len(errors)} errors occurred during processing")
    
    print("\n✨ Done!")

if __name__ == '__main__':
    main()
