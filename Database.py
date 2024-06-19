import pandas as pd
import numpy as np
import csv
from sklearn.linear_model import LinearRegression
import warnings
from scipy import stats
import statsmodels.api as sm

warnings.filterwarnings("ignore")

years = range(1995, 2020)

def process_files(input_df_path, input1_path, input2_path, output_file):

    input_df = pd.read_csv(input_df_path)

    # Create a dictionary to store the totals for each country
    country_totals = {}


    # Calculate totals for each country
    with open(input1_path, newline='') as input1_file:
        input1_reader = csv.reader(input1_file)
        for row1 in input1_reader:
            country = row1[0]
            country_totals[country] = {
                'total_value_added': 0,
                'EXGR_VA': 0,
                'total_m_loc_consumed': 0,
                'total_m_foreign_consumed': 0,
                'total_m_total_consumed': 0,
                'total_gfcf': 0
            }
#            with open(input2_path, newline='') as input2_file:
#                input2_reader = csv.reader(input2_file)
#                for row2 in input2_reader:
#                    industry = row2[0]
#
            bd_key = f"{country}"
            filtered_df = input_df[input_df['Country'] == bd_key]

            country_totals[country]['total_value_added'] += filtered_df['ValueAdded'].sum()
            country_totals[country]['EXGR_VA'] += filtered_df['EXGR_VA'].sum()
            country_totals[country]['total_m_loc_consumed'] += filtered_df['M_loc_consumed'].sum()
            country_totals[country]['total_m_foreign_consumed'] += filtered_df['M_foreighn_consumed'].sum()
            country_totals[country]['total_m_total_consumed'] += filtered_df['M_total_consumed'].sum()
            country_totals[country]['total_gfcf'] += filtered_df['GFCF'].sum()

    # Create Names of new columns
    year_ranges = [range(1995, 2020), range(1995, 2008), range(2010, 2020)]
    suffix = 0
    created_variables = []
