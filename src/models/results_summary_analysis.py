#!/usr/bin/env python
"""
1. Grab the national results
2. Calculate the global results 
3. Calculate the new tropical plantation scneario based on global results
"""
__author__ = "Liqing Peng"
__copyright__ = "Copyright (C) 2020-2023 World Resources Institute, The Carbon Harvest Model (CHARM) Project"
__credits__ = ["Liqing Peng", "Jessica Zionts", "Tim Searchinger", "Richard Waite"]
__license__ = "Polyform Strict License 1.0.0"
__version__ = "2023.1.1"
__maintainer__ = "Liqing Peng"
__email__ = "liqing.peng@wri.org"
__status__ = "Dev"

import numpy as np
import pandas as pd
import Global_by_country, Agricultural_land_tropical_scenario

### Datafile
root = '../..'
# figdir = '{}/../Paper/Figure'.format(root)

discount_filename = '4p'
years_filename = '40yr'


datafile = '{}/data/processed/CHARM regional - DR_{} - {} - Jan 18 2023.xlsx'.format(root, discount_filename, years_filename)
outdir = '{}/data/processed/derivative'.format(root)

# Sensitivity analysis
# growth_exps = ['GR 25U', 'GR 25D', 'GR2_GR1 25D', 'GR2_GR1 25U', 'GR2_GR1 50D']
# rootshoot_exps = ['RSR 25U', 'RSR 25D']
# trade_exps = ['trade 50U', 'trade 50D']
# demand_exps = ['demand OECD', 'demand IIASA', 'demand LINE']
# exp_filename = demand_exps[2]
#
# datafile = '{}/data/processed/CHARM regional - DR_{} - {} - Nov 1 2022 - {}.xlsx'.format(root, discount_filename, years_filename, exp_filename)
# outdir = '{}/data/processed/derivative/sensitivity_analysis'.format(root)

#############################################Read in model inputs###########################################
### Default parameters
nyears_harvest_settings = Global_by_country.SetupTime(datafile, country_iso='BRA', nyears_run_control='harvest')
Global = Global_by_country.Parameters(datafile, nyears_harvest_settings, country_iso='BRA')
nyears = Global.nyears
rotation_length = Global.rotation_length_harvest # this is the rotation length from Brazil, currently set to 7

##############################################Read in model outputs##########################################
# 2021 Nov Lists
# carbon_lists = ['Default: Plantation supply wood (mega tC)', 'Default: Secondary forest supply wood (mega tC)', 'S1 regrowth: total PDV (mega tC)', 'S1 regrowth: PDV plantation (mega tC)', 'S1 regrowth: PDV secondary (mega tC)', 'S2 conversion: total PDV (mega tC)', 'S3 mixture: total PDV (mega tC)', 'S4 125% GR: total PDV (mega tC)', 'S5 WFL 50% less: total PDV (mega tC)']
# area_lists = ['Plantation area (ha)', 'S1 regrowth: Secondary area (ha)', 'S2 conversion: Secondary area (ha)', 'S3 mixture: Secondary area (ha)', 'S3 mixture: Secondary middle aged area (ha)', 'S3 mixture: Secondary mature area (ha)', 'S4 125% GR: Secondary area (ha)', 'S5 WFL 50% less: Secondary area (ha)']
# 2022 Jan Lists
carbon_lists = ['Default: Plantation supply wood (mega tC)', 'Default: Secondary forest supply wood (mega tC)', 'S1 regrowth: total PDV (mega tC)', 'S1 regrowth: PDV plantation (mega tC)', 'S1 regrowth: PDV secondary (mega tC)', 'S2 conversion: total PDV (mega tC)', 'S3 mixture: total PDV (mega tC)', 'S4 125% GR: total PDV (mega tC)', 'S5 62% SL: total PDV (mega tC)', 'S6 WFL 50% less: total PDV (mega tC)']
area_lists = ['Plantation area (ha)', 'S1 regrowth: Secondary area (ha)', 'S2 conversion: Secondary area (ha)', 'S3 mixture: Secondary area (ha)', 'S3 mixture: Secondary middle aged area (ha)', 'S3 mixture: Secondary mature area (ha)', 'S4 125% GR: Secondary area (ha)', 'S5 62% SL: Secondary area (ha)', 'S6 WFL 50% less: Secondary area (ha)']

