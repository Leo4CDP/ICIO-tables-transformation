import os
import csv
from decimal import Decimal, ROUND_HALF_UP

# Function to calculate various values as per the described algorithm
def calculate_values(base, country, industry):
    # Initialize variables
    local_consumed = 0
    local_consumption = 0
    import_val = 0
    taxes = 0
    value_added = 0
    output = 0
    k = 0
    # Find relevant column
    country_industry_col = country + "_" + industry
    
    # Calculate LOCALCONS and IMPORT
    for row in base:
        if row['V1'].startswith(country):
            local_consumed += float(row[country_industry_col])  # Convert to float
        elif row['V1'] == 'TLS':
            taxes = float(row[country_industry_col])  # Convert to float
        elif row['V1'] == 'VA':
            value_added = float(row[country_industry_col])  # Convert to float
        elif row['V1'] == 'OUT':
            output = float(row[country_industry_col])  # Convert to float
        
    # Calculate other variables
    for index, row in enumerate(base):
        if row['V1'] == country_industry_col:
            k = index
            break

    import_val = output - local_consumed - taxes - value_added
    local_consumption = sum([float(base[k][country + "_HFCE"]), float(base[k][country + "_NPISH"]), float(base[k][country + "_GGFC"]), float(base[k][country + "_GFCF"]), float(base[k][country + "_INVNT"]), float(base[k][country + "_DPABR"])])
    local_interim = sum([float(base[k][col]) for col in base[k] if col.startswith(country)]) - local_consumption  # Convert to float
    foreign_consumption = sum([float(base[k][col]) for col in base[k] if col.endswith('_HFCE') or col.endswith('_NPISH') or col.endswith('_GGFC') or col.endswith('_GFCF') or col.endswith('_INVNT') or col.endswith('_DPABR')]) - local_consumption  # Convert to float
    foreign_interim = output - (local_consumption + foreign_consumption + local_interim)
    
    # Construct dictionary of calculated values
    data = {
        'Year': filename[:4],
        'Country': country,
        'Industry': industry,
        'Import': round(import_val,4),
        'LocalConsumed': round(local_consumed,4),
        'GrossConsumed': round(import_val + local_consumed,4),
        'Taxes': round(taxes,4),
        'ValueAdded': round(value_added,4),
        'OutPut1': round(output,4),
        'HFCE': round(float(base[k][country + "_HFCE"]),4),
        'NPISH': round(float(base[k][country + "_NPISH"]),4),
        'GGFC': round(float(base[k][country + "_GGFC"]),4),
        'GFCF': round(float(base[k][country + "_GFCF"]),4),
        'INVNT': round(float(base[k][country + "_INVNT"]),4),
        'DPABR': round(float(base[k][country + "_DPABR"]),4),
        '4ExportInterim': round(foreign_interim,4),
        '4LocalInterim': round(local_interim,4),
        '4ExportConsumption': round(foreign_consumption,4),
        '4LocalConcumption': round(local_consumption,4),
        'NetProduction': round(local_interim + local_consumption - local_consumed,4),
        'NetExport': round(foreign_interim + foreign_consumption - import_val,4),
        'NetVA': round(foreign_interim + foreign_consumption + local_interim + local_consumption - import_val - local_consumed,4),
        'TotalProduction': round(local_interim + local_consumption + foreign_interim + foreign_consumption,4)
    }
    
    return data

# Input paths
input1_path = "input1.csv"
input2_path = "input2.csv"
input3_folder = os.path.join(os.getcwd(), "ICIObase")  # Full path to the 'IODatebase' folder
output_folder = "output.csv"
column_names = ['Year', 'Country', 'Industry', 'Import', 'LocalConsumed', 'GrossConsumed', 'Taxes', 'ValueAdded', 'OutPut1', 'HFCE', 'NPISH', 'GGFC', 'GFCF', 'INVNT', 'DPABR', '4ExportInterim', '4LocalInterim', '4ExportConsumption', '4LocalConcumption', 'NetProduction', 'NetExport', 'NetVA', 'TotalProduction']

with open(output_folder, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=column_names)
    writer.writeheader()
    
    # Iterate through files in input3_folder
    for filename in os.listdir(input3_folder):
        if filename.endswith(".csv"):
            # Read data from current file
            with open(os.path.join(input3_folder, filename), newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                data = list(reader)
                
                # Iterate through rows of input1
                with open(input1_path, newline='') as input1_file:
                    input1_reader = csv.reader(input1_file)
                    for row1 in input1_reader:
                        country = row1[0]
                        
                        # Iterate through rows of input2
                        with open(input2_path, newline='') as input2_file:
                            input2_reader = csv.reader(input2_file)
                            for row2 in input2_reader:
                                industry = row2[0]
                                
                                # Calculate values and append to output.csv
                                result_data = calculate_values(data, country, industry)
                                writer.writerow(result_data)
                                
                                print(f"{filename}_{country}_{industry} FINISHED.")
