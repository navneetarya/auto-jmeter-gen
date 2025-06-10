import csv
import os

class CSVLoader:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.tables = {}  # table_name -> [rows]

    def load_all(self):
        for file_name in os.listdir(self.folder_path):
            if file_name.endswith('.csv'):
                table_name = os.path.splitext(file_name)[0].lower()
                with open(os.path.join(self.folder_path, file_name), 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    self.tables[table_name] = [row for row in reader]
        return self.tables