def extract_global_outputs_summary(results):
    """Extract the 1-5th scenarios output"""
    ###The major scenarios
    cf_MtC_GtCO2 = 1/1000 * 44 / 12
    cf_ha_mha = 1/1000000
    # Fixme change 40 to 41
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
    carbon_costs_annual = results[['S1 regrowth: total PDV (mega tC)','S1 regrowth: PDV plantation (mega tC)', 'S1 regrowth: PDV secondary (mega tC)',]].sum() / 0.8 * cf_MtC_GtCO2 / nyears

    return carbon_costs_annual

def prepare_global_outputs_for_new_tropical_scenario(results):
    """Extract outputs for the 6th scenario"""
    # Get global carbon and area numbers
    carbon_global = results[results.select_dtypes(include=['number']).columns][
                        carbon_lists].sum() / 0.8 * 1000000  # mega tC to tC
    area_global = results[results.select_dtypes(include=['number']).columns][area_lists].sum() / 0.8

    return carbon_global, area_global


def prepare_new_tropical_plantations_area(nyears, rotation_length, area_established_agriland_annual_global):
    """
        This is for the Tropical New Plantation Scenario, 4th scenario's input
        Set up plantation establishment rate per year, time and total area for harvest
    """
    # The first established plantation is in year 0, 2010; the last established plantation is in one rotation ahead of the last year. nyears - 1 + 1 for the range().
    year_new_plantation_st, year_new_plantation_ed = 0, nyears - rotation_length
    # The first harvested year of the established plantation is in one rotation behind of the first established year; the last harvested year is in last year, nyears - 1
    year_harvest_st, year_harvest_ed = year_new_plantation_st + rotation_length, nyears - 1

    area_established_new_agriland = np.zeros(nyears) # This is the area establishing plantation starting from year 0
    area_harvested_new_agriland = np.zeros(nyears)  # This is the new established area starting from the first rotation end
    area_harvested_agriland = np.zeros(nyears)   # This is the total harvested area plantation for each year's established plantation

    # For each year of new established plantations, accumulate the area,
    # and then count the number of rotation for that year's plantation (there may be multiple harvests in the same area over the course)
    for year in range(year_new_plantation_st, year_new_plantation_ed):
        area_established_new_agriland[year] = area_established_agriland_annual_global
        # divide the rotation length and round down
        nrotation = (year_harvest_ed - year) // rotation_length
        area_harvested_agriland[year] = area_established_agriland_annual_global * nrotation

    # after one rotation period
    area_harvested_new_agriland[rotation_length:] = area_established_agriland_annual_global

    # area_established_agriland = np.cumsum(area_established_new_agriland) # This is to show the accumulate agricultural land
    area_established_new_agriland_accumulate = np.sum(area_established_new_agriland)
    area_harvested_agriland_accumulate = np.sum(area_harvested_agriland)
    area_harvested_new_agriland_accumulate = np.sum(area_harvested_new_agriland)

    # CHECK - area_established_new_agriland_accumulate should EQUAL area_harvested_new_agriland_accumulate
    if area_harvested_new_agriland_accumulate != area_established_new_agriland_accumulate:
        raise ValueError('The total new tropical plantation area does not match!')
    return area_established_new_agriland_accumulate, area_harvested_agriland_accumulate, area_harvested_new_agriland


