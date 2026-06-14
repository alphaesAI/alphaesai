import os
import sys
from pathlib import Path
import json
import logging

from datetime import datetime

file_dir = Path(os.getcwd())

root_dir = file_dir.parent.parent
print("root directory: ", root_dir)

sys.path.append(str(root_dir))

from Shared.EDIProcessing import Parser, TransactionFormatter, CSVConverter
from DimMember.EDIProcessing.mapper import Mapper

def main():
    generic_json = Parser().parse(input_file)
    # print("\n\n generic json: ", generic_json)
    
    structured_json = TransactionFormatter().format(generic_json)
    # print("\n\n structured_json: ", structured_json)

    mapper = Mapper().map_member(structured_json)
    # print("\n\n mapper: ", mapper)
    
    csv_converter = CSVConverter().converter(mapper, output_file)

if __name__ == "__main__":
    input_file = "/Volumes/claimsprocessing/source/834/834member.txt"
    output_file = "/Volumes/claimsprocessing/processed/csv_files/member_output.csv"
    main()
