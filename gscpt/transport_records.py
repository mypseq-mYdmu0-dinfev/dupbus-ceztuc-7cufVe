#!/usr/bin/env python3
"""
Transportation Records Processor
Processes Opal Card CSV files into standardised format for financial records
"""

import pandas as pd
import os
from datetime import datetime
import glob

def process_transport_records():
    """Process contactless payment CSV files into standardised format"""
    
    # Define paths: this script's own directory inside the repo.
    input_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Find the most recent Contactless Payment CSV file
    pattern = os.path.join(input_dir, 'Contactless Payment*.csv')
    csv_files = glob.glob(pattern)
    
    if not csv_files:
        print("No 'Contactless Payment' CSV files found in the directory.")
        return
    
    # Get the most recent file
    input_file = max(csv_files, key=os.path.getctime)
    print(f"Processing: {os.path.basename(input_file)}")
    
    try:
        # Read the CSV file
        df = pd.read_csv(input_file, encoding='utf-8')
        
        # Verify this is a transportation CSV by checking for Card Details column
        if 'Card Details' not in df.columns:
            print("Error: Not a valid transportation CSV (missing 'Card Details' column)")
            return
            
        print(f"Found {len(df)} records")
        
        # Process each record
        processed_records = []
        
        for _, record in df.iterrows():
            # Transform date from DD/MM/YYYY to YYYY-MM-DD
            date_parts = record['Date'].split('/')
            day, month, year = date_parts[0], date_parts[1], date_parts[2]
            formatted_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            
            # Create datetime for note (YYYYMMDDHHMM)
            time_parts = record['Time'].split(':')
            hour, minute = time_parts[0], time_parts[1]
            datetime_code = f"{year}{month.zfill(2)}{day.zfill(2)}{hour}{minute}"
            
            # Create note: "[Mode] from [Details] YYYYMMDDHHMM"
            # Capitalise Light rail to Light Rail
            mode = record['Mode'].replace('Light rail', 'Light Rail')
            note = f"{mode} from {record['Details']} {datetime_code}"
            
            # Process amount: remove $ and replace 0.00 with 0.01
            amount = record['Amount'].replace('$', '')
            if amount == '0.00':
                amount = '0.01'
            
            processed_records.append({
                'Date': formatted_date,
                'Payee': 'Transport for NSW',
                'Note': note,
                'Amount': amount
            })
        
        # Create output DataFrame
        output_df = pd.DataFrame(processed_records)
        
        # Verification
        original_sum = df['Amount'].str.replace('$', '').astype(float).sum()
        processed_sum = output_df['Amount'].astype(float).sum()
        zero_count = (df['Amount'] == '$0.00').sum()
        
        print(f"Original sum: ${original_sum:.2f}")
        print(f"Processed sum: ${processed_sum:.2f}")
        print(f"Zero amount records converted: {zero_count}")
        
        # Verify the conversion is correct
        expected_difference = zero_count * 0.01
        actual_difference = processed_sum - original_sum
        
        if abs(actual_difference - expected_difference) < 0.001:
            print("✓ Verification passed")
        else:
            print("✗ Verification failed - amounts don't match")
            return
        
        # Generate output filename with current timestamp
        current_time = datetime.now().strftime('%Y%m%d%H%M')
        output_filename = f"Transport Records {current_time}.csv"
        output_path = os.path.join(input_dir, output_filename)
        
        # Save to CSV
        output_df.to_csv(output_path, index=False, encoding='utf-8')
        
        print(f"✓ Output saved: {output_filename}")
        print(f"✓ {len(processed_records)} records processed successfully")
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    process_transport_records()