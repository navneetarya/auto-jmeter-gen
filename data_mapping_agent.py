import os
import pandas as pd
import difflib

DATA_DIR = "data"

def load_csv_tables():
    tables = {}
    if not os.path.exists(DATA_DIR):
        print(f"⚠️ Data directory '{DATA_DIR}' not found.")
        return tables

    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".csv"):
            path = os.path.join(DATA_DIR, filename)
            table_name = filename.replace(".csv", "")
            try:
                df = pd.read_csv(path)
                tables[table_name] = df
            except Exception as e:
                print(f"❌ Failed to load {filename}: {e}")
    return tables

# 🔧 This is our mocked LLM-style matching logic
def mock_llm_match(swagger_param, column_name):
    swagger_param = swagger_param.lower()
    column_name = column_name.lower()

    # Direct match
    if swagger_param == column_name:
        return 1.0

    # Similar name (like 'petId' vs 'id')
    if swagger_param in column_name or column_name in swagger_param:
        return 0.8

    # Fuzzy match using difflib
    ratio = difflib.SequenceMatcher(None, swagger_param, column_name).ratio()
    return ratio

# data_mapping_agent.py
def map_params_to_data(swagger_params, tables):
    best_score = 0
    best_table = None
    best_mapping = {}
    sample_row = None

    for table_name, df in tables.items():
        df_cols = df.columns.tolist()
        mapping = {}
        matched = 0
        for param in swagger_params:
            for col in df_cols:
                if param.lower() == col.lower():
                    mapping[param] = f"${{{col}}}"
                    matched += 1
                    break

        if matched > best_score:
            best_score = matched
            best_table = table_name
            best_mapping = mapping

    if best_table:
        sample_row = tables[best_table].iloc[0].to_dict()

    return best_mapping, best_table, sample_row

