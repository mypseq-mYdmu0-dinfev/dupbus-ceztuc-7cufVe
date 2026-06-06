#!/usr/bin/env python3
"""
Trade Records Processor
Processes IBKR statement data CSV files into the required format
"""

import pandas as pd
import os
from datetime import datetime
import sys

# Base directory: this script's own directory inside the repo.
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

def process_transaction_csv(input_filename, output_filename=None):
    """
    Process IBKR transaction CSV file according to specified format
    
    Args:
        input_filename (str): Input CSV filename
        output_filename (str): Output CSV filename (optional, auto-generated if None)
    """
    
    # File paths
    base_path = BASE_PATH
    input_path = os.path.join(base_path, input_filename)
    
    if output_filename is None:
        # Generate output filename by adding _proc and current timestamp before .csv
        current_time = datetime.now().strftime('%Y%m%d%H%M')
        base_name = os.path.splitext(input_filename)[0]
        output_filename = f"{base_name}_proc {current_time}.csv"
    
    output_path = os.path.join(base_path, output_filename)
    
    try:
        # Read the CSV file line by line to handle varying column counts
        trades_data = []
        trades_header = None
        
        with open(input_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                if not line:
                    continue
                
                # Split the line by comma, but handle quoted fields
                import csv
                from io import StringIO
                reader = csv.reader(StringIO(line))
                try:
                    fields = next(reader)
                except:
                    continue
                
                # Check if this is a trades-related line
                if len(fields) >= 3:
                    if fields[0] == 'Trades' and fields[1] == 'Header':
                        trades_header = fields
                    elif fields[0] == 'Trades' and fields[1] == 'Data' and fields[2] == 'Order':
                        trades_data.append(fields)
        
        if not trades_data:
            print("No trade data found in the file.")
            return
        
        if not trades_header:
            print("No trades header found. Using default column mapping.")
            # Default expected columns based on the document
            symbol_col = 5
            datetime_col = 6
            quantity_col = 7
            tprice_col = 8
            comm_col = 11
        else:
            # Find column indices from header
            try:
                symbol_col = trades_header.index('Symbol')
                datetime_col = trades_header.index('Date/Time')
                quantity_col = trades_header.index('Quantity')
                tprice_col = trades_header.index('T. Price')
                comm_col = trades_header.index('Comm/Fee')
            except ValueError as e:
                print(f"Column mapping error: {e}")
                return
        
        # Process each trade record
        processed_records = []
        record_sequence = 0
        ticker_symbols = set()  # To collect unique tickers
        
        for fields in trades_data:
            if len(fields) <= max(symbol_col, datetime_col, quantity_col, tprice_col, comm_col):
                continue
            
            try:
                # Parse datetime
                datetime_str = fields[datetime_col].strip('"')
                dt = pd.to_datetime(datetime_str)
                
                # Format date and time
                date_formatted = f"'{dt.strftime('%m%d')}"
                time_formatted = f"'{dt.strftime('%H%M')}"
                
                # Determine type and process quantity
                quantity = float(fields[quantity_col])
                if quantity > 0:
                    transaction_type = 'Asset'
                    qty = int(abs(quantity))
                    commission = float(fields[comm_col])
                else:
                    transaction_type = 'Liquidation'
                    qty = int(abs(quantity))
                    commission = -float(fields[comm_col])
                
                # Process ticker and collect for list
                ticker_symbol = fields[symbol_col]
                ticker_symbols.add(ticker_symbol)
                ticker = f"{ticker_symbol} x"
                
                # Process price (4 decimal places)
                price = float(fields[tprice_col])
                price_formatted = f"{price:.4f}"
                
                # Add the main record with sequence number
                record = [
                    date_formatted,
                    time_formatted,
                    transaction_type,
                    ticker,
                    qty,
                    commission,
                    price_formatted,
                    dt,  # For sorting
                    record_sequence  # For maintaining order within same datetime
                ]
                processed_records.append(record)
                record_sequence += 1
                
                # Add PnL line after liquidation
                if transaction_type == 'Liquidation':
                    pnl_record = [
                        date_formatted,
                        time_formatted,
                        'PnL',
                        f"[{ticker_symbol}]",
                        '',
                        '',
                        '',
                        dt,  # For sorting
                        record_sequence  # Ensures PnL comes after Liquidation
                    ]
                    processed_records.append(pnl_record)
                    record_sequence += 1
                    
            except (ValueError, IndexError) as e:
                print(f"Error processing record: {e}")
                continue
        
        # Create DataFrame and sort chronologically
        columns = ['Date', 'Time', 'Type', 'Ticker', 'Qty', 'SC', 'PPS', 'datetime_sort', 'sequence']
        result_df = pd.DataFrame(processed_records, columns=columns)
        
        # Sort by datetime first, then by sequence to maintain order
        result_df = result_df.sort_values(['datetime_sort', 'sequence'])
        
        # Remove helper columns
        result_df = result_df.drop(['datetime_sort', 'sequence'], axis=1)
        
        # Save to CSV without index and header
        result_df.to_csv(output_path, index=False, header=False)
        
        # Generate ticker list file
        current_time = datetime.now().strftime('%Y%m%d%H%M')
        base_name = os.path.splitext(input_filename)[0]
        list_filename = f"{base_name}_list {current_time}.csv"
        list_path = os.path.join(base_path, list_filename)
        
        # Sort tickers alphabetically and save
        sorted_tickers = sorted(list(ticker_symbols))
        ticker_df = pd.DataFrame(sorted_tickers, columns=['Ticker'])
        ticker_df.to_csv(list_path, index=False, header=False)
        
        print(f"Processing complete!")
        print(f"Input: {input_filename}")
        print(f"Output: {output_filename}")
        print(f"Records processed: {len(trades_data)}")
        print(f"Output records: {len(result_df)}")
        
        # Display first few rows as preview
        print("\nPreview of output:")
        print(result_df.head(3).to_string(index=False))
        
    except FileNotFoundError:
        print(f"Error: Input file '{input_filename}' not found in {base_path}")
    except Exception as e:
        print(f"Error processing file: {str(e)}")

def find_latest_csv():
    """Find the most recent CSV file starting with U11885223"""
    base_path = BASE_PATH
    
    # Find all CSV files starting with U11885223, excluding processed files
    csv_files = []
    for filename in os.listdir(base_path):
        if (filename.startswith('U11885223') and 
            filename.endswith('.csv') and 
            not filename.endswith('_proc {current_time}.csv')):
            file_path = os.path.join(base_path, filename)
            mod_time = os.path.getmtime(file_path)
            csv_files.append((filename, mod_time))
    
    if not csv_files:
        raise FileNotFoundError("No CSV files starting with 'U11885223' found in the directory")
    
    # Sort by modification time (most recent first)
    csv_files.sort(key=lambda x: x[1], reverse=True)
    
    return csv_files[0][0]  # Return filename of most recent file

def main():
    """Main function to run the script"""
    
    try:
        # Automatically find the most recent CSV file
        input_filename = find_latest_csv()
        print(f"Using most recent file: {input_filename}")
        
        # Optional output filename from command line
        output_filename = sys.argv[1] if len(sys.argv) > 1 else None
        
        # Process the file
        process_transaction_csv(input_filename, output_filename)
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()