def run_new_tropical_plantations_scenario(results):
    """
    VERY IMPORTANT FEATURE OF THIS SCRIPT!
    Tropical New Plantation Scenario
    This is the 4th scenario
    require the input from the existing model outputs
    """

    ### New plantation land area assumption
    # We assume the *** 2Mha *** per year of agricultural land are converted to plantation evenly from 2010-2050
    area_established_agriland_annual_global = 2 * 1000000  # Mha per year
    area_established_new_agriland_accumulate, area_harvested_agriland_accumulate, area_harvested_new_agriland = prepare_new_tropical_plantations_area(nyears, rotation_length, area_established_agriland_annual_global)

    ### Read in the country sum parameters
    carbon_global, area_global = prepare_global_outputs_for_new_tropical_scenario(results)
    total_pdv_plantation = carbon_global['S1 regrowth: PDV plantation (mega tC)']  # Total PDV for existing plantation, tC
    total_pdv_secondary_regrowth = carbon_global['S1 regrowth: PDV secondary (mega tC)']  # Total PDV for secondary regrowth scenario, tC
    area_harvested_new_secondary_sum = area_global['S1 regrowth: Secondary area (ha)']  # Total area of secondary harvested for regrowth, ha
    total_wood_secondary = carbon_global['Default: Secondary forest supply wood (mega tC)']     # Total wood from secondary, tC
    total_wood_plantation = carbon_global['Default: Plantation supply wood (mega tC)']     # Total wood from secondary, tC

    ############################################## Calculation #############################################
    ### 1. Calculate Average PDV per hectare for secondary as Total PDV for secondary/Total area of secondary harvested
    pdv_average_secondary_regrowth = total_pdv_secondary_regrowth / area_harvested_new_secondary_sum  # tC/ha

    ### 2. Calculate average yield for secondary as total wood from secondary/ total area of secondary harvested, only harvest once
    yield_average_secondary = total_wood_secondary / area_harvested_new_secondary_sum

    ################################ Aggregated/Weighted Parameters
    # 2023/Jan: Change the rotation year from exactly 10 years to all countries that are below 10 years
    # only tropical countries that are shorter than 10 years rotation period: Brazil, Congo, Ethiopia, Indonesia, Vietnam (Add Ethiopia)
    ### 3. Calculate average tropical plantation wood harvest
    # weighted average of the output per ha for each harvest
    tropical_countries_iso = ['BRA', 'COD', 'ETH', 'IDN', 'VNM']
    # Get the plantation area
    area_plantation_tropical = [results.loc[results['ISO']==iso]['Plantation area (ha)'].values[0] for iso in tropical_countries_iso]
    # Get the output per ha at the 2020 year
    output_ha_tropical = [results.loc[results['ISO']==iso]['Output per ha Agricultural land conversion (tC/ha)'].values[0] for iso in tropical_countries_iso]
    weighted_sum = sum([area_plantation_tropical[i] * output_ha_tropical[i] for i in range(len(output_ha_tropical))])
    # Get the weighted average output per ha for the five countries
    output_ha_tropical_average = weighted_sum / sum(area_plantation_tropical)

    ### 4. Calculate the total wood harvest/production from the new plantation from agricultural land
    # New plantation wood production for 2020-2050, tC, from the 2 Mha per year agricultural land with continuous harvest
    wood_supply_agriland = area_harvested_agriland_accumulate * output_ha_tropical_average

    ### 5. Calculate area reduced due to new plantation as “new plantation wood production/average yield for secondary”
    area_reduced_secondary = wood_supply_agriland / yield_average_secondary

    ### 6. Calculate new total PDV for secondary as Average PDV per hectare for secondary * (Total area of secondary harvested – area reduced due to new plantation)
    total_pdv_secondary_after_replace = pdv_average_secondary_regrowth * (area_harvested_new_secondary_sum - area_reduced_secondary)

    ### 7. Calculate total PDV for NEW plantation from agricultural land.
    # Get the yearly PDV value from the agriland
    total_pdv_agriland_sum_country = []
    # weighted average from the several tropical countries
    for iso in tropical_countries_iso:
        # Global = Global_by_country.Parameters(datafile, country_iso=iso)
        nyears_harvest_settings = Global_by_country.SetupTime(datafile, country_iso=iso, nyears_run_control='harvest')
        nyears_growth_settings = Global_by_country.SetupTime(datafile, country_iso=iso, nyears_run_control='growth')
        ### Default plantation scenarios, (1) secondary harvest regrowth and (2) conversion
        ### Read in global parameters ###
        global_harvest_settings = Global_by_country.Parameters(datafile, nyears_harvest_settings, country_iso=iso)
        global_growth_settings = Global_by_country.Parameters(datafile, nyears_growth_settings, country_iso=iso)
        annual_discounted_value_nyears_agriland = np.zeros((global_growth_settings.nyears, global_harvest_settings.nyears))
        for year in range(global_harvest_settings.nyears):
            #### This is the only line that requires the CHARM model run ####
            annual_discounted_value_nyears_agriland[:, year] = Agricultural_land_tropical_scenario.CarbonTracker(global_growth_settings, year_start_for_PDV=year).annual_discounted_value[:]
        pdv_yearly_agriland = np.sum(annual_discounted_value_nyears_agriland, axis=0)

        total_pdv_agriland = np.zeros((global_harvest_settings.nyears))
        for year in range(global_harvest_settings.nyears):
            total_pdv_agriland[year] = pdv_yearly_agriland[year] * area_harvested_new_agriland[year]
        total_pdv_agriland_sum_country.append(np.sum(total_pdv_agriland))

    # use plantation area to weighted average from the tropical countries
    pdv_weighted_sum = sum([area_plantation_tropical[i] * total_pdv_agriland_sum_country[i] for i in range(len(total_pdv_agriland_sum_country))])
    # Get the weighted average output per ha for the four countries
    total_pdv_tropical_weighted_average = pdv_weighted_sum / sum(area_plantation_tropical)

    ### 8. Calculate global PDV as Total PDV for existing plantation + Total PDV for new plantation + New total PDV for secondary
    global_pdv = total_pdv_plantation + total_pdv_secondary_after_replace + total_pdv_tropical_weighted_average

    # Convert tC to GtCO2 per year.
    carbon_cost_annual = global_pdv / 1000000000 * 44 / 12 / nyears
    # Convert ha to Mha
    updated_secondary_area = (area_harvested_new_secondary_sum - area_reduced_secondary) / 1000000
    new_plantation_area = np.sum(area_harvested_new_agriland) / 1000000

    ### 9. Calculate the total secondary wood supply reduced from the new plantation
    total_wood_secondary_after_replace = total_wood_secondary - wood_supply_agriland
    total_wood_plantation_after_replace = total_wood_plantation + wood_supply_agriland

    return carbon_cost_annual, updated_secondary_area, new_plantation_area, total_wood_secondary_after_replace, total_wood_plantation_after_replace


