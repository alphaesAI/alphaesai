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
    try:
        # 1. Verification Step
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        # 2. Sequential Ingestion Pipeline
        structured_json = EDIProcessor().parse(str(input_file))
        mapper_data = Mapper().map_member(structured_json)
        
        # 3. Destination Directory Creation & Delivery
        os.makedirs(output_file.parent, exist_ok=True)
        CSVConverter().converter(mapper_data, str(output_file))
        print("Pipeline executed successfully!")
        
    except Exception as e:
        print(f"Execution failed due to: {e}")
        
        # Dynamically build destination matching the source dimension folder context
        failed_dir = input_file.parent.parent / "failed"
        failed_file_path = failed_dir / input_file.name
        
        if input_file.exists():
            os.makedirs(failed_dir, exist_ok=True)
            print(f"Moving file to failure directory: {failed_file_path}")
            shutil.move(str(input_file), str(failed_file_path))
        else:
            print(f"Cannot move file - it doesn't exist: {input_file}")
        
        # Re-raise the exception for clean downstream monitoring/alert tracking
        raise e

if __name__ == "__main__":
    # Pointing directly to your clean workspace folder structure paths
    input_file = root_dir / "source/834/pending/member.txt"
    output_file = root_dir / "temp/834/834member.csv"
    main()