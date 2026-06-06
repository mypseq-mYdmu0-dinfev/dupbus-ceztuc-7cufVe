"""
Battery Logs Processor

Reads .txt files (except temp.txt) in this directory and consolidates them
into one timestamped CSV (columns: HH, mm, %, Remarks).

USAGE
-----
1. In THIS script's own directory, place one or more .txt files.
   Each file holds lines of battery readings; a line of exactly 8 digits is
   kept verbatim as a date marker, blank lines are preserved, and a `%` on a
   line separates the numeric reading from an optional remark.
2. Run:  python3 battery_logs.py
3. Output CSV is written beside this script as `Battery Logs [timestamp].csv`
   (timestamp = current local time, YYYYMMDDHHmm).

If no numerical data is found, no output file is created.
"""

import os
import re
from datetime import datetime

def process_and_export_files(directory_path):
    """
    Finds all .txt files in a directory, processes them, and exports to a single .csv.

    Args:
        directory_path (str): The absolute path to the directory containing .txt files.
    """
    # Check if the provided path is a valid directory
    if not os.path.isdir(directory_path):
        print(f"Error: The directory '{directory_path}' does not exist.")
        print("Please make sure the drive is connected and the path is correct.")
        return

    # Generate a timestamp for the output file
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    output_filename = f"Battery Logs {timestamp}.csv"
    output_filepath = os.path.join(directory_path, output_filename)

    total_processed_lines = 0

    try:
        # Open the single output file to write all processed data into
        with open(output_filepath, 'w', newline='', encoding='utf-8') as outfile:
            # Add the column headers to the CSV file
            outfile.write("HH,mm,%,Remarks\n")

            # Iterate over all files in the specified directory
            for filename in os.listdir(directory_path):
                # Process only files with a .txt extension
                if filename.endswith(".txt"):
                    input_filepath = os.path.join(directory_path, filename)
                    
                    print(f"Processing '{input_filepath}'...")

                    try:
                        # Open the input file
                        with open(input_filepath, 'r', encoding='utf-8') as infile:
                            # Read the input file line by line
                            for line in infile:
                                # Preserve blank lines
                                stripped_line = line.strip()
                                if not stripped_line:
                                    outfile.write('\n')
                                    continue
                                
                                # Check for timestamp (8 consecutive digits only)
                                if re.match(r'^\d{8}$', stripped_line):
                                    outfile.write(stripped_line + '\n')
                                    continue
                                
                                # Process normal lines
                                numerical_part = line
                                remark = ""

                                # Separate the line into numerical part and remarks based on '%'
                                if '%' in line:
                                    parts = line.split('%', 1)
                                    numerical_part = parts[0]
                                    # Clean up the remark: remove parentheses, commas, and extra spaces
                                    remark = parts[1].replace('(', '').replace(')', '').replace(',', '').strip()

                                # 1, 2, 3: Neglect spaces, signs, and non-numerical text from the numerical part
                                only_digits = re.sub(r'[^0-9]', '', numerical_part)

                                # Continue only if there are digits left
                                if only_digits:
                                    # Check if this is a 100% case
                                    if '100%' in line:
                                        # Special handling for 100%: keep last 3 digits together
                                        if len(only_digits) >= 3:
                                            # Split: first (len-3) digits in 2-digit chunks, then last 3 digits
                                            prefix_length = len(only_digits) - 3
                                            two_digit_chunks = []
                                            
                                            for i in range(0, prefix_length, 2):
                                                two_digit_chunks.append(only_digits[i:i+2])
                                            
                                            # Add the last 3 digits as one chunk
                                            two_digit_chunks.append(only_digits[-3:])
                                            
                                            # Prepare the columns for the CSV line
                                            csv_parts = two_digit_chunks
                                            if remark:
                                                csv_parts.append(remark)
                                            
                                            # Join the parts with a comma to create the CSV line
                                            csv_line = ",".join(csv_parts)
                                            
                                            # Write the formatted line to the output file
                                            outfile.write(csv_line + '\n')
                                            total_processed_lines += 1
                                    else:
                                        # Normal 2-digit chunking
                                        two_digit_chunks = [only_digits[i:i+2] for i in range(0, len(only_digits), 2)]
                                        
                                        # Prepare the columns for the CSV line
                                        csv_parts = two_digit_chunks
                                        if remark:
                                            csv_parts.append(remark)
                                        
                                        # Join the parts with a comma to create the CSV line
                                        csv_line = ",".join(csv_parts)
                                        
                                        # Write the formatted line to the output file
                                        outfile.write(csv_line + '\n')
                                        total_processed_lines += 1
                    
                    except FileNotFoundError:
                        print(f"Error: Could not find the file '{input_filepath}'")
                    except Exception as e:
                        print(f"An unexpected error occurred while processing {filename}: {e}")
        
        # After processing all files, check if we wrote any data
        if total_processed_lines > 0:
            print(f"Successfully created '{output_filepath}' with {total_processed_lines} lines.")
        else:
            # If no data was processed, remove the empty output file
            os.remove(output_filepath)
            print(f"No numerical data found in any .txt files. No output file was created.")

    except Exception as e:
        print(f"An unexpected error occurred while creating or writing to the output file: {e}")

def main():
    """
    Main function to run the script.
    """
    # The target directory: this script's own directory inside the repo.
    target_directory = os.path.dirname(os.path.abspath(__file__))
    
    process_and_export_files(target_directory)

# This makes the script executable
if __name__ == "__main__":
    main()