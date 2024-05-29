import pandas as pd
import csv

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
            country_totals[country]['total_m_loc_consumed'] += filtered_df['M_loc_consumed'].sum()
            country_totals[country]['total_m_foreign_consumed'] += filtered_df['M_foreighn_consumed'].sum()
            country_totals[country]['total_m_total_consumed'] += filtered_df['M_total_consumed'].sum()
            country_totals[country]['total_gfcf'] += filtered_df['GFCF'].sum()

    # Process each industry and write to the output file
    with open(output_file, 'w') as f:
        f.write('Country,Industry,ValueAdded,M_loc_consumed,M_foreighn_consumed,M_total_consumed,GFCC,VA_M_cor,Va_GFCC_cor,DB_INDEX,GROWTH_FACTOR,SHARE\n')

        with open(input1_path, newline='') as input1_file:
            input1_reader = csv.reader(input1_file)
            for row1 in input1_reader:
                country = row1[0]
                totals = country_totals[country]

                with open(input2_path, newline='') as input2_file:
                    input2_reader = csv.reader(input2_file)
                    for row2 in input2_reader:
                        industry = row2[0]

                        bd_key = f"{country}{industry}"
                        filtered_df = input_df[input_df['DB_INDEX'] == bd_key]

                        value_added = round(filtered_df['ValueAdded'].sum(),4)
                        m_loc_consumed = round(filtered_df['M_loc_consumed'].sum(),4)
                        m_foreign_consumed = round(filtered_df['M_foreighn_consumed'].sum(),4)
                        m_total_consumed = round(filtered_df['M_total_consumed'].sum(),4)
                        gfcf = round(filtered_df['GFCF'].sum(),4)

                        yearly_data = {
                            'M_total_consumed': filtered_df[filtered_df['Year'].isin(years)]['M_total_consumed'],
                            'ValueAdded': filtered_df[filtered_df['Year'].isin(years)]['ValueAdded'],
                            'GFCF': filtered_df[filtered_df['Year'].isin(years)]['GFCF'],
                        }

                        va_m_cor = round(yearly_data['M_total_consumed'].corr(yearly_data['ValueAdded'], method='pearson'), 4) if not yearly_data['M_total_consumed'].isnull().all() else 'n/a'
                        va_gfcc_cor = round(yearly_data['GFCF'].corr(yearly_data['ValueAdded'], method='pearson'), 4) if not yearly_data['GFCF'].isnull().all() else 'n/a'

                        # Calculate GROWTH_FACTOR and SHARE using country totals
                        if country_totals[country]['total_value_added'] > 0:
                            growth_factor = round((gfcf + m_total_consumed) / value_added,4)
                            share = round((value_added) / country_totals[country]['total_value_added'],4)
                        else:
                            growth_factor = 'n/a'
                            share = 'n/a'

                        f.write(f"{country},{industry},{value_added},{m_loc_consumed},{m_foreign_consumed},{m_total_consumed},{gfcf},{va_m_cor},{va_gfcc_cor},{bd_key},{growth_factor},{share}\n")
                        print(f"Country '{country}' Industry '{industry}' processed.")
                
                # Write totals for the country
                f.write(f"{country},TOTAL,{totals['total_value_added']},{totals['total_m_loc_consumed']},{totals['total_m_foreign_consumed']},{totals['total_m_total_consumed']},{totals['total_gfcf']},n/a,n/a,n/a,n/a,n/a\n")

process_files("DB_with_EXGR_DVA1.csv", "Input1.csv", "Input2.csv", "BASE_FINAL.csv")