def calculate_existing_tropical_plantations_numbers():
    """
    Tropical Plantation Equivalent
    require the input from the CST model outputs
    In 2010, pull out the total quantity of wood harvested from NON-plantation forests. Then calculate an average yield for tropical forests in 2010 (tC/ha). Then simply divide the non-plantation quantity by the tropical yield to get the total number of tropical plantation hectares that could replace one year’s worth of global secondary forest harvest.
    """
    # Read in CST demand 2010 existing level
    results = pd.read_excel(datafile, sheet_name='CST_NOSUB_IND')

    ### Read in the country sum parameters
    carbon_global, area_global = prepare_global_outputs_for_new_tropical_scenario(results)
    total_wood_secondary = carbon_global['Default: Secondary forest supply wood (mega tC)']     # Total wood from secondary, tC
    total_wood_plantation = carbon_global['Default: Plantation supply wood (mega tC)']     # Total wood from secondary, tC

    ### Calculate average tropical plantation wood harvest
    # only tropical countries that are 10 years rotation period: Brazil, Congo, Indonesia, Vietnam
    # weighted average of the output per ha for each harvest
    tropical_countries_iso = ['BRA', 'COD', 'ETH', 'IDN', 'VNM']
    # Get the plantation area
    area_plantation_tropical = [results.loc[results['ISO']==iso]['Plantation area (ha)'].values[0] for iso in tropical_countries_iso]
    # Get the output per ha at the 2020 year
    output_ha_tropical = [results.loc[results['ISO']==iso]['Output per ha Agricultural land conversion (tC/ha)'].values[0] for iso in tropical_countries_iso]
    weighted_sum = sum([area_plantation_tropical[i] * output_ha_tropical[i] for i in range(len(output_ha_tropical))])
    # Get the weighted average output per ha for the four countries
    output_ha_tropical_average = weighted_sum / sum(area_plantation_tropical)

    # For cst demand 2010 level
    wood_secondary_2010 = total_wood_secondary / nyears
    area_plantation_tropical_equivalent = wood_secondary_2010 / output_ha_tropical_average
    wood_secondary_share = total_wood_secondary / (total_wood_plantation + total_wood_secondary)

    return total_wood_secondary, wood_secondary_2010, wood_secondary_share, output_ha_tropical_average, area_plantation_tropical_equivalent

# result = calculate_existing_tropical_plantations_numbers()
# print(result)
# exit()


def export_results_to_excel():
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
                carbon_last, secondary_land_last, new_tropical_land_last, secondary_wood_last, plantation_wood_last = run_new_tropical_plantations_scenario(results)
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

    outfile = '{}/data/processed/derivative/CHARM_global_carbon_land_summary - {}.xlsx'.format(root, years_filename)
    # outfile = '{}/CHARM_global_carbon_land_summary - {} - {}.xlsx'.format(outdir, years_filename, exp_filename)

    # Convert to pandas dataframe
    scenarios = ['S1 Secondary forest harvest + regrowth', 'S2 Secondary forest harvest + conversion', 'S3 Secondary forest mixed harvest',
     'S4 New tropical plantations', 'S5 Higher plantation productivity', 'S6 Higher harvest efficiency', 'S7 50% less 2050 wood fuel demand']
    carbon_df = pd.DataFrame(carbon_costs, index=row_index, columns=scenarios)
    write_excel(outfile, 'CO2 (Gt per yr) DR_{}'.format(discount_filename), carbon_df)
    # For land and wood supply, no matter what discount it is, the land area does not change
    if discount_filename == '4p':
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
        write_excel(outfile, 'Land (Mha) DR_{}'.format(discount_filename), area_df)
        write_excel(outfile, 'Wood supply (mega tC) DR_{}'.format(discount_filename), wood_df)

    return

