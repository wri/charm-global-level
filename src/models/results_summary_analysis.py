#!/usr/bin/env python
"""
1. Grab the national results
2. Calculate the global results 
3. Calculate the new tropical plantation scneario based on global results
"""
__author__ = "Liqing Peng"
__copyright__ = "Copyright (C) 2023 World Resources Institute, The Carbon Harvest Model (CHARM) Project"
__credits__ = ["Liqing Peng", "Jessica Zionts", "Tim Searchinger", "Richard Waite"]
__license__ = "MIT"
__version__ = "2023.1.1"
__maintainer__ = "Liqing Peng"
__email__ = "liqing.peng@wri.org"
__status__ = "Dev"

import numpy as np
import pandas as pd
import Tropical_new_plantation_calculator

#############################################Path###########################################
root = '../..'
indir = '{}/data/processed'.format(root)
outdir = '{}/data/processed/derivative'.format(root)
sensoutdir = '{}/data/processed/derivative/sensitivity_analysis'.format(root)


##############################################Read in model outputs##########################################
# 2022 Jan Lists
carbon_lists = ['Default: Plantation supply wood (mega tC)', 'Default: Secondary forest supply wood (mega tC)', 'S1 regrowth: total PDV (mega tC)', 'S1 regrowth: PDV plantation (mega tC)', 'S1 regrowth: PDV secondary (mega tC)', 'S2 conversion: total PDV (mega tC)', 'S3 mixture: total PDV (mega tC)', 'S4 125% GR: total PDV (mega tC)', 'S5 62% SL: total PDV (mega tC)', 'S6 WFL 50% less: total PDV (mega tC)']
area_lists = ['Plantation area (ha)', 'S1 regrowth: Secondary area (ha)', 'S2 conversion: Secondary area (ha)', 'S3 mixture: Secondary area (ha)', 'S3 mixture: Secondary middle aged area (ha)', 'S3 mixture: Secondary mature area (ha)', 'S4 125% GR: Secondary area (ha)', 'S5 62% SL: Secondary area (ha)', 'S6 WFL 50% less: Secondary area (ha)']

def extract_global_outputs_summary(results):
    """Extract the 1-5th scenarios output"""
    ###The major scenarios
    cf_MtC_GtCO2 = 1/1000 * 44 / 12
    cf_ha_mha = 1/1000000
    # Fixme change 40 to 41
    nyears = 40 + 1
    carbon_costs_annual = results[['S1 regrowth: total PDV (mega tC)','S2 conversion: total PDV (mega tC)', 'S3 mixture: total PDV (mega tC)', 'S4 125% GR: total PDV (mega tC)', 'S5 62% SL: total PDV (mega tC)', 'S6 WFL 50% less: total PDV (mega tC)']].sum() / 0.8 * cf_MtC_GtCO2 / nyears
    area_total = results[['Plantation area (ha)', 'S1 regrowth: Secondary area (ha)', 'S2 conversion: Secondary area (ha)', 'S3 mixture: Secondary area (ha)', 'S4 125% GR: Secondary area (ha)', 'S5 62% SL: Secondary area (ha)', 'S6 WFL 50% less: Secondary area (ha)']].sum() / 0.8 * cf_ha_mha

    return carbon_costs_annual, area_total

def extract_global_wood_supply(results):
    """Extract the 1-5th scenarios output"""
    ###The major scenarios
    wood_supply = results[['Default: Plantation supply wood (mega tC)', 'Default: Secondary forest supply wood (mega tC)','125% GR: Plantation supply wood (mega tC)', '125% GR: Secondary forest supply wood (mega tC)', '62% SL: Plantation supply wood (mega tC)', '62% SL: Secondary forest supply wood (mega tC)', 'WFL50less: Plantation supply wood (mega tC)', 'WFL50less: Secondary forest supply wood (mega tC)']].sum() / 0.8 * 1000000  # mega tC to tC

    return wood_supply

def extract_secondary_carbon_costs(results):
    """Extract the 1-5th scenarios output"""
    ###The major scenarios
    cf_MtC_GtCO2 = 1/1000 * 44 / 12
    # Fixme change 40 to 41
    nyears = 40 + 1
    carbon_costs_annual = results[['S1 regrowth: total PDV (mega tC)','S1 regrowth: PDV plantation (mega tC)', 'S1 regrowth: PDV secondary (mega tC)',]].sum() / 0.8 * cf_MtC_GtCO2 / nyears

    return carbon_costs_annual

