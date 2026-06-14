from pyedi import X12Parser

class Parser:
    def __init__(self):
        self.parser = X12Parser()

    def parse(self, file_path: str):
        with open(file_path, "r") as file:
            edi_data = file.read()

        generic_json = self.parser.parse(edi_data)

        return generic_json