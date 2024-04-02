import os
import re
import yaml
import argparse




# Function to parse a single schema file
def parse_schema_file(file_path):
    # Mapping from PySpark data types to your YAML format data types
    data_type_mapping = {
        'string': 'StringType',
        'integer': 'IntegerType',
        'long': 'LongType',
        'short': 'ShortType',
        'decimal': 'DecimalType',
        'date': 'DateType',
        'timestamp': 'TimeStampType',
    }
    with open(file_path, 'r') as file:
        schema_lines = file.readlines()

    columns = []
    for line in schema_lines:
        match = re.match(r'\|\-\-\s(\w+):\s(\w+)\s\(nullable\s=\s(\w+)\)', line.strip())
        if match:
            column_name, raw_data_type, nullable_status = match.groups()
            data_type = data_type_mapping.get(raw_data_type.lower(), 'StringType')
            print(data_type)
            if data_type == 'StringType':
                columns.append({
                    'name': column_name,
                    'data_type': data_type,
                    'constraint_length': 5,
                    'constraint_nulls':0,
                    'constraint_nullable': nullable_status == 'true',
                    'constraint_constants': [],
                    'constraint_distinct': False,
                    'constraint_special_chars':[]
                })
            elif data_type in ['IntegerType', 'LongType', 'ShortType']:
                columns.append({
                    'name': column_name,
                    'data_type': data_type,
                    'constraint_nulls':0,
                    'constraint_nullable': nullable_status == 'true',
                    'constraint_range': [1,100],
                    'constraint_distinct': False,
                    'constraint_constants':[]
                })
            elif data_type == 'DecimalType':
                columns.append({
                    'name': column_name,
                    'data_type': data_type,
                    'constraint_nulls':0,
                    'constraint_nullable': nullable_status == 'true',
                    'constraint_decimal_range': [10,2],
                    'constraint_range': [1.00,100.00],
                    'constraint_distinct': False,
                    'constraint_constants':[]
                })
            elif data_type == 'DateType':
                columns.append({
                    'name': column_name,
                    'data_type': data_type,
                    'constraint_nulls':0,
                    'constraint_nullable': nullable_status == 'false',
                    'constraint_range': ['1800-01-01','2024-01-01'],
                    'constraint_distinct': False,
                    'constraint_constants':[]
                })
            elif data_type == 'TimeStampType':
                columns.append({
                    'name': column_name,
                    'data_type': data_type,
                    'constraint_nulls':0,
                    'constraint_nullable': nullable_status == 'true',
                    'constraint_range': ['1800-01-01 00:00:00:00000','2024-01-01 00:00:00:00000'],
                    'constraint_distinct': False,
                    'constraint_constants':[]
                })
    return columns

def generate_yaml(schema_directory:str, target_directory):
    output_file_name = 'all_tables.yaml'
    all_tables = {}
    # Main processing loop
    for filename in os.listdir(schema_directory):
        if filename.endswith('.txt'):
            table_name = filename[:-4]  # Removing the '.txt' extension
            file_path = os.path.join(schema_directory, filename)
            
            columns = parse_schema_file(file_path)
            all_tables[table_name] = {
                'rows': 1000,
                'save_to_local': [False , {'local_location': ''}],
                'save_to_databricks': [False ,{'databricks_table': ''}],
                'columns': columns
            }

    # Combine all tables into the final YAML structure
    yaml_content = {
        'seed': 1209,
        'tables': all_tables
    }

    # Write the combined YAML content to a file
    output_file_path = os.path.join(target_directory, output_file_name)
    with open(output_file_path, 'w') as yaml_file:
        yaml.dump(yaml_content, yaml_file, sort_keys=False, default_flow_style=False)

    print("Combined YAML file generated successfully.")

if __name__=="__main__":
    parser = argparse.ArgumentParser(prog = "Yaml Config Generator")

    parser.add_argument('-sd', '--schema_directory', required=True, help="The Directory where we have ketp the spark schema in txt files.")
    parser.add_argument('-t', '--target', required=True, help="The directory where we want to save the Ymal File to.")

    args = parser.parse_args()

    generate_yaml(schema_directory=args.schema_directory,
                  target_directory=args.target)