def extract_regrowth_scenario(results):
    """Extract the 1st scenarios output"""
    ###The major scenarios
    cf_MtC_GtCO2 = 1/1000 * 44 / 12
    cf_ha_mha = 1/1000000
    # Fixme change 40 to 41
    nyears = 40 + 1
    carbon_costs_annual = results[['S1 regrowth: total PDV (mega tC)']].sum() / 0.8 * cf_MtC_GtCO2 / nyears
    area_total = results[['Plantation area (ha)', 'S1 regrowth: Secondary area (ha)']].sum() / 0.8 * cf_ha_mha

    return carbon_costs_annual, area_total

############################################## Results Summary ##########################################
def summarize_results_all(datafile, outfile, discount_rate):
    ### Prepare the data arrays
    # 12 demand and sub levels x (6+1) scenarios
    carbon_costs = np.zeros((12, 7))
    # 12 demand and sub levels x (6+1) scenarios + 2 columns for plantation areas
    required_area = np.zeros((12, 9))
    # 12 demand and sub levels x (4+1) scenarios x 2
    wood_supply = np.zeros((12, 10))
    row = 0
    row_index = []
    for vslp_input_control in ['ALL', 'IND', 'WFL']:
        for substitution_mode in ['NOSUB', 'SUBON']:
            for future_demand_level in ['BAU', 'CST']:
                output_tabname = '{}_{}_{}'.format(future_demand_level, substitution_mode, vslp_input_control)
                row_index.append(output_tabname)
                results = pd.read_excel(datafile, sheet_name=output_tabname)
                carbon_main, land_main = extract_global_outputs_summary(results)
                wood_main = extract_global_wood_supply(results)
                carbon_last, secondary_land_last, new_tropical_land_last, secondary_wood_last, plantation_wood_last = Tropical_new_plantation_calculator.PlantationCalculator(datafile, results).run_new_tropical_plantations_scenario()
                carbon_costs[row, :3] = carbon_main.values[:3]
                carbon_costs[row, 4:7] = carbon_main.values[3:]
                required_area[row, :3] = land_main.values[1:4]
                required_area[row, 4:7] = land_main.values[4:]
                wood_supply[row, :2] = wood_main.values[:2]
                wood_supply[row, 4:10] = wood_main.values[2:]
                # The 4th scenario new tropical plantation
                carbon_costs[row, 3] = carbon_last
                required_area[row, 3] = secondary_land_last

                required_area[row, 7] = land_main.values[0]  # The existing plantation
                required_area[row, 8] = new_tropical_land_last  # The new plantation

                wood_supply[row, 2] = plantation_wood_last
                wood_supply[row, 3] = secondary_wood_last

                row = row + 1

    def write_excel(filename, sheetname, dataframe):
        "This function will overwrite the Outputs sheet"
        with pd.ExcelWriter(filename, engine='openpyxl', mode='a') as writer:
            workbook = writer.book
            try:
                workbook.remove(workbook[sheetname])
                print("Updating Outputs sheet...")
            except:
                print("Creating Outputs sheet...")
            finally:
                dataframe.to_excel(writer, sheet_name=sheetname)
                writer.save()

    # Convert to pandas dataframe
    scenarios = ['S1 Secondary forest harvest + regrowth', 'S2 Secondary forest harvest + conversion', 'S3 Secondary forest mixed harvest',
     'S4 New tropical plantations', 'S5 Higher plantation productivity', 'S6 Higher harvest efficiency', 'S7 50% less 2050 wood fuel demand']
    carbon_df = pd.DataFrame(carbon_costs, index=row_index, columns=scenarios)
    write_excel(outfile, 'CO2 (Gt per yr) DR_{}'.format(discount_rate), carbon_df)
    # For land and wood supply, no matter what discount it is, the land area does not change
    if discount_rate == '4p':
        land_areas = scenarios + ['Existing plantations', 'New plantations']
        wood_supply_items = ['Default: Plantation supply wood (mega tC)',
                             'Default: Secondary forest supply wood (mega tC)',
                             'Agriland: Plantation supply wood (mega tC)',
                             'Agriland: Secondary forest supply wood (mega tC)',
                             '125% GR: Plantation supply wood (mega tC)',
                             '125% GR: Secondary forest supply wood (mega tC)',
                             '62% SL: Plantation supply wood (mega tC)',
                             '62% SL: Secondary forest supply wood (mega tC)',
                             'WFL50less: Plantation supply wood (mega tC)',
                             'WFL50less: Secondary forest supply wood (mega tC)']
        area_df = pd.DataFrame(required_area, index=row_index, columns=land_areas)
        wood_df = pd.DataFrame(wood_supply, index=row_index, columns=wood_supply_items)
        write_excel(outfile, 'Land (Mha) DR_{}'.format(discount_rate), area_df)
        write_excel(outfile, 'Wood supply (mega tC) DR_{}'.format(discount_rate), wood_df)

    return


