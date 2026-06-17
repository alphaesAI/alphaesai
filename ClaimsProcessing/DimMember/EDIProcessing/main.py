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

def main():
    # Use the dynamic root directory instead of hardcoding
    base_source_dir = root_dir / "source/834"

    # The rest of the script works exactly the same
    pending_file    = base_source_dir / "pending/mickey.txt"
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
        print(f"Moving file to execution phase: {inprogress_file}")
        shutil.move(str(active_file), str(inprogress_file))
        active_file = inprogress_file  # Update pointer to current location

        # 3. Sequential Ingestion Pipeline Execution
        structured_json = EDIProcessor().parse(str(active_file))
        mapper_data = Mapper().map_member(structured_json)
        
        # 4. Destination Directory Creation & Delivery (CSV)
        os.makedirs(output_file.parent, exist_ok=True)
        CSVConverter().converter(mapper_data, str(output_file))
        print("Pipeline execution logic completed successfully!")
        
        # 5. Transition: Inprogress -> Processed
        os.makedirs(processed_dir, exist_ok=True)
        processed_file = processed_dir / active_file.name
        print(f"Moving file to completion phase: {processed_file}")
        shutil.move(str(active_file), str(processed_file))
        
    except Exception as e:
        print(f"Execution failed due to: {e}")
        
        # 6. Transition: Inprogress -> Failed
        if active_file.exists():
            os.makedirs(failed_dir, exist_ok=True)
            failed_file_path = failed_dir / active_file.name
            print(f"Moving file to failure directory: {failed_file_path}")
            shutil.move(str(active_file), str(failed_file_path))
        else:
            print(f"Cannot move file to failed - it does not exist at: {active_file}")
        
        raise e

if __name__ == "__main__":
    # Output CSV configuration
    output_file = root_dir / "temp/834/mickey.csv"
    main()