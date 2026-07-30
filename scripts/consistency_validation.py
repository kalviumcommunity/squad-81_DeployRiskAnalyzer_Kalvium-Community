"""
Systematic Data Consistency & Validation Rules Pipeline
Performs range checks, null constraints, format pattern validation, and business rule validation.
Isolates failing records into output/validation_failures.csv and exports clean data to data/processed/validated_customer_data.csv.

Tasks Implemented:
1. Range Checks (Age 0-150, price >= 0, birth_date between 1920 and today)
2. Null Constraints (customer_id and email not null)
3. Format Pattern Validation (email contains @, phone is 10 digits)
4. Business Rule Validation (end_date >= start_date)
5. Validation Report & Failure Isolation (passes_all_checks, validation_failures.csv, clean dataset output)
"""

import os
import sys
import pandas as pd
import numpy as np

# Ensure stdout uses UTF-8 encoding on Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def load_dataset(filepath='data/raw/customer_validation_data.csv'):
    """Loads target raw dataset or creates synthetic dataset if missing."""
    if os.path.exists(filepath):
        print(f"Loading raw dataset from '{filepath}'...")
        df = pd.read_csv(filepath)
    else:
        print(f"File '{filepath}' not found. Generating synthetic dataset with quality edge cases...")
        data = {
            'customer_id': [101, 102, 103, 104, np.nan, 106, 107, 108, 109, 110],
            'age': [32, 180, 25, 40, 29, 35, 31, 45, 27, 50],
            'birth_date': ['1992-04-15', '1985-02-10', '2050-08-20', '1984-11-05', '1995-03-12',
                          '1989-07-22', '1993-09-30', '1979-01-18', '1997-12-04', '1974-06-25'],
            'price': [150.00, 200.00, 99.99, -50.00, 120.00, 80.00, 300.00, 450.00, 175.00, 500.00],
            'email': ['john.doe@example.com', 'jane.smith@example.com', 'alex@example.com', 'sarah@example.com',
                      'mark@example.com', np.nan, 'invalidemaildomain.com', 'mike@example.com', 'lisa@example.com', 'david@example.com'],
            'phone': ['9876543210', '9876543211', '9876543212', '9876543213', '9876543214',
                      '9876543215', '9876543216', '12345', '9876543218', '9876543219'],
            'start_date': ['2024-01-01', '2024-01-01', '2024-01-01', '2024-01-01', '2024-01-01',
                           '2024-01-01', '2024-01-01', '2024-01-01', '2024-06-01', '2024-02-01'],
            'end_date': ['2024-06-30', '2024-06-30', '2024-06-30', '2024-06-30', '2024-06-30',
                         '2024-06-30', '2024-06-30', '2024-06-30', '2024-01-01', '2024-08-01']
        }
        df = pd.DataFrame(data)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        df.to_csv(filepath, index=False)
    return df


def apply_range_checks(df):
    """Task 1: Range Checks - Age (0-150), Price (>=0), Birth Date (1920 to Today)."""
    print("\n--- Task 1: Range Checks ---")
    df['valid_age'] = (df['age'] >= 0) & (df['age'] <= 150)
    df['valid_price'] = df['price'] >= 0
    
    birth_dt = pd.to_datetime(df['birth_date'], errors='coerce')
    df['valid_date'] = (birth_dt >= pd.Timestamp('1920-01-01')) & (birth_dt <= pd.Timestamp.now())

    print(f"Invalid ages (outside 0-150): {(~df['valid_age']).sum()}")
    print(f"Invalid prices (negative values): {(~df['valid_price']).sum()}")
    print(f"Invalid birth dates (future or < 1920): {(~df['valid_date']).sum()}")
    return df


def apply_null_constraints(df):
    """Task 2: Null Constraints - Critical columns customer_id and email."""
    print("\n--- Task 2: Null Constraints ---")
    df['valid_customer_id'] = df['customer_id'].notna()
    df['valid_email'] = df['email'].notna()

    print(f"Missing customer IDs: {(~df['valid_customer_id']).sum()}")
    print(f"Missing emails: {(~df['valid_email']).sum()}")
    return df