def collect_all_discount_rates_results(infile, outfile):
    "For Appendix 3 table"
    df_list = []
    for dr in ('0p', '2p', '4p', '6p'):
        carbon = pd.read_excel(infile, sheet_name='CO2 (Gt per yr) DR_{}'.format(dr), index_col=0)
        carbon_sel = carbon.loc[['BAU_NOSUB_ALL', 'BAU_SUBON_ALL']]
        df_list.append(carbon_sel.rename(index={'BAU_NOSUB_ALL': 'Gross emissions', 'BAU_SUBON_ALL':'Net emissions including substitution savings'}))
    big_table = pd.concat(df_list)
    big_table.to_csv(outfile)

    return


def collect_secondary_carbon_costs_all_years():
    "This is to compare 100yr and 40yr on secondary carbon costs only, excluding plantation, for bar charts"
    # 4 demand and 2x4 scenarios
    carbon_costs = np.zeros((4, 8))
    col_index = []
    col = 0
    vslp_input_control = 'ALL'
    for years in [40, 100]:
        for discount_rate in ['0p', '2p', '4p', '6p']:
            datafile = '{}/data/processed/CHARM regional - YR_{} - DR_{} - V{}.xlsx'.format(root, years, discount_rate, version)
            col_index.append('YR{}-DR{}'.format(years, discount_rate))
            row_index = []
            row = 0
            for substitution_mode in ['NOSUB', 'SUBON']:
                for future_demand_level in ['BAU', 'CST']:
                    output_tabname = '{}_{}_{}'.format(future_demand_level, substitution_mode, vslp_input_control)
                    row_index.append(output_tabname)
                    results = pd.read_excel(datafile, sheet_name=output_tabname)
                    carbon_main = extract_secondary_carbon_costs(results)
                    carbon_costs[row, col] = carbon_main.values[2]  # S1 regrowth: PDV secondary (mega tC)

                    row = row + 1
            col = col + 1

    # Convert to pandas dataframe
    carbon_df = pd.DataFrame(carbon_costs, index=row_index, columns=col_index)
    carbon_df.to_csv('{}/data/processed/derivative/secondary_carbon_costs_40vs100yr.csv'.format(root))

    return


