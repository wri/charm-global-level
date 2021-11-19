#!/usr/bin/env python
"""
This is the clean-version main file for model execution.
"""
__author__ = "Liqing Peng"
__copyright__ = "Copyright (C) 2020-2021 World Resources Institute, The Carbon Harvest Model (CHARM) Project"
__credits__ = ["Liqing Peng", "Jessica Zionts", "Tim Searchinger", "Richard Waite"]
__license__ = "Polyform Strict License 1.0.0"
__version__ = "2021.11.1"
__maintainer__ = "Liqing Peng"
__email__ = "liqing.peng@wri.org"
__status__ = "Dev"

import numpy as np
import pandas as pd
import Global_by_country, Secondary_conversion_scenario, Secondary_regrowth_scenario, Plantation_counterfactual_secondary_plantation_age_scenario, Land_area_calculator

root = '../../'

#############################################RUNNING MODEL###########################################

def run_model():
    """
    This is a driver for running global analysis for forestry land and carbon consequences.
    """
    # Read input/output data excel file.
    datafile = '{}/data/processed/CHARM_global.xlsx'.format(root)
    # Read in countries
    countries = pd.read_excel(datafile, sheet_name='Inputs', usecols="A:B", skiprows=1)
    # Read in input data
    input_data = pd.read_excel(datafile, sheet_name='Inputs', skiprows=1)
    # If the cell has formula, it will be read as NaN

    def single_run_with_combination_input(future_demand_level_input='BAU', substitution_mode_input='SUBON', vslp_input_control_input='ALL'):
        """
        This function generates the 30 countries results for each scenario, depending on the combination of below parameters.
        :param future_demand_level_input: select future demand level from "BAU" business-as-usual or "CST": constant demand
        :param substitution_mode_input: select substitution mode from "SUBON" with substitution or "NOSUB" gross carbon impacts
        :param vslp_input_control_input: select VSLP option from "ALL" total roundwood (VSLP_WFL+VSLP_IND) or "IND" industrial roundwood (VSLP_IND)
        :return:
        """
        # Initiate the output variables.
        countrynames, codes = [], []
        secondary_wood_default, plantation_wood_default = [], []
        pdv_per_ha_plantation_default, pdv_per_ha_regrowth, pdv_per_ha_conversion = [], [], []
        area_plantation = []
        area_regrowth, carbon_regrowth, carbon_existing_plantation, carbon_secondary_regrowth = [], [], [], []
        area_conversion, carbon_conversion = [], []

        # For each country, calculate the results for all scenarios. Each variable collects a list of the countries' results.
        for country, code in zip(countries['Country'], countries['ISO']):
            # Test if the parameters are set up for this country, if there is one parameter missing, no calculation will be done for this country.
            input_country = input_data.loc[input_data['Country'] == country]
            input_country = input_country.drop(['Emissions substitution factor for LLP (tC saved/tons C in LLP)'], axis=1)
            if input_country.isnull().values.any():
                print("Please fill in the abbreviation and all the missing parameters for country '{}'!".format(country))
            else:
                ################################### Execute model runs ##################################
                ### Default plantation scenarios, (1) secondary harvest regrowth and (2) conversion
                ### Read in global parameters ###
                global_settings = Global_by_country.Parameters(datafile, country_iso=code, future_demand_level=future_demand_level_input, substitution_mode=substitution_mode_input, vslp_input_control=vslp_input_control_input)
                # run different policy scenarios
                result_plantation_default = Plantation_counterfactual_secondary_plantation_age_scenario.CarbonTracker(global_settings)
                result_conversion_default = Secondary_conversion_scenario.CarbonTracker(global_settings)
                result_regrowth_default = Secondary_regrowth_scenario.CarbonTracker(global_settings)

                # run the land area calculator
                LAC_default = Land_area_calculator.LandCalculator(global_settings, plantation_counterfactual_code='secondary_plantation_age')

                ################################### Prepare output ##################################
                countrynames.append(country)
                codes.append(code)

                # Carbon tracker
                pdv_per_ha_plantation_default.append(np.sum(result_plantation_default.annual_discounted_value))
                pdv_per_ha_regrowth.append(np.sum(result_regrowth_default.annual_discounted_value))
                pdv_per_ha_conversion.append(np.sum(result_conversion_default.annual_discounted_value))

                # Default situation
                secondary_wood_default.append(sum(LAC_default.output_need_secondary / 1000000))
                plantation_wood_default.append(sum(LAC_default.product_total_carbon) / 1000000 - sum(LAC_default.output_need_secondary) / 1000000)
                area_plantation.append(sum(LAC_default.area_harvested_new_plantation))

                # Scenario 1
                area_regrowth.append(sum(LAC_default.area_harvested_new_secondary_regrowth_combined))
                carbon_regrowth.append(LAC_default.total_pdv_plantation_secondary_regrowth)
                carbon_existing_plantation.append(LAC_default.total_pdv_plantation_sum)
                carbon_secondary_regrowth.append(LAC_default.total_pdv_secondary_regrowth_sum)

                # Scenario 2
                area_conversion.append(sum(LAC_default.area_harvested_new_secondary_conversion))
                carbon_conversion.append(LAC_default.total_pdv_plantation_secondary_conversion)

        # Save to the excel file
        dataframe = pd.DataFrame({'Country': countrynames,
                                  'ISO': codes,
                                  # Save PDV
                                  'PDV per ha Secondary middle regrowth (tC/ha)': pdv_per_ha_regrowth,
                                  'PDV per ha Secondary conversion (tC/ha)': pdv_per_ha_conversion,
                                  'PDV per ha Plantation (tC/ha)': pdv_per_ha_plantation_default,

                                  # Save wood supply
                                  'Default: Plantation supply wood (mega tC)': plantation_wood_default,
                                  'Default: Secondary forest supply wood (mega tC)': secondary_wood_default,

                                  # Save plantation area
                                  'Plantation area (ha)': area_plantation,

                                  # S1
                                  'S1 regrowth: Secondary area (ha)': area_regrowth,
                                  'S1 regrowth: total PDV (mega tC)': carbon_regrowth,

                                  # S2
                                  'S2 conversion: Secondary area (ha)': area_conversion,
                                  'S2 conversion: total PDV (mega tC)': carbon_conversion,

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

        # Prepare output tab name
        output_tabname = '{}_{}_{}'.format(future_demand_level_input, substitution_mode_input, vslp_input_control_input)
        write_excel(datafile, output_tabname, dataframe)


    ################## Run the experiments ###################
    # vslp_input_control options ['ALL', 'IND', 'WFL']
    # substitution_mode options ['NOSUB', 'SUBON']
    # future_demand_level options ['BAU', 'CST']
    single_run_with_combination_input(future_demand_level_input='BAU',
                                      substitution_mode_input='SUBON',
                                      vslp_input_control_input='ALL')

    return

if __name__ == "__main__":
    run_model()