export_results_to_excel()
exit()

def export_results_to_excel_ALL_NOSUB():
    # 2 demand and sub levels x (6+1) scenarios
    carbon_costs = np.zeros((2, 7))
    # 2 demand and sub levels x (6+1) scenarios + 2 columns for plantation areas
    required_area = np.zeros((2, 9))
    # 2 demand and sub levels x (4+1) scenarios x 2
    wood_supply = np.zeros((2, 10))
    row = 0
    row_index = []
    vslp_input_control = 'ALL'
    substitution_mode = 'NOSUB'
    for future_demand_level in ['BAU', 'CST']:
        output_tabname = '{}_{}_{}'.format(future_demand_level, substitution_mode, vslp_input_control)
        row_index.append(output_tabname)
        results = pd.read_excel(datafile, sheet_name=output_tabname)
        carbon_main, land_main = extract_global_outputs_summary(results)
        wood_main = extract_global_wood_supply(results)
        carbon_last, secondary_land_last, new_tropical_land_last, secondary_wood_last, plantation_wood_last = run_new_tropical_plantations_scenario(results)
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

    outfile = '{}/CHARM_global_carbon_land_summary - {} - {}.xlsx'.format(outdir, years_filename, exp_filename)

    # Convert to pandas dataframe
    scenarios = ['S1 Secondary forest harvest + regrowth', 'S2 Secondary forest harvest + conversion', 'S3 Secondary forest mixed harvest',
     'S4 New tropical plantations', 'S5 Higher plantation productivity', 'S6 Higher harvest efficiency', 'S7 50% less 2050 wood fuel demand']
    carbon_df = pd.DataFrame(carbon_costs, index=row_index, columns=scenarios)
    write_excel(outfile, 'CO2 (Gt per yr) DR_{}'.format(discount_filename), carbon_df)
    # For land and wood supply, no matter what discount it is, the land area does not change
    if discount_filename == '4p':
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
        write_excel(outfile, 'Land (Mha) DR_{}'.format(discount_filename), area_df)
        write_excel(outfile, 'Wood supply (mega tC) DR_{}'.format(discount_filename), wood_df)

    return

# export_results_to_excel_ALL_NOSUB()
# exit()

def collect_all_discount_rates_results():
    "For Appendix 3"
    # infile = '{}/data/processed/derivative/CHARM_global_carbon_land_summary.xlsx'.format(root)
    infile = '{}/data/processed/derivative/CHARM_global_carbon_land_summary - {}.xlsx'.format(root, years_filename)
    df_list = []
    for dr in ('0p', '2p', '4p', '6p'):
        carbon = pd.read_excel(infile, sheet_name='CO2 (Gt per yr) DR_{}'.format(dr), index_col=0)
        carbon_sel = carbon.loc[['BAU_NOSUB_ALL', 'BAU_SUBON_ALL']]
        df_list.append(carbon_sel.rename(index={'BAU_NOSUB_ALL': 'Gross emissions', 'BAU_SUBON_ALL':'Net emissions including substitution savings'}))
    big_table = pd.concat(df_list)
    big_table.to_csv('{}/data/processed/derivative/carbon_results_all_discountrate - {}.csv'.format(root, years_filename))

# collect_all_discount_rates_results()
# exit()


def export_secondary_carbon_costs_to_excel():
    "This is to compare 100yr and 40yr on secondary carbon costs only, excluding plantation"
    # 4 demand and 2x4 scenarios
    carbon_costs = np.zeros((4, 8))
    col_index = []
    col = 0
    vslp_input_control = 'ALL'
    for years_filename in ['40yr', '100yr']:
        for discount_filename in ['0p', '2p', '4p', '6p']:
            datafile = '{}/data/processed/CHARM regional - DR_{} - {} - Feb 10 2022.xlsx'.format(root, discount_filename, years_filename)
            col_index.append('{}-{}'.format(years_filename, discount_filename))
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
    carbon_df = pd.DataFrame(carbon_costs, index=row_index, columns=col_index)
    carbon_df.to_csv('{}/data/processed/derivative/carbon_results_40vs100yr.csv'.format(root))

    return

# export_secondary_carbon_costs_to_excel()
# exit()