def summarize_results_sensitivity(outfile, years, discount_rate):
    "This is for the sensitivity analysis only"
    m = len(experiments)
    # 2 demand and sub levels x M experiments
    carbon_costs = np.zeros((2, m+1))
    # 2 demand and sub levels x M experiments
    required_area = np.zeros((2, m+1))

    vslp_input_control = 'ALL'
    substitution_mode = 'NOSUB'
    for col, exp in enumerate(experiments):
        datafile = '{}/{}/CHARM regional - YR_{} - DR_{} - V{} - {}.xlsx'.format(indir, sensindir, years, discount_rate, version, exp)
        for row, future_demand_level in enumerate(['BAU', 'CST']):
            output_tabname = '{}_{}_{}'.format(future_demand_level, substitution_mode, vslp_input_control)
            results = pd.read_excel(datafile, sheet_name=output_tabname)
            carbon_main, land_main = extract_regrowth_scenario(results)
            carbon_costs[row, col+1] = -carbon_main.values[0]  # minus - cost
            required_area[row, col+1] = land_main.values[0] + land_main.values[1]

    # Add the baseline scenario
    datafile = '{}/CHARM regional - YR_{} - DR_{} - V{}.xlsx'.format(indir, years, discount_rate, version)
    for row, future_demand_level in enumerate(['BAU', 'CST']):
        output_tabname = '{}_{}_{}'.format(future_demand_level, substitution_mode, vslp_input_control)
        results = pd.read_excel(datafile, sheet_name=output_tabname)
        carbon_main, land_main = extract_regrowth_scenario(results)
        carbon_costs[row, 0] = -carbon_main.values[0]  # minus - cost
        required_area[row, 0] = land_main.values[0] + land_main.values[1]

    def write_excel(filename, sheetname, dataframe):
        "This function will overwrite the Outputs sheet"
        with pd.ExcelWriter(filename, engine='openpyxl', mode='a') as writer:
            workbook = writer.book
            try:
                workbook.remove(workbook[sheetname])
                print("Updating Outputs sheet...")
            except:
                print("Creating Outputs sheet...")
            finally:
                dataframe.to_excel(writer, sheet_name=sheetname)
                writer.save()


    # Convert to pandas dataframe

    carbon_df = pd.DataFrame(carbon_costs, index=['BAU_NOSUB_ALL', 'CST_NOSUB_ALL'], columns=names)
    write_excel(outfile, 'CO2 (Gt per yr) DR_{}'.format(discount_rate), carbon_df)
    area_df = pd.DataFrame(required_area, index=['BAU_NOSUB_ALL', 'CST_NOSUB_ALL'], columns=names)
    write_excel(outfile, 'Land (Mha) DR_{}'.format(discount_rate), area_df)

    return


########## Input
version = '20230125'
sensindir = 'run_NatSensitivity_{}'.format(version)
discount_rates = ['4p', '0p', '2p', '6p']
years_list = [100]


# Step 1
# for years in years_list:
#     for discount_rate in discount_rates:
#         datafile = '{}/data/processed/CHARM regional - YR_{} - DR_{} - V{}.xlsx'.format(root, years, discount_rate, version)
#         outfile = '{}/data/processed/derivative/CHARM_global_carbon_land_summary - YR_{} - V{}.xlsx'.format(root, years, version)
#         summarize_results_all(datafile, outfile, discount_rate)

# Step 2
# for years in years_list:
#     infile = '{}/data/processed/derivative/CHARM_global_carbon_land_summary - YR_{} - V{}.xlsx'.format(root, years, version)
#     outfile = '{}/data/processed/derivative/carbon_results_all_discountrate - YR_{} - V{}.csv'.format(root, years, version)
#     collect_all_discount_rates_results(infile, outfile)

# Step 3 Fig E3
# collect_secondary_carbon_costs_all_years()

# Step 4

# Sensitivity analysis
# growth_exps = ['GR_25U', 'GR_25D', 'GR1_GR2_25U', 'GR1_GR2_25D', 'GR1_GR2_50U']
# rootshoot_exps = ['RSR_25U', 'RSR_25D']
# demand_exps = ['Demand_OECD', 'Demand_IIASA', 'Demand_LINE']
# trade_exps = ['Trade_50U', 'Trade_50D']
# old_exps = ['Old_GRRL', 'Old_PGR', 'Old_SGR', 'Old_RL', 'Old_SR']
# experiments = growth_exps + rootshoot_exps + demand_exps + trade_exps
#
# growth_names = ['GRs 25% Up', 'GRs 25% Down', 'GR1/GR2 25% Up', 'GR1/GR2 25% Down', 'GR1/GR2 50% Up']
# rootshoot_names = ['R/S 25% Up', 'R/S 25% Down']
# demand_names = ['OECD', 'IIASA', 'LINE']
# trade_names = ['Tropical exports 50% Up', 'Tropical exports 50% Down']
# names = ['Baseline'] + growth_names + rootshoot_names + demand_names + trade_names

# years = 40
# discount_rate = '4p'
# outfile = '{}/CHARM_global_carbon_land_summary - YR_{} - V{} - sensitivity.xlsx'.format(sensoutdir, years, version)

# years = 100
# discount_rate = '4p'
# outfile = '{}/CHARM_global_carbon_land_summary - YR_{} - V{} - sensitivity Old.xlsx'.format(sensoutdir, years, version)

# experiments = old_exps
# names = ['Baseline'] + old_exps

# summarize_results_sensitivity(outfile, years, discount_rate)