#    prefix = {"corr_", "p_value_corr_", "slope_", "intercept_", "r_squared_", "p_value_", "t_value_sl_", "std_err_"}
    middle = {"GFCC","M_loc_consumed","M_foreighn_consumed","M_total_consumed","M_TOTAL_AND_GFCC"}
    va_dva = {"EXGR_VA","ValueAdded"}
    for years in year_ranges:
        suffix = suffix + 1
        for vadva in va_dva:
            for flag in middle:
                variable_name_base = f"{flag}_{vadva}_{suffix}"
                created_variables.extend([
                    f"corr_{variable_name_base}",
                    f"p_value_corr_{variable_name_base}",
                    f"slope_{variable_name_base}",
                    f"intercept_{variable_name_base}",
                    f"r_squared_{variable_name_base}",
                    f"p_value_{variable_name_base}",
                    f"t_value_sl_{variable_name_base}",
                    f"std_err_{variable_name_base}"])
    n = len(created_variables)
    print(created_variables)

    # Process each industry and write to the output file
    with open(output_file, 'w',newline='') as f:
        existing_columns = ['Country','Industry','ValueAdded','DVA_Exports','M_loc_consumed','M_foreighn_consumed','M_total_consumed','GFCC','DB_INDEX','GROWTH_FACTOR','SHARE']
        writer = csv.writer(f, delimiter=',')
        writer.writerow(existing_columns + created_variables)

        with open(input1_path, newline='') as input1_file:
            input1_reader = csv.reader(input1_file)
            for row1 in input1_reader:
                country = row1[0]
                totals = country_totals[country]

                with open(input2_path, newline='') as input2_file:
                    input2_reader = csv.reader(input2_file)
                    for row2 in input2_reader:
                        industry = row2[0]
                        information = {}

                        bd_key = f"{country}{industry}"
                        filtered_df = input_df[input_df['DB_IND'] == bd_key]

                        value_added = round(filtered_df['ValueAdded'].sum(),4)
                        DVA_Exports = round(filtered_df['EXGR_VA'].sum(),4)
                        m_loc_consumed = round(filtered_df['M_loc_consumed'].sum(),4)
                        m_foreign_consumed = round(filtered_df['M_foreighn_consumed'].sum(),4)
                        m_total_consumed = round(filtered_df['M_total_consumed'].sum(),4)
                        gfcc = round(filtered_df['GFCF'].sum(),4)
                        M_TOTAL_AND_GFCG = m_total_consumed + gfcc
                        
                        year_ranges = [range(1995, 2020), range(1995, 2008), range(2010, 2020)]
                        suffix = 0

                        if country_totals[country]['total_value_added'] > 0:
                            growth_factor = round((gfcc + m_total_consumed) / value_added,4)
                            share = round((value_added) / country_totals[country]['total_value_added'],4)
                        else:
                            growth_factor = 'n/a'
                            share = 'n/a'
                            
                        data_to_write = [country,industry,value_added,DVA_Exports,m_loc_consumed,m_foreign_consumed,m_total_consumed,gfcc,bd_key,growth_factor,share]  # Existing data
                           
                        for years in year_ranges:
                            yearly_data = {
                                  'M_loc_consumed': filtered_df[filtered_df['Year'].isin(years)]['M_loc_consumed'],
                                  'M_foreighn_consumed': filtered_df[filtered_df['Year'].isin(years)]['M_foreighn_consumed'],
                                  'M_total_consumed': filtered_df[filtered_df['Year'].isin(years)]['M_total_consumed'],
                                  'EXGR_VA': filtered_df[filtered_df['Year'].isin(years)]['EXGR_VA'],
                                  'M_TOTAL_AND_GFCC': filtered_df[filtered_df['Year'].isin(years)]['M_TOTAL_AND_GFCG'],
                                  'ValueAdded': filtered_df[filtered_df['Year'].isin(years)]['ValueAdded'],
                                  'GFCC': filtered_df[filtered_df['Year'].isin(years)]['GFCF'],
                                  'Year': filtered_df[filtered_df['Year'].isin(years)]['Year']
                            }
                              
                            suffix = suffix + 1
                            correlations = {}
                            
                            for vadva in va_dva:
                                for flag in middle:
                                    if not yearly_data[flag].isnull().all() and not yearly_data[vadva].isnull().all() and yearly_data[flag].nunique() > 1:
                                        correlation, p_value_correlation = stats.pearsonr(yearly_data[flag],yearly_data[vadva])
                                        correlation = "{:.7f}".format(correlation)
                                        p_value_correlation = "{:.7f}".format(p_value_correlation)
                                        X = sm.add_constant(yearly_data[flag])
                                        y = yearly_data[vadva]

                                        model = sm.OLS(y, X).fit()

                                        slope = "{:.7f}".format(model.params[1])
                                        intercept = "{:.7f}".format(model.params[0])
                                        r_value = "{:.7f}".format(model.rsquared)
                                        p_value = "{:.7f}".format(model.pvalues[1])  
                                        t_value_slope = "{:.7f}".format(model.tvalues[0])
                                        r_squared = "{:.7f}".format(model.rsquared)
                                        std_err = "{:.7f}".format(model.bse[1])
                                        
                                        correlations = (correlation, p_value_correlation, slope, intercept, r_squared, p_value, t_value_slope, std_err)
                                    else:
                                        correlations = ('n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a')
                                    data_to_write.extend(correlations)
                        writer.writerow(data_to_write)
                        print(f"Country '{country}' Industry '{industry}' processed.")    

#                        for record_name, record_data in data.items():
#                            data_to_write = [record_data.get(col_name) for col_name in existing_columns]
#                            data_to_write.extend([record_data.get(var_name) for var_name in created_variables])
#                            writer.writerow(data_to_write)
#                        print(f"Country '{country}' Industry '{industry}' processed.")
                
                # Write totals for the country
#                f.write(f"{country},TOTAL,{totals['total_value_added']},{totals['EXGR_VA']},{totals['total_m_loc_consumed']},{totals['total_m_foreign_consumed']},{totals['total_m_total_consumed']},{totals['total_gfcf']}\n")

process_files("Output_EXGR_DVA1.csv", "Input1.csv", "Input2.csv", "BASE_FINAL.csv")
