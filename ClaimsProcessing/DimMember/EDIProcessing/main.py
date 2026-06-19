import os
import sys
import shutil
from pathlib import Path
import json
import logging
from datetime import datetime

# Setup workspace environment paths
file_dir = Path(os.getcwd())
root_dir = file_dir.parent.parent
print("root directory: ", root_dir)

sys.path.append(str(root_dir))

from Shared.EDIProcessing import EDIProcessor, CSVConverter
from DimMember.EDIProcessing.mapper import Mapper

def process_single_file(pending_file, base_source_dir):
    inprogress_dir  = base_source_dir / "inprogress"
    processed_dir   = base_source_dir / "processed"
    failed_dir      = base_source_dir / "failed"
    
    # Active file reference tracker
    active_file = pending_file

    try:
        # 1. Verification Step
        if not active_file.exists():
            raise FileNotFoundError(f"Input file not found in pending: {active_file}")
        
        # 2. Transition: Pending -> Inprogress
        os.makedirs(inprogress_dir, exist_ok=True)
        inprogress_file = inprogress_dir / active_file.name
        print(f"\nMoving file to execution phase: {inprogress_file}")
        shutil.move(str(active_file), str(inprogress_file))
        active_file = inprogress_file  # Update pointer to current location

        # 3. Sequential Ingestion Pipeline Execution
        structured_json = EDIProcessor().parse(str(active_file))
        mapper_data = Mapper().map_member(structured_json)
        
        # 4. Destination Directory Creation & Delivery (CSV)
        # Dynamically name output CSV based on the input file name
        output_file = root_dir / f"temp/834/{active_file.stem}.csv"
        os.makedirs(output_file.parent, exist_ok=True)
        CSVConverter().converter(mapper_data, str(output_file))
        print(f"Pipeline execution logic completed successfully for {active_file.name}!")
        
        # 5. Transition: Inprogress -> Processed
        os.makedirs(processed_dir, exist_ok=True)
        processed_file = processed_dir / active_file.name
        print(f"Moving file to completion phase: {processed_file}")
        shutil.move(str(active_file), str(processed_file))
        
    except Exception as e:
        print(f"Execution failed for {active_file.name} due to: {e}")
        
        # 6. Transition: Inprogress -> Failed
        if active_file.exists():
            os.makedirs(failed_dir, exist_ok=True)
            failed_file_path = failed_dir / active_file.name
            print(f"Moving file to failure directory: {failed_file_path}")
            shutil.move(str(active_file), str(failed_file_path))
        else:
            print(f"Cannot move file to failed - it does not exist at: {active_file}")

def main():
    base_source_dir = root_dir / "source/834"
    pending_dir = base_source_dir / "pending"
    
    if not pending_dir.exists():
        print(f"Pending directory does not exist at: {pending_dir}")
        return

    # Find all items in the pending folder
    all_items = list(pending_dir.iterdir())
    
    # Filter to process only files (ignoring sub-folders or hidden files)
    pending_files = [f for f in all_items if f.is_file() and not f.name.startswith('.')]
    
    if not pending_files:
        print("No files found in the pending directory to process.")
        return
        
    print(f"Found {len(pending_files)} file(s) to process.")

    # Loop through each file dynamically
    for file_path in pending_files:
        process_single_file(file_path, base_source_dir)

if __name__ == "__main__":
    main()