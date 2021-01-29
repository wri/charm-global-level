#!/usr/bin/env python
__author__ = "Liqing Peng, Jessica Zionts, Tim Searchinger"
__copyright__ = "Copyright (C) 2020 WRI, The Carbon Harvest Model (CHarM) Project"
__maintainer__ = "Liqing Peng"
__email__ = "liqing.peng@wri.org"

import numpy as np
import pandas as pd
import Global_by_country, Plantation_scenario, Secondary_conversion_scenario, Secondary_regrowth_scenario, Land_area_calculator
# import Pasture_zero_counterfactual_scenario, Pasture_with_counterfactual_scenario
import Plantation_counterfactual_secondary_historic_scenario, Plantation_counterfactual_secondary_plantation_age_scenario, Plantation_counterfactual_unharvested_scenario


################################################### TESTING ####################################################

root = '../../'

def test_carbon_tracker():
    "TEST Carbon tracker"
    # set up the country
    iso = 'USA'
    # datafile = '{}/data/processed/CHARM regional - BAU - Jan 22.xlsx'.format(root)
    datafile = '{}/data/processed/CHARM regional - BAU SF_1.2 - Jan 26.xlsx'.format(root)
    global_settings = Global_by_country.Parameters(datafile, country_iso=iso)
    # Plantation_scenario.CarbonTracker(global_settings, year_start_for_PDV=0).plot_C_pools_counterfactual_print_PDV()
    # Plantation_counterfactual_secondary_plantation_age_scenario.CarbonTracker(global_settings, year_start_for_PDV=0).plot_C_pools_counterfactual_print_PDV()
    Secondary_conversion_scenario.CarbonTracker(global_settings, year_start_for_PDV=0).plot_C_pools_counterfactual_print_PDV()
    # Secondary_regrowth_scenario.CarbonTracker(global_settings, year_start_for_PDV=0).plot_C_pools_counterfactual_print_PDV()

    return

# test_carbon_tracker()
# exit()

def test_land_area_calculator():
    "TEST land area calculator"
    iso = 'BRA'
    datafile = '{}/data/processed/CHARM regional - BAU SF_1.2 - Jan 26.xlsx'.format(root)
    global_settings = Global_by_country.Parameters(datafile, country_iso=iso)
    # run the land area calculator
    LAC = Land_area_calculator.LandCalculator(global_settings) #, plantation_counterfactual_code='')
    # print("T PDV conversion", LAC.total_pdv_plantation_secondary_conversion)
    # print("T PDV regrowth", LAC.total_pdv_plantation_secondary_regrowth)
    # print("Area conversion", sum(LAC.area_harvested_new_secondary_conversion))
    # print("Area regrowth", sum(LAC.area_harvested_new_secondary_regrowth))

    return
# test_land_area_calculator()
# exit()


#############################################RUNNING MODEL###########################################

def run_model_legacy():

    datafile = '{}/data/processed/CHARM input v3 - old plantation scenario.xlsx'.format(root)

    scenarios = pd.read_excel(datafile, sheet_name='Inputs', usecols="A:B", skiprows=1)
    input_data = pd.read_excel(datafile, sheet_name='Inputs', skiprows=1)

    scenarionames, codes, pdv_per_ha_plantation, pdv_per_ha_conversion, pdv_per_ha_regrowth, plantation_share, secondary_share, pdv_conversion, pdv_regrowth, area_conversion, area_regrowth = [], [], [], [], [], [], [], [], [], [], []
    for scenario, code in zip(scenarios['Country'], scenarios['ISO']):
        # Test if the parameters are set up for this scenario, if there is one missing, will not do any calculation
        input_scenario = input_data.loc[input_data['Country'] == scenario]
        input_scenario = input_scenario.drop(['Emissions substitution factor for LLP (tC saved/tons C in LLP)'], axis=1)
        if input_scenario.isnull().values.any():
            print("Please fill in the abbreviation and all the missing parameters for scenario '{}'!".format(scenario))
        else:
            # read in global parameters
            global_settings = Global_by_country.Parameters(datafile, country_iso=code)
            # run different policy scenarios
            result_plantation = Plantation_scenario.CarbonTracker(global_settings)
            result_secondary_conversion = Secondary_conversion_scenario.CarbonTracker(global_settings)
            result_secondary_regrowth = Secondary_regrowth_scenario.CarbonTracker(global_settings)
            # run the land area calculator
            LAC = Land_area_calculator.LandCalculator(global_settings)

            # Prepare output
            scenarionames.append(scenario)
            codes.append(code)
            pdv_per_ha_plantation.append(np.sum(result_plantation.annual_discounted_value))
            pdv_per_ha_conversion.append(np.sum(result_secondary_conversion.annual_discounted_value))
            pdv_per_ha_regrowth.append(np.sum(result_secondary_regrowth.annual_discounted_value))
            pdv_conversion.append(LAC.total_pdv_plantation_secondary_conversion)
            pdv_regrowth.append(LAC.total_pdv_plantation_secondary_regrowth)
            area_conversion.append(sum(LAC.area_harvested_new_secondary_conversion))
            area_regrowth.append(sum(LAC.area_harvested_new_secondary_regrowth))
            secondary_share.append(sum(LAC.output_need_secondary)/sum(LAC.product_total_carbon)*100)
            plantation_share.append(100-sum(LAC.output_need_secondary)/sum(LAC.product_total_carbon)*100)


    # Save to the output
    dataframe = pd.DataFrame({'Country': scenarionames,
                              'ISO': codes,
                              'PDV Plantation (tC/ha)': pdv_per_ha_plantation,
                              'PDV Secondary forest conversion (tC/ha)': pdv_per_ha_conversion,
                              'PDV Secondary regrowth conversion (tC/ha)': pdv_per_ha_regrowth,
                              'PDV conversion scenario (tC)': pdv_conversion,
                              'PDV regrowth scenario (tC)': pdv_regrowth,
                              'Secondary area conversion (ha)': area_conversion,
                              'Secondary area regrowth (ha)': area_regrowth,
                              'Plantation wood production share (%)': plantation_share,
                              'Secondary wood production share (%)': secondary_share
                              })

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
                dataframe.to_excel(writer, sheet_name=sheetname, index=False)
                writer.save()

    write_excel(datafile, 'Outputs', dataframe)

    return

