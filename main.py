from input_interpreter import extract_swagger_details
from data_mapping_agent import load_csv_tables, map_params_to_data

# Test with different Swagger URLs
swagger_url = "https://fakerestapi.azurewebsites.net/swagger/v1/swagger.json"
# swagger_url = "https://petstore.swagger.io/v2/swagger.json"

endpoints, swagger_params = extract_swagger_details(swagger_url)

print("\n📡 Extracted Endpoints:")
for e in endpoints:
    print(e)

print("\n🔍 Swagger Parameters:")
for p in swagger_params:
    print("-", p)

tables = load_csv_tables()

print("\n📄 Loaded CSV Tables:")
for t in tables:
    print(f"- {t}: Columns → {tables[t].columns.tolist()}")

mapped_params, used_table, sample_row = map_params_to_data(swagger_params, tables)

print("\n🔗 Mapped Parameters:")
print(mapped_params)

print("\n📊 Used Table:", used_table)
print("📄 Sample Row:", sample_row)


from jmeter_generator import generate_jmeter_testplan

# 👇 Choose one meaningful endpoint to test generation
endpoint_to_test = "POST /api/v1/Books"
method = "POST"

generate_jmeter_testplan(
    endpoint=endpoint_to_test,
    method=method,
    param_mapping=mapped_params,
    csv_filename="books.csv"
)