def apply_format_validation(df):
    """Task 3: Format Pattern Validation - Email regex containing @, Phone 10-digits."""
    print("\n--- Task 3: Format Pattern Validation ---")
    df['valid_email_format'] = df['email'].astype(str).str.contains('@', na=False) & df['email'].notna()
    df['valid_phone'] = df['phone'].astype(str).str.match(r'^\d{10}$', na=False)

    print(f"Invalid email formats (missing @): {(~df['valid_email_format']).sum()}")
    print(f"Invalid phone formats (not 10 digits): {(~df['valid_phone']).sum()}")
    return df


def apply_business_rules(df):
    """Task 4: Business Rule Validation - Campaign end_date >= start_date."""
    print("\n--- Task 4: Business Rule Validation ---")
    start_dt = pd.to_datetime(df['start_date'], errors='coerce')
    end_dt = pd.to_datetime(df['end_date'], errors='coerce')
    df['valid_date_order'] = (end_dt >= start_dt) & start_dt.notna() & end_dt.notna()

    print(f"Invalid date ranges (end_date < start_date): {(~df['valid_date_order']).sum()}")
    return df


def generate_validation_report(df):
    """Task 5: Validation Report & Failure Isolation."""
    print("\n--- Task 5: Validation Report & Failure Isolation ---")
    os.makedirs('output', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)

    validation_cols = [
        'valid_age', 'valid_price', 'valid_date',
        'valid_customer_id', 'valid_email', 'valid_email_format',
        'valid_phone', 'valid_date_order'
    ]

    df['passes_all_checks'] = df[validation_cols].all(axis=1)

    # Isolate failures
    failures = df[~df['passes_all_checks']]
    failures_filepath = 'output/validation_failures.csv'
    failures.to_csv(failures_filepath, index=False)

    # Report
    print(f"Records: {len(df)}")
    print(f"Passed: {df['passes_all_checks'].sum()}")
    print(f"Failed: {(~df['passes_all_checks']).sum()}")

    # Clean dataset output
    df_clean = df[df['passes_all_checks']]
    clean_filepath = 'data/processed/validated_customer_data.csv'
    df_clean.to_csv(clean_filepath, index=False)

    print(f"\n[SUCCESS] Isolated {len(failures)} failures to '{failures_filepath}'.")
    print(f"[SUCCESS] Exported {len(df_clean)} validated clean records to '{clean_filepath}'.")

    # Detailed rule-by-rule report log
    rule_summary = []
    for col in validation_cols:
        passed_count = int(df[col].sum())
        failed_count = int((~df[col]).sum())
        rule_summary.append({
            'rule_name': col,
            'passed': passed_count,
            'failed': failed_count,
            'pass_rate_pct': round((passed_count / len(df)) * 100, 2)
        })

    summary_df = pd.DataFrame(rule_summary)
    summary_filepath = 'output/validation_rule_summary.csv'
    summary_df.to_csv(summary_filepath, index=False)
    print("\nValidation Rule Summary:")
    print(summary_df.to_string(index=False))

    return df, df_clean, failures, summary_df


def main():
    print("==================================================")
    print("   DATA CONSISTENCY & VALIDATION RULES PIPELINE   ")
    print("==================================================")

    # Load dataset
    df = load_dataset()

    # Task 1: Range Checks
    df = apply_range_checks(df)

    # Task 2: Null Constraints
    df = apply_null_constraints(df)

    # Task 3: Format Pattern Validation
    df = apply_format_validation(df)

    # Task 4: Business Rule Validation
    df = apply_business_rules(df)

    # Task 5: Validation Report & Failure Isolation
    df, df_clean, failures, summary_df = generate_validation_report(df)


if __name__ == '__main__':
    main()