# run_model()


def run_model_new_plantation_scenarios():
    # datafile = '{}/data/processed/CHARM regional - BAU - Jan 25.xlsx'.format(root)
    # datafile = '{}/data/processed/CHARM regional - constant demand - Jan 25.xlsx'.format(root)

    # datafile = '{}/data/processed/CHARM regional - BAU SF_1.2 - Jan 26.xlsx'.format(root)
    # datafile = '{}/data/processed/CHARM regional - BAU SF_0 - Jan 26.xlsx'.format(root)
    # datafile = '{}/data/processed/CHARM regional - constant demand SF_1.2 - Jan 26.xlsx'.format(root)
    datafile = '{}/data/processed/CHARM regional - constant demand SF_0 - Jan 26.xlsx'.format(root)

    scenarios = pd.read_excel(datafile, sheet_name='Inputs', usecols="A:B", skiprows=1)
    input_data = pd.read_excel(datafile, sheet_name='Inputs', skiprows=1)

    scenarionames, codes = [], []
    pdv_per_ha_conversion, pdv_per_ha_regrowth = [], []
    area_conversion_legacy, area_regrowth_legacy, area_plantation = [], [], []
    secondary_wood, plantation_wood = [], []
    pdv_per_ha_plantation_legacy, pdv_conversion_legacy, pdv_regrowth_legacy = [], [], []
    pdv_per_ha_plantation_secondary_historic, pdv_conversion_secondary_historic, pdv_regrowth_secondary_historic = [], [], []
    pdv_per_ha_plantation_secondary_plantation_age, pdv_conversion_secondary_plantation_age, pdv_regrowth_secondary_plantation_age = [], [], []
    pdv_per_ha_plantation_unharvested, pdv_conversion_unharvested, pdv_regrowth_unharvested = [], [], []

    for scenario, code in zip(scenarios['Country'], scenarios['ISO']):
        # Test if the parameters are set up for this scenario, if there is one missing, will not do any calculation
        input_scenario = input_data.loc[input_data['Country'] == scenario]
        input_scenario = input_scenario.drop(['Emissions substitution factor for LLP (tC saved/tons C in LLP)'], axis=1)
        if input_scenario.isnull().values.any():
            print("Please fill in the abbreviation and all the missing parameters for scenario '{}'!".format(scenario))
        else:
            # read in global parameters
            global_settings = Global_by_country.Parameters(datafile, country_iso=code)
            # run different policy scenarios
            result_plantation_legacy = Plantation_scenario.CarbonTracker(global_settings)
            # FIXME New plantation scenarios
            result_plantation_secondary_historic = Plantation_counterfactual_secondary_historic_scenario.CarbonTracker(
                global_settings)
            result_plantation_secondary_plantation_age = Plantation_counterfactual_secondary_plantation_age_scenario.CarbonTracker(
                global_settings)
            result_plantation_unharvested = Plantation_counterfactual_unharvested_scenario.CarbonTracker(
                global_settings)

            result_secondary_conversion = Secondary_conversion_scenario.CarbonTracker(global_settings)
            result_secondary_regrowth = Secondary_regrowth_scenario.CarbonTracker(global_settings)

            # run the land area calculator
            # new plantation scenarios
            LAC_legacy = Land_area_calculator.LandCalculator(global_settings)
            LAC_secondary_historic = Land_area_calculator.LandCalculator(global_settings,plantation_counterfactual_code='secondary_historic')
            LAC_secondary_plantation_age = Land_area_calculator.LandCalculator(global_settings, plantation_counterfactual_code='secondary_plantation_age')
            LAC_unharvested = Land_area_calculator.LandCalculator(global_settings, plantation_counterfactual_code='unharvested')

            # Prepare output
            scenarionames.append(scenario)
            codes.append(code)

            pdv_per_ha_conversion.append(np.sum(result_secondary_conversion.annual_discounted_value))
            pdv_per_ha_regrowth.append(np.sum(result_secondary_regrowth.annual_discounted_value))

            # Plantation scenarios
            pdv_per_ha_plantation_legacy.append(np.sum(result_plantation_legacy.annual_discounted_value))
            pdv_conversion_legacy.append(LAC_legacy.total_pdv_plantation_secondary_conversion)
            pdv_regrowth_legacy.append(LAC_legacy.total_pdv_plantation_secondary_regrowth)

            area_conversion_legacy.append(sum(LAC_legacy.area_harvested_new_secondary_conversion))
            area_regrowth_legacy.append(sum(LAC_legacy.area_harvested_new_secondary_regrowth))
            area_plantation.append(sum(LAC_legacy.area_harvested_new_plantation))

            secondary_wood.append(sum(LAC_legacy.output_need_secondary)/1000000)
            plantation_wood.append(sum(LAC_legacy.product_total_carbon)/1000000 - sum(LAC_legacy.output_need_secondary)/1000000)

            pdv_per_ha_plantation_secondary_historic.append(np.sum(result_plantation_secondary_historic.annual_discounted_value))
            pdv_conversion_secondary_historic.append(LAC_secondary_historic.total_pdv_plantation_secondary_conversion)
            pdv_regrowth_secondary_historic.append(LAC_secondary_historic.total_pdv_plantation_secondary_regrowth)

            pdv_per_ha_plantation_secondary_plantation_age.append(np.sum(result_plantation_secondary_plantation_age.annual_discounted_value))
            pdv_conversion_secondary_plantation_age.append(LAC_secondary_plantation_age.total_pdv_plantation_secondary_conversion)
            pdv_regrowth_secondary_plantation_age.append(LAC_secondary_plantation_age.total_pdv_plantation_secondary_regrowth)

            pdv_per_ha_plantation_unharvested.append(np.sum(result_plantation_unharvested.annual_discounted_value))
            pdv_conversion_unharvested.append(LAC_unharvested.total_pdv_plantation_secondary_conversion)
            pdv_regrowth_unharvested.append(LAC_unharvested.total_pdv_plantation_secondary_regrowth)


    # Save to the output
    dataframe = pd.DataFrame({'Country': scenarionames,
                              'ISO': codes,

                              'Secondary area conversion (ha)': area_conversion_legacy,
                              'Secondary area regrowth (ha)': area_regrowth_legacy,
                              'Plantation area (ha)': area_plantation,

                              'Plantation supply wood (mega tC)': plantation_wood,
                              'Secondary supply wood (mega tC)': secondary_wood,

                              'PDV per ha Secondary conversion (tC/ha)': pdv_per_ha_conversion,
                              'PDV per ha Secondary regrowth (tC/ha)': pdv_per_ha_regrowth,
                              'PDV per ha Plantation old version (tC/ha)': pdv_per_ha_plantation_legacy,
                              'PDV per ha Plantation secondary historic (tC/ha)': pdv_per_ha_plantation_secondary_historic,
                              'PDV per ha Plantation secondary plantation age (tC/ha)': pdv_per_ha_plantation_secondary_plantation_age,
                              'PDV per ha Plantation unharvested (tC/ha)': pdv_per_ha_plantation_unharvested,

                              'Total PDV conversion plantation old version (mega tC)': pdv_conversion_legacy,
                              'Total PDV conversion plantation secondary historic (mega tC)': pdv_conversion_secondary_historic,
                              'Total PDV conversion plantation secondary plantation age (mega tC)': pdv_conversion_secondary_plantation_age,
                              'Total PDV conversion plantation unharvested (mega tC)': pdv_conversion_unharvested,

                              'Total PDV regrowth plantation old version (mega tC)': pdv_regrowth_legacy,
                              'Total PDV regrowth plantation secondary historic (mega tC)': pdv_regrowth_secondary_historic,
                              'Total PDV regrowth plantation secondary plantation age (mega tC)': pdv_regrowth_secondary_plantation_age,
                              'Total PDV regrowth plantation unharvested (mega tC)': pdv_regrowth_unharvested,

                              })

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
                dataframe.to_excel(writer, sheet_name=sheetname, index=False)
                writer.save()

    write_excel(datafile, 'Outputs', dataframe)

    return


run_model_new_plantation_scenarios()