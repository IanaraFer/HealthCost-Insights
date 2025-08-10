"""
Healthcare Billing Data Generator
Generates realistic healthcare billing data with intentional anomalies for analysis
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from faker import Faker
import warnings
warnings.filterwarnings('ignore')

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)
fake = Faker()
Faker.seed(42)

def generate_healthcare_data(num_records=50000):
    """
    Generate comprehensive healthcare billing dataset
    """
    print(f"Generating {num_records:,} healthcare billing records...")
    
    # Define realistic medical procedures and costs
    procedures = {
        'Emergency Room Visit': {'base_cost': 1200, 'variance': 400, 'frequency': 0.15},
        'Routine Checkup': {'base_cost': 250, 'variance': 50, 'frequency': 0.25},
        'Blood Test': {'base_cost': 150, 'variance': 30, 'frequency': 0.20},
        'X-Ray': {'base_cost': 300, 'variance': 75, 'frequency': 0.12},
        'MRI Scan': {'base_cost': 2500, 'variance': 500, 'frequency': 0.05},
        'CT Scan': {'base_cost': 1800, 'variance': 300, 'frequency': 0.08},
        'Surgery - Minor': {'base_cost': 5000, 'variance': 1000, 'frequency': 0.04},
        'Surgery - Major': {'base_cost': 25000, 'variance': 8000, 'frequency': 0.02},
        'Physical Therapy': {'base_cost': 180, 'variance': 40, 'frequency': 0.09}
    }
    
    # Insurance providers with different coverage rates
    insurance_providers = {
        'BlueCross BlueShield': {'coverage_rate': 0.80, 'frequency': 0.25},
        'Aetna': {'coverage_rate': 0.75, 'frequency': 0.20},
        'UnitedHealth': {'coverage_rate': 0.82, 'frequency': 0.22},
        'Cigna': {'coverage_rate': 0.78, 'frequency': 0.15},
        'Medicare': {'coverage_rate': 0.85, 'frequency': 0.10},
        'Medicaid': {'coverage_rate': 0.90, 'frequency': 0.08}
    }
    
    # Medical departments
    departments = [
        'Emergency Medicine', 'Internal Medicine', 'Cardiology', 'Orthopedics',
        'Radiology', 'Surgery', 'Pediatrics', 'Neurology', 'Oncology', 'Psychiatry'
    ]
    
    # Generate base data
    data = []
    
    for i in range(num_records):
        # Patient information
        patient_id = f"P{10000 + i:06d}"
        patient_age = np.random.normal(45, 18)
        patient_age = max(1, min(95, int(patient_age)))
        
        # Procedure selection based on frequency
        procedure_name = np.random.choice(
            list(procedures.keys()),
            p=[procedures[p]['frequency'] for p in procedures.keys()]
        )
        procedure_info = procedures[procedure_name]
        
        # Base cost calculation
        base_cost = np.random.normal(
            procedure_info['base_cost'],
            procedure_info['variance']
        )
        base_cost = max(50, base_cost)  # Minimum cost
        
        # Insurance information
        insurance_name = np.random.choice(
            list(insurance_providers.keys()),
            p=[insurance_providers[p]['frequency'] for p in insurance_providers.keys()]
        )
        coverage_rate = insurance_providers[insurance_name]['coverage_rate']
        
        # Calculate costs
        total_billed = base_cost
        insurance_paid = total_billed * coverage_rate * np.random.uniform(0.85, 1.0)
        patient_responsibility = total_billed - insurance_paid
        
        # Date range (last 2 years)
        start_date = datetime.now() - timedelta(days=730)
        service_date = start_date + timedelta(days=random.randint(0, 730))
        
        # Department
        department = random.choice(departments)
        
        # Provider information
        provider_id = f"DR{random.randint(1000, 9999)}"
        
        # Diagnosis codes (ICD-10 style)
        diagnosis_codes = [
            'Z00.00', 'I10', 'E11.9', 'M79.1', 'R53.83', 'K21.9',
            'F41.1', 'M25.511', 'N39.0', 'R50.9', 'H52.4', 'J06.9'
        ]
        primary_diagnosis = random.choice(diagnosis_codes)
        
        data.append({
            'claim_id': f"CLM{20240000 + i:08d}",
            'patient_id': patient_id,
            'patient_age': patient_age,
            'service_date': service_date.strftime('%Y-%m-%d'),
            'procedure_name': procedure_name,
            'procedure_code': f"CPT{random.randint(10000, 99999)}",
            'primary_diagnosis': primary_diagnosis,
            'department': department,
            'provider_id': provider_id,
            'insurance_provider': insurance_name,
            'total_billed_amount': round(total_billed, 2),
            'insurance_paid_amount': round(insurance_paid, 2),
            'patient_responsibility': round(patient_responsibility, 2),
            'claim_status': np.random.choice(['Paid', 'Pending', 'Denied'], p=[0.85, 0.10, 0.05]),
            'admission_type': np.random.choice(['Outpatient', 'Inpatient', 'Emergency'], p=[0.70, 0.20, 0.10]),
            'length_of_stay': random.randint(1, 15) if np.random.random() < 0.3 else 1
        })
    
    df = pd.DataFrame(data)
    
    # Introduce realistic anomalies (5% of data)
    anomaly_count = int(num_records * 0.05)
    anomaly_indices = np.random.choice(df.index, anomaly_count, replace=False)
    
    print(f"Introducing {anomaly_count:,} anomalies...")
    
    for idx in anomaly_indices:
        anomaly_type = np.random.choice([
            'billing_error', 'duplicate_claim', 'unusual_cost', 'fraud_indicator'
        ])
        
        if anomaly_type == 'billing_error':
            # Incorrect billing amounts
            df.loc[idx, 'total_billed_amount'] *= np.random.uniform(2.0, 5.0)
        
        elif anomaly_type == 'duplicate_claim':
            # Create near-duplicate claims
            if idx < len(df) - 1:
                df.loc[idx + 1, 'patient_id'] = df.loc[idx, 'patient_id']
                df.loc[idx + 1, 'procedure_name'] = df.loc[idx, 'procedure_name']
                df.loc[idx + 1, 'service_date'] = df.loc[idx, 'service_date']
        
        elif anomaly_type == 'unusual_cost':
            # Unusually high costs for routine procedures
            if 'Routine' in df.loc[idx, 'procedure_name']:
                df.loc[idx, 'total_billed_amount'] *= np.random.uniform(10.0, 20.0)
        
        elif anomaly_type == 'fraud_indicator':
            # Multiple expensive procedures same day
            df.loc[idx, 'procedure_name'] = 'Surgery - Major'
            df.loc[idx, 'total_billed_amount'] = np.random.uniform(50000, 100000)
    
    # Add calculated fields
    df['payment_rate'] = df['insurance_paid_amount'] / df['total_billed_amount']
    df['cost_per_day'] = df['total_billed_amount'] / df['length_of_stay']
    df['month_year'] = pd.to_datetime(df['service_date']).dt.to_period('M').astype(str)
    
    print("Healthcare billing data generated successfully!")
    return df

def generate_provider_data(num_providers=500):
    """
    Generate healthcare provider reference data
    """
    print(f"Generating {num_providers} provider records...")
    
    specialties = [
        'Family Medicine', 'Internal Medicine', 'Emergency Medicine', 'Cardiology',
        'Orthopedic Surgery', 'Radiology', 'Anesthesiology', 'Pediatrics',
        'Neurology', 'Oncology', 'Psychiatry', 'Dermatology'
    ]
    
    providers = []
    for i in range(num_providers):
        provider_id = f"DR{1000 + i:04d}"
        years_experience = random.randint(1, 40)
        
        providers.append({
            'provider_id': provider_id,
            'provider_name': fake.name(),
            'specialty': random.choice(specialties),
            'years_experience': years_experience,
            'medical_school': fake.company() + " Medical School",
            'board_certified': random.choice([True, False], p=[0.9, 0.1]),
            'hospital_affiliation': fake.company() + " Medical Center",
            'license_state': fake.state_abbr(),
            'npi_number': f"{random.randint(1000000000, 9999999999)}"
        })
    
    return pd.DataFrame(providers)

def main():
    """
    Main function to generate all datasets
    """
    print("=== Healthcare Billing Data Generator ===\n")
    
    # Generate main billing data
    billing_df = generate_healthcare_data(50000)
    
    # Generate provider reference data
    provider_df = generate_provider_data(500)
    
    # Save datasets
    print("\nSaving datasets...")
    
    billing_df.to_csv('healthcare_billing_data.csv', index=False)
    print(f"✓ Saved healthcare_billing_data.csv ({len(billing_df):,} records)")
    
    provider_df.to_csv('provider_reference_data.csv', index=False)
    print(f"✓ Saved provider_reference_data.csv ({len(provider_df):,} records)")
    
    # Generate summary statistics
    print("\n=== Dataset Summary ===")
    print(f"Total Claims: {len(billing_df):,}")
    print(f"Date Range: {billing_df['service_date'].min()} to {billing_df['service_date'].max()}")
    print(f"Total Billed Amount: ${billing_df['total_billed_amount'].sum():,.2f}")
    print(f"Average Claim Amount: ${billing_df['total_billed_amount'].mean():,.2f}")
    print(f"Unique Patients: {billing_df['patient_id'].nunique():,}")
    print(f"Unique Providers: {billing_df['provider_id'].nunique():,}")
    
    print("\nTop Procedures by Volume:")
    print(billing_df['procedure_name'].value_counts().head())
    
    print("\nInsurance Provider Distribution:")
    print(billing_df['insurance_provider'].value_counts())

if __name__ == "__main__":
    main()
