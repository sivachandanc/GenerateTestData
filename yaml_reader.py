import yaml
import pandas as pd
import random
from string import ascii_letters
import numpy as np
from datetime import datetime, timedelta

with open("/Users/sivachandanchakka/learning/GenerateTestData/all_tables.yaml", 'r') as yaml_file:
    yaml_data = yaml.safe_load(yaml_file)
    random.seed(yaml_data['seed'])
    np.random.seed(yaml_data['seed'])


def string_logic(column_name, num_rows, length, nulls, constants, distinct,special_characters, df):

    def generate_unique_string(length, existing, special_chars):
        while True:
            # Ensure at least one special character is included
            part_special = random.choice(special_chars) if special_chars else ''
            part_random = ''.join(random.choices(ascii_letters, k=length - len(part_special)))
            s = part_random + part_special
            s = ''.join(random.sample(s, len(s)))  # Shuffle to randomize the position of the special character
            if s not in existing:
                return s

    values = []

    if constants:
        values.extend(constants * (num_rows // len(constants)))
        values.extend(constants[:num_rows % len(constants)])
    else:
        existing_values = set()
        for _ in range(int(num_rows * (1 - nulls))):
            if distinct:
                s = generate_unique_string(length, existing_values, special_characters)
                existing_values.add(s)
            else:
                s = generate_unique_string(length, [], special_characters)
            values.append(s)
    
    # Adjust for null values if necessary
    if nulls > 0 and not constants:
        num_nulls = int(num_rows * nulls)
        for _ in range(num_nulls):
            values.append(np.nan)
        random.shuffle(values)

    # Ensure the column has the correct number of rows
    values = values[:num_rows]
    df[column_name] = values
    return df


def numeric_logic(column_name, num_rows, constraint_range, nulls, constants, distinct, df):
    def generate_unique_number(existing, number_range):
        while True:
            num = random.randint(*number_range)  # Generate a number within the specified range
            if num not in existing:
                return num

    values = []

    # Rule 1: Use constants if provided
    if constants:
        values.extend(constants * (num_rows // len(constants)))
        values.extend(constants[:num_rows % len(constants)])
    else:
        existing_values = set()
        for _ in range(int(num_rows * (1 - nulls))):
            if distinct:
                num = generate_unique_number(existing_values, constraint_range)
                existing_values.add(num)
            else:
                # If not distinct, just generate a random number within the range
                num = random.randint(*constraint_range)
            values.append(num)
    
    # Adjust for null values if necessary
    if nulls > 0 and not constants:
        num_nulls = int(num_rows * nulls)
        for _ in range(num_nulls):
            values.append(np.nan)
        random.shuffle(values)

    # Ensure the column has the correct number of rows
    values = values[:num_rows]
    df[column_name] = values
    return df
import pandas as pd
import numpy as np
import random

def decimal_logic(column_name, num_rows, constraint_range, constraint_decimal, nulls, constants, distinct, df):
    _, decimal_places = constraint_decimal  # Only decimal_places is used from constraint_decimal

    def generate_unique_decimal(existing, number_range, decimal_places):
        while True:
            integer_part = random.randint(*number_range)  # Use constraint_range directly for integer part
            decimal_part = random.randint(0, 10**decimal_places - 1)
            decimal_number = float(f"{integer_part}.{str(decimal_part).zfill(decimal_places)}")
            if distinct and decimal_number in existing:
                continue
            return decimal_number

    values = []

    # Rule 1: Use constants if provided
    if constants:
        values.extend(constants * (num_rows // len(constants)))
        values.extend(constants[:num_rows % len(constants)])
    else:
        existing_values = set()
        for _ in range(int(num_rows * (1 - nulls))):
            if distinct:
                num = generate_unique_decimal(existing_values, constraint_range, decimal_places)
                existing_values.add(num)
            else:
                num = generate_unique_decimal(set(), constraint_range, decimal_places)
            values.append(num)
    
    # Adjust for null values if necessary
    if nulls > 0 and not constants:
        num_nulls = int(num_rows * nulls)
        for _ in range(num_nulls):
            values.append(np.nan)
        random.shuffle(values)

    # Ensure the column has the correct number of rows
    values = values[:num_rows]
    df[column_name] = values
    return df



def date_logic(column_name, num_rows, constraint_range, nulls, constants, distinct, df):
    start_date = datetime.strptime(constraint_range[0], "%Y-%m-%d")
    end_date = datetime.strptime(constraint_range[1], "%Y-%m-%d")
    date_range = (end_date - start_date).days

    def generate_unique_date(existing, start_date, date_range):
        while True:
            offset_days = random.randint(0, date_range)
            date = start_date + timedelta(days=offset_days)
            if distinct and date in existing:
                continue
            return date

    values = []

    # Rule 1: Use constants if provided, ensuring they're datetime objects
    if constants:
        constants_dates = [datetime.strptime(date_str, "%Y-%m-%d") for date_str in constants]
        values.extend(constants_dates * (num_rows // len(constants)))
        values.extend(constants_dates[:num_rows % len(constants)])
    else:
        existing_dates = set()
        for _ in range(int(num_rows * (1 - nulls))):
            if distinct:
                date = generate_unique_date(existing_dates, start_date, date_range)
                existing_dates.add(date)
            else:
                date = generate_unique_date(set(), start_date, date_range)
            values.append(date)
    
    # Adjust for null values if necessary
    if nulls > 0 and not constants:
        num_nulls = int(num_rows * nulls)
        for _ in range(num_nulls):
            values.append(pd.NaT)  # Use pandas' NaT for missing date values
        random.shuffle(values)

    # Ensure the column has the correct number of rows
    values = values[:num_rows]
    df[column_name] = pd.to_datetime(values)  # Ensure the column is of datetime type
    return df





def timestamp_logic(column_name, num_rows, constraint_range, nulls, constants, distinct, df):
    def parse_custom_timestamp(ts_str):
        """Parse a timestamp string with a non-standard microseconds separator."""
        # Assuming the format is 'YYYY-MM-DD HH:MM:SS:ffffff'
        try:
            # Split the timestamp string on the last colon, which precedes the microseconds
            date_time_part, microseconds_part = ts_str.rsplit(':', 1)
            # Reconstruct the timestamp with the correct microseconds separator
            corrected_ts_str = f"{date_time_part}.{microseconds_part}"
            # Now parse the corrected timestamp string
            return datetime.strptime(corrected_ts_str, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError as e:
            print(f"Error parsing timestamp: {e}")
            return None

    def generate_unique_timestamp(existing, start_timestamp, timestamp_range_seconds):
        while True:
            offset_seconds = random.randint(0, timestamp_range_seconds)
            timestamp = start_timestamp + timedelta(seconds=offset_seconds)
            # Randomly generate microseconds and add to the timestamp
            microseconds = random.randint(0, 999999)
            timestamp += timedelta(microseconds=microseconds)
            if distinct and timestamp in existing:
                continue
            return timestamp
    # Adjust the parsing of start and end timestamps
    start_timestamp = parse_custom_timestamp(constraint_range[0])
    end_timestamp = parse_custom_timestamp(constraint_range[1])
    timestamp_range_seconds = int((end_timestamp - start_timestamp).total_seconds())

    values = []
    existing_timestamps = set()

    # Generate timestamps
    for _ in range(int(num_rows * (1 - nulls))):
        if distinct:
            timestamp = generate_unique_timestamp(existing_timestamps, start_timestamp, timestamp_range_seconds)
            existing_timestamps.add(timestamp)
        else:
            timestamp = generate_unique_timestamp(set(), start_timestamp, timestamp_range_seconds)
        values.append(timestamp)

    # Adjust for null values if necessary
    if nulls > 0:
        num_nulls = int(num_rows * nulls)
        values += [pd.NaT] * num_nulls  # Use pandas' NaT for missing timestamp values
        random.shuffle(values)

    # Ensure the column has the correct number of rows
    values = values[:num_rows]
    df[column_name] = pd.to_datetime(values)  # Ensure the column is suitable for timestamps
    return df

for table in yaml_data['tables']:
    dataframe = pd.DataFrame()
    number_of_rows = yaml_data['tables'][table]['rows']
    save_to_local = yaml_data['tables'][table]['save_to_local'][0]
    local_save_location = yaml_data['tables'][table]['save_to_local'][1]['local_location']
    save_to_databricks = yaml_data['tables'][table]['save_to_databricks'][0]
    databricks_location = yaml_data['tables'][table]['save_to_databricks'][1]['databricks_table']
    for column in yaml_data['tables'][table]['columns']:
        if column['data_type'] == 'StringType':
            dataframe = string_logic(column['name'],
                         num_rows=number_of_rows,
                         length=column['constraint_length'],
                         nulls=column['constraint_nulls'],
                         constants=column['constraint_constants'],
                         distinct=column['constraint_distinct'],
                         special_characters=column['constraint_special_chars'],
                         df=dataframe)
        elif column['data_type'] in ['IntegerType', 'ShortType', 'LongType']:
            dataframe = numeric_logic(column['name'],
                         num_rows=number_of_rows,
                         constraint_range=column['constraint_range'],
                         nulls=column['constraint_nulls'],
                         constants=column['constraint_constants'],
                         distinct=column['constraint_distinct'],
                         df=dataframe)
        elif column['data_type'] == 'DecimalType':
            dataframe = decimal_logic(column['name'],
                         num_rows=number_of_rows,
                         constraint_range=column['constraint_range'],
                         constraint_decimal=column['constraint_decimal_range'],
                         nulls=column['constraint_nulls'],
                         constants=column['constraint_constants'],
                         distinct=column['constraint_distinct'],
                         df=dataframe)
        elif column['data_type'] == 'DateType':
            dataframe = date_logic(column['name'],
                         num_rows=number_of_rows,
                         constraint_range=column['constraint_range'],
                         nulls=column['constraint_nulls'],
                         constants=column['constraint_constants'],
                         distinct=column['constraint_distinct'],
                         df=dataframe)
        elif column['data_type'] == 'DateType':
            dataframe = date_logic(column['name'],
                         num_rows=number_of_rows,
                         constraint_range=column['constraint_range'],
                         nulls=column['constraint_nulls'],
                         constants=column['constraint_constants'],
                         distinct=column['constraint_distinct'],
                         df=dataframe)
        elif column['data_type'] == 'TimeStampType':
            dataframe = timestamp_logic(column['name'],
                         num_rows=number_of_rows,
                         constraint_range=column['constraint_range'],
                         nulls=column['constraint_nulls'],
                         constants=column['constraint_constants'],
                         distinct=column['constraint_distinct'],
                         df=dataframe)
        else:
            raise Exception


    print(dataframe)


        