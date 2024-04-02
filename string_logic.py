import pandas as pd
import numpy as np
import random
from string import ascii_letters

# Example seed and number of rows
random_seed = 42
num_rows = 100
random.seed(random_seed)
np.random.seed(random_seed)  # Ensuring reproducibility for numpy operations as well

# Configuration for the column
column_config = {
    'name': 'patient_id',
    'datatype': 'StringType',
    'constraint_length': 5,
    'constraint_nulls': 0,
    'constraint_nullable': True,
    'constraint_constants': [],
    'constraint_distinct': False,
    'constraint_special_chars': ['@', '#', '$']  # Example special characters
}

# Function to generate a unique string of given length that includes at least one special character
def generate_unique_string(length, existing, special_chars):
    while True:
        # Ensure at least one special character is included
        part_special = random.choice(special_chars) if special_chars else ''
        part_random = ''.join(random.choices(ascii_letters, k=length - len(part_special)))
        s = part_random + part_special
        s = ''.join(random.sample(s, len(s)))  # Shuffle to randomize the position of the special character
        if s not in existing:
            return s

# Generate the column based on configuration
def generate_column(config, num_rows):
    column_name = config['name']
    length = config['constraint_length']
    nulls = config['constraint_nulls']
    constants = config['constraint_constants']
    distinct = config['constraint_distinct']
    special_chars = config['constraint_special_chars']

    # Initialize list to store generated values
    values = []

    # Check if constants are provided
    if constants:
        values.extend(constants * (num_rows // len(constants)))
        values.extend(constants[:num_rows % len(constants)])
    else:
        existing_values = set()
        for _ in range(int(num_rows * (1 - nulls))):
            if distinct:
                s = generate_unique_string(length, existing_values, special_chars)
                existing_values.add(s)
            else:
                s = generate_unique_string(length, [], special_chars)
            values.append(s)
    
    # Adjust for null values if necessary
    if nulls > 0 and not constants:
        num_nulls = int(num_rows * nulls)
        for _ in range(num_nulls):
            values.append(np.nan)
        random.shuffle(values)

    # Ensure the column has the correct number of rows
    values = values[:num_rows]

    return pd.DataFrame({column_name: values})

# Generate the DataFrame column
df = generate_column(column_config, num_rows)
df.head()
