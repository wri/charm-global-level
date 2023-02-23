#!/usr/bin/env python
"""
This is the main file for model execution.
"""
__author__ = "Liqing Peng"
__copyright__ = "Copyright (C) 2023 World Resources Institute, The Carbon Harvest Model (CHARM) Project"
__credits__ = ["Liqing Peng", "Jessica Zionts", "Tim Searchinger", "Richard Waite"]
__license__ = "MIT"
__version__ = "2023.2"
__maintainer__ = "Liqing Peng"
__email__ = "liqing.peng@wri.org"
__status__ = "Dev"


import numpy as np
import pandas as pd
import Global_by_country, Plantation_counterfactual_secondary_plantation_age_scenario, Secondary_conversion_scenario, Secondary_regrowth_scenario, Secondary_mature_regrowth_scenario, Agricultural_land_tropical_scenario, Land_area_calculator, Carbon_cost_calculator

### Datafile
root = '../..'

#############################################RUNNING MODEL###########################################
def run_model_all_scenarios(years, discount_rate, version, path):
    """
    Created and Edited: 2022/01
    This is an updated driver for running global analysis for forestry land and carbon consequences.
    Adding several scenarios based on the run_model_five_scenarios
    """
    ## Standard runs
    # Read input/output data excel file.
    datafile = '{}/data/processed/CHARM regional - YR_{} - DR_{} - V{}.xlsx'.format(path, years, discount_rate, version)

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
        # country name, code
        countrynames, codes = [], []
        # wood supply
        secondary_wood_default, plantation_wood_default = [], []
        secondary_wood_highGR, plantation_wood_highGR = [], []   # This will increase the percentage of wood from plantation, reduce the share of secondary
        secondary_wood_optimalSL, plantation_wood_optimalSL = [], []  # This will increase the share of secondary
        secondary_wood_WFL50less, plantation_wood_WFL50less = [], []  # This will change the total wood supply for both secondary and plantation
        # pdv
        pdv_per_ha_plantation_default, pdv_per_ha_plantation_highGR = [], []
        pdv_per_ha_regrowth, pdv_per_ha_regrowth_mature, pdv_per_ha_regrowth_optimalSL = [], [], []
        pdv_per_ha_conversion = []
        pdv_per_ha_agriland = []
        # area
        area_plantation = []
        area_regrowth, carbon_regrowth, carbon_existing_plantation, carbon_secondary_regrowth = [], [], [], []
        area_conversion, carbon_conversion = [], []
        area_mixture, carbon_mixture, area_mixture_middle, area_mixture_mature = [], [], [], []
        area_regrowth_highGR, carbon_regrowth_highGR = [], []
        area_regrowth_optimalSL, carbon_regrowth_optimalSL = [], []
        area_regrowth_WFL50less, carbon_regrowth_WFL50less = [], []

        output_ha_agriland = []

        # For each country, calculate the results for all scenarios. Each variable collects a list of the countries' results.
        for country, code in zip(countries['Country'], countries['ISO']):
            # Test if the parameters are set up for this country, if there is one parameter missing, no calculation will be done for this country.
            input_country = input_data.loc[input_data['Country'] == country]
            input_country = input_country.drop(['Emissions substitution factor for LLP (tC saved/tons C in LLP)'], axis=1)
            if input_country.isnull().values.any():
                print("Please fill in the abbreviation and all the missing parameters for country '{}'!".format(country))
            else:
                ################################### Execute model runs ##################################
                nyears_harvest_settings = Global_by_country.SetupTime(datafile, country_iso=code, nyears_run_control='harvest')
                nyears_growth_settings = Global_by_country.SetupTime(datafile, country_iso=code, nyears_run_control='growth')
                ### Default plantation scenarios, (1) secondary harvest regrowth and (2) conversion
                ### Read in global parameters ###
                global_harvest_settings = Global_by_country.Parameters(datafile, nyears_harvest_settings,
                                                                        country_iso=code,
                                                                       future_demand_level=future_demand_level_input,
                                                                       substitution_mode=substitution_mode_input,
                                                                       vslp_input_control=vslp_input_control_input)
                global_growth_settings = Global_by_country.Parameters(datafile, nyears_growth_settings,
                                                                       country_iso=code,
                                                                       future_demand_level=future_demand_level_input,
                                                                       substitution_mode=substitution_mode_input,
                                                                       vslp_input_control=vslp_input_control_input)
                # run different policy scenarios
                result_plantation_default = Plantation_counterfactual_secondary_plantation_age_scenario.CarbonTracker(global_harvest_settings)
                result_conversion_default = Secondary_conversion_scenario.CarbonTracker(global_harvest_settings)
                result_regrowth_default = Secondary_regrowth_scenario.CarbonTracker(global_harvest_settings)
                result_agriland_default = Agricultural_land_tropical_scenario.CarbonTracker(global_harvest_settings)

                # run the land area calculator
                LAC_default = Land_area_calculator.LandCalculator(global_harvest_settings)
                if global_harvest_settings.rotation_length_harvest <= 10:
                    output_ha_agriland_default = LAC_default.output_ha_agriland[global_harvest_settings.year_index_harvest_plantation[1]-1]
                else:
                    output_ha_agriland_default = 0
                # run the carbon cost calculator
                CCC_default = Carbon_cost_calculator.CarbonCalculator(global_harvest_settings, global_growth_settings, LAC_default)


                ### scenario (3) secondary harvest regrowth: 50% middle aged and 50% mature secondary forest
                ### Read in global parameters ###
                global_harvest_settings = Global_by_country.Parameters(datafile, nyears_harvest_settings,
                                                                       country_iso=code,
                                                               future_demand_level=future_demand_level_input,
                                                               substitution_mode=substitution_mode_input,
                                                               vslp_input_control=vslp_input_control_input,
                                                               secondary_mature_wood_share=0.5)
                global_growth_settings = Global_by_country.Parameters(datafile, nyears_growth_settings,
                                                                       country_iso=code,
                                                                       future_demand_level=future_demand_level_input,
                                                                       substitution_mode=substitution_mode_input,
                                                                       vslp_input_control=vslp_input_control_input,
                                                                       secondary_mature_wood_share=0.5)
                # run different policy scenarios
                # result_plantation_mixture = Plantation_counterfactual_secondary_plantation_age_scenario.CarbonTracker(global_settings)
                # result_regrowth_mixture = Secondary_regrowth_scenario.CarbonTracker(global_settings)
                result_regrowth_mature_mixture = Secondary_mature_regrowth_scenario.CarbonTracker(global_harvest_settings)

                # run the land area calculator
                LAC_mixture = Land_area_calculator.LandCalculator(global_harvest_settings)
                # run the carbon cost calculator
                CCC_mixture = Carbon_cost_calculator.CarbonCalculator(global_harvest_settings, global_growth_settings, LAC_mixture)

                ### scenario (4) secondary harvest regrowth: 125% productivity increase in plantation
                ### Read in global parameters ###
                global_harvest_settings = Global_by_country.Parameters(datafile, nyears_harvest_settings,
                                                               country_iso=code,
                                                               future_demand_level=future_demand_level_input,
                                                               substitution_mode=substitution_mode_input,
                                                               vslp_input_control=vslp_input_control_input,
                                                               plantation_growth_increase_ratio=1.25)
                global_growth_settings = Global_by_country.Parameters(datafile, nyears_growth_settings,
                                                                       country_iso=code,
                                                                       future_demand_level=future_demand_level_input,
                                                                       substitution_mode=substitution_mode_input,
                                                                       vslp_input_control=vslp_input_control_input,
                                                                       plantation_growth_increase_ratio=1.25)
                # run different policy scenarios
                result_plantation_highGR = Plantation_counterfactual_secondary_plantation_age_scenario.CarbonTracker(
                    global_harvest_settings)

                # run the land area calculator
                LAC_highGR = Land_area_calculator.LandCalculator(global_harvest_settings)
                # run the carbon cost calculator
                CCC_highGR = Carbon_cost_calculator.CarbonCalculator(global_harvest_settings, global_growth_settings, LAC_highGR)

                ### scenario (5) secondary harvest regrowth: optimal slash rate in tropical secondary forests
                ### Read in global parameters ###
                global_harvest_settings = Global_by_country.Parameters(datafile, nyears_harvest_settings,
                                                                       country_iso=code,
                                                                       future_demand_level=future_demand_level_input,
                                                                       substitution_mode=substitution_mode_input,
                                                                       vslp_input_control=vslp_input_control_input,
                                                                       slash_rate_mode='optimal')
                global_growth_settings = Global_by_country.Parameters(datafile, nyears_growth_settings,
                                                                       country_iso=code,
                                                                       future_demand_level=future_demand_level_input,
                                                                       substitution_mode=substitution_mode_input,
                                                                       vslp_input_control=vslp_input_control_input,
                                                                       slash_rate_mode='optimal')
                # run different policy scenarios
                result_regrowth_optimalSL = Secondary_regrowth_scenario.CarbonTracker(global_harvest_settings)
                # run the land area calculator
                LAC_optimalSL = Land_area_calculator.LandCalculator(global_harvest_settings)
                # run the carbon cost calculator
                CCC_optimalSL = Carbon_cost_calculator.CarbonCalculator(global_harvest_settings, global_growth_settings, LAC_optimalSL)

                ### scenario (6) secondary harvest regrowth: 50% reduction in VSLP-WFL production
                # read in global parameters
                global_harvest_settings = Global_by_country.Parameters(datafile, nyears_harvest_settings,
                                                               country_iso=code,
                                                               future_demand_level=future_demand_level_input,
                                                               substitution_mode=substitution_mode_input,
                                                               vslp_input_control=vslp_input_control_input,
                                                               vslp_future_demand='WFL50less')
                global_growth_settings = Global_by_country.Parameters(datafile, nyears_growth_settings,
                                                                       country_iso=code,
                                                                       future_demand_level=future_demand_level_input,
                                                                       substitution_mode=substitution_mode_input,
                                                                       vslp_input_control=vslp_input_control_input,
                                                                       vslp_future_demand='WFL50less')
                # run the land area calculator
                LAC_WFL50less = Land_area_calculator.LandCalculator(global_harvest_settings)
                # run the carbon cost calculator
                CCC_WFL50less = Carbon_cost_calculator.CarbonCalculator(global_harvest_settings, global_growth_settings, LAC_WFL50less)

                ################################### Prepare output ##################################
                countrynames.append(country)
                codes.append(code)

                # Carbon tracker
                pdv_per_ha_plantation_default.append(np.sum(result_plantation_default.annual_discounted_value))
                pdv_per_ha_regrowth.append(np.sum(result_regrowth_default.annual_discounted_value))
                pdv_per_ha_conversion.append(np.sum(result_conversion_default.annual_discounted_value))
                pdv_per_ha_regrowth_mature.append(np.sum(result_regrowth_mature_mixture.annual_discounted_value))
                pdv_per_ha_plantation_highGR.append(np.sum(result_plantation_highGR.annual_discounted_value))
                pdv_per_ha_regrowth_optimalSL.append(np.sum(result_regrowth_optimalSL.annual_discounted_value))
                pdv_per_ha_agriland.append(np.sum(result_agriland_default.annual_discounted_value))

                # Get output per ha for new plantation
                output_ha_agriland.append(output_ha_agriland_default)

                # Default situation
                secondary_wood_default.append(sum(LAC_default.output_need_secondary / 1000000))
                plantation_wood_default.append(sum(LAC_default.product_total_carbon) / 1000000 - sum(LAC_default.output_need_secondary) / 1000000)
                area_plantation.append(sum(CCC_default.area_harvested_new_plantation))

                # Scenario 1
                area_regrowth.append(sum(LAC_default.area_harvested_new_secondary_regrowth_combined))
                carbon_regrowth.append(CCC_default.total_pdv_plantation_secondary_regrowth)
                carbon_existing_plantation.append(CCC_default.total_pdv_plantation_sum)
                carbon_secondary_regrowth.append(CCC_default.total_pdv_secondary_regrowth_sum)

                # Scenario 2
                area_conversion.append(sum(LAC_default.area_harvested_new_secondary_conversion))
                carbon_conversion.append(CCC_default.total_pdv_plantation_secondary_conversion)

                # Scenario 3: 50:50 secondary supply
                area_mixture.append(sum(LAC_mixture.area_harvested_new_secondary_regrowth_combined))
                carbon_mixture.append(CCC_mixture.total_pdv_plantation_secondary_regrowth)
                area_mixture_middle.append(sum(LAC_mixture.area_harvested_new_secondary_regrowth))
                area_mixture_mature.append(sum(LAC_mixture.area_harvested_new_secondary_mature_regrowth))

                # Scenario 4: Plantation productivity increase
                # Productivity increase
                secondary_wood_highGR.append(sum(LAC_highGR.output_need_secondary / 1000000))
                plantation_wood_highGR.append(sum(LAC_highGR.product_total_carbon) / 1000000 - sum(LAC_highGR.output_need_secondary) / 1000000)
                area_regrowth_highGR.append(sum(LAC_highGR.area_harvested_new_secondary_regrowth_combined))
                carbon_regrowth_highGR.append(CCC_highGR.total_pdv_plantation_secondary_regrowth)

                # Scenario 5: Secondary forest slash rate reduction
                # Productivity increase
                secondary_wood_optimalSL.append(sum(LAC_optimalSL.output_need_secondary / 1000000))
                plantation_wood_optimalSL.append(sum(LAC_optimalSL.product_total_carbon) / 1000000 - sum(LAC_optimalSL.output_need_secondary) / 1000000)
                area_regrowth_optimalSL.append(sum(LAC_optimalSL.area_harvested_new_secondary_regrowth_combined))
                carbon_regrowth_optimalSL.append(CCC_optimalSL.total_pdv_plantation_secondary_regrowth)

                # Scenario 6: VSLP-WFL 50% reduction
                secondary_wood_WFL50less.append(sum(LAC_WFL50less.output_need_secondary / 1000000))
                plantation_wood_WFL50less.append( sum(LAC_WFL50less.product_total_carbon) / 1000000 - sum(LAC_WFL50less.output_need_secondary) / 1000000)
                area_regrowth_WFL50less.append(sum(LAC_WFL50less.area_harvested_new_secondary_regrowth_combined))
                carbon_regrowth_WFL50less.append(CCC_WFL50less.total_pdv_plantation_secondary_regrowth)


        # Save to the excel file
        dataframe = pd.DataFrame({'Country': countrynames,
                                  'ISO': codes,
                                  # Save PDV
                                  'PDV per ha Secondary middle regrowth (tC/ha)': pdv_per_ha_regrowth,
                                  'PDV per ha Secondary mature regrowth (tC/ha)': pdv_per_ha_regrowth_mature,
                                  'PDV per ha Secondary conversion (tC/ha)': pdv_per_ha_conversion,
                                  'PDV per ha Plantation (tC/ha)': pdv_per_ha_plantation_default,
                                  'PDV per ha Plantation 125% GR (tC/ha)': pdv_per_ha_plantation_highGR,
                                  'PDV per ha Secondary regrowth 62% SL (tC/ha)': pdv_per_ha_regrowth_optimalSL,
                                  'PDV per ha Agricultural land conversion (tC/ha)': pdv_per_ha_agriland,
                                  # Save output
                                  'Output per ha Agricultural land conversion (tC/ha)': output_ha_agriland,
                                  # Save wood supply
                                  'Default: Plantation supply wood (mega tC)': plantation_wood_default,
                                  'Default: Secondary forest supply wood (mega tC)': secondary_wood_default,
                                  '125% GR: Plantation supply wood (mega tC)': plantation_wood_highGR,
                                  '125% GR: Secondary forest supply wood (mega tC)': secondary_wood_highGR,
                                  '62% SL: Plantation supply wood (mega tC)': plantation_wood_optimalSL,
                                  '62% SL: Secondary forest supply wood (mega tC)': secondary_wood_optimalSL,
                                  'WFL50less: Plantation supply wood (mega tC)': plantation_wood_WFL50less,
                                  'WFL50less: Secondary forest supply wood (mega tC)': secondary_wood_WFL50less,

                                  # Save plantation area
                                  'Plantation area (ha)': area_plantation,

                                  # S1
                                  'S1 regrowth: Secondary area (ha)': area_regrowth,
                                  'S1 regrowth: total PDV (mega tC)': carbon_regrowth,
                                  'S1 regrowth: PDV plantation (mega tC)': carbon_existing_plantation,
                                  'S1 regrowth: PDV secondary (mega tC)': carbon_secondary_regrowth,

                                  # S2
                                  'S2 conversion: Secondary area (ha)': area_conversion,
                                  'S2 conversion: total PDV (mega tC)': carbon_conversion,

                                  # S3
                                  'S3 mixture: Secondary area (ha)': area_mixture,
                                  'S3 mixture: total PDV (mega tC)': carbon_mixture,
                                  'S3 mixture: Secondary middle aged area (ha)': area_mixture_middle,
                                  'S3 mixture: Secondary mature area (ha)': area_mixture_mature,

                                  # S4
                                  'S4 125% GR: Secondary area (ha)': area_regrowth_highGR,
                                  'S4 125% GR: total PDV (mega tC)': carbon_regrowth_highGR,

                                  # S5
                                  'S5 62% SL: Secondary area (ha)': area_regrowth_optimalSL,
                                  'S5 62% SL: total PDV (mega tC)': carbon_regrowth_optimalSL,

                                  # S6
                                  'S6 WFL 50% less: Secondary area (ha)': area_regrowth_WFL50less,
                                  'S6 WFL 50% less: total PDV (mega tC)': carbon_regrowth_WFL50less,

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
    def run_all_input_permutations():
        "Run model based on the different combination of the three parameters"
        for vslp_input_control in ['ALL', 'IND', 'WFL']:
            for substitution_mode in ['NOSUB', 'SUBON']:
                for future_demand_level in ['BAU', 'CST']:
                    single_run_with_combination_input(future_demand_level_input=future_demand_level, substitution_mode_input=substitution_mode, vslp_input_control_input=vslp_input_control)
        return

    run_all_input_permutations()

    return


def run_model_main_scenario(years, discount_rate, version, sensdir, sensexp, path):
    """
    Created and Edited: 2022/11
    This is a driver for running global analysis for forestry land and carbon consequences.
    This is only for the main regrowth scenario 1, to save running time for sensitivity analysis
    """
    # Read input/output data excel file.
    datafile = '{}/data/processed/{}/CHARM regional - YR_{} - DR_{} - V{} - {}.xlsx'.format(path, sensdir, years, discount_rate, version, sensexp)

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
        # country name, code
        countrynames, codes = [], []
        # wood supply
        secondary_wood_default, plantation_wood_default = [], []
        # pdv
        pdv_per_ha_plantation_default = []
        pdv_per_ha_regrowth = []
        # area
        area_plantation = []
        area_regrowth, carbon_regrowth, carbon_existing_plantation, carbon_secondary_regrowth = [], [], [], []
        output_ha_agriland = []

        # For each country, calculate the results for all scenarios. Each variable collects a list of the countries' results.
        for country, code in zip(countries['Country'], countries['ISO']):
            # Test if the parameters are set up for this country, if there is one parameter missing, no calculation will be done for this country.
            input_country = input_data.loc[input_data['Country'] == country]
            input_country = input_country.drop(['Emissions substitution factor for LLP (tC saved/tons C in LLP)'], axis=1)
            if input_country.isnull().values.any():
                print("Please fill in the abbreviation and all the missing parameters for country '{}'!".format(country))
            else:
                ################################### Execute model runs ##################################
                nyears_harvest_settings = Global_by_country.SetupTime(datafile, country_iso=code, nyears_run_control='harvest')
                nyears_growth_settings = Global_by_country.SetupTime(datafile, country_iso=code, nyears_run_control='growth')
                ### Default plantation scenarios, (1) secondary harvest regrowth and (2) conversion
                ### Read in global parameters ###
                global_harvest_settings = Global_by_country.Parameters(datafile, nyears_harvest_settings,
                                                                        country_iso=code,
                                                                       future_demand_level=future_demand_level_input,
                                                                       substitution_mode=substitution_mode_input,
                                                                       vslp_input_control=vslp_input_control_input)
                global_growth_settings = Global_by_country.Parameters(datafile, nyears_growth_settings,
                                                                       country_iso=code,
                                                                       future_demand_level=future_demand_level_input,
                                                                       substitution_mode=substitution_mode_input,
                                                                       vslp_input_control=vslp_input_control_input)
                # run different policy scenarios
                result_plantation_default = Plantation_counterfactual_secondary_plantation_age_scenario.CarbonTracker(global_harvest_settings)
                # result_conversion_default = Secondary_conversion_scenario.CarbonTracker(global_harvest_settings)
                result_regrowth_default = Secondary_regrowth_scenario.CarbonTracker(global_harvest_settings)
                # result_agriland_default = Agricultural_land_tropical_scenario.CarbonTracker(global_harvest_settings)

                # run the land area calculator
                LAC_default = Land_area_calculator.LandCalculator(global_harvest_settings)
                if global_harvest_settings.rotation_length_harvest == 10:
                    output_ha_agriland_default = LAC_default.output_ha_agriland[global_harvest_settings.year_index_harvest_plantation[1]-1]
                else:
                    output_ha_agriland_default = 0
                # run the carbon cost calculator
                CCC_default = Carbon_cost_calculator.CarbonCalculator(global_harvest_settings, global_growth_settings, LAC_default)

                ################################### Prepare output ##################################
                countrynames.append(country)
                codes.append(code)

                # Carbon tracker
                pdv_per_ha_plantation_default.append(np.sum(result_plantation_default.annual_discounted_value))
                pdv_per_ha_regrowth.append(np.sum(result_regrowth_default.annual_discounted_value))

                # Get output per ha for new plantation
                output_ha_agriland.append(output_ha_agriland_default)

                # Default situation
                secondary_wood_default.append(sum(LAC_default.output_need_secondary / 1000000))
                plantation_wood_default.append(sum(LAC_default.product_total_carbon) / 1000000 - sum(LAC_default.output_need_secondary) / 1000000)
                area_plantation.append(sum(CCC_default.area_harvested_new_plantation))

                # Scenario 1
                area_regrowth.append(sum(LAC_default.area_harvested_new_secondary_regrowth_combined))
                carbon_regrowth.append(CCC_default.total_pdv_plantation_secondary_regrowth)
                carbon_existing_plantation.append(CCC_default.total_pdv_plantation_sum)
                carbon_secondary_regrowth.append(CCC_default.total_pdv_secondary_regrowth_sum)


        # Save to the excel file
        dataframe = pd.DataFrame({'Country': countrynames,
                                  'ISO': codes,
                                  # Save PDV
                                  'PDV per ha Secondary middle regrowth (tC/ha)': pdv_per_ha_regrowth,
                                  'PDV per ha Plantation (tC/ha)': pdv_per_ha_plantation_default,
                                  # Save output
                                  'Output per ha Agricultural land conversion (tC/ha)': output_ha_agriland,
                                  # Save wood supply
                                  'Default: Plantation supply wood (mega tC)': plantation_wood_default,
                                  'Default: Secondary forest supply wood (mega tC)': secondary_wood_default,

                                  # Save plantation area
                                  'Plantation area (ha)': area_plantation,

                                  # S1
                                  'S1 regrowth: Secondary area (ha)': area_regrowth,
                                  'S1 regrowth: total PDV (mega tC)': carbon_regrowth,
                                  'S1 regrowth: PDV plantation (mega tC)': carbon_existing_plantation,
                                  'S1 regrowth: PDV secondary (mega tC)': carbon_secondary_regrowth,

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
    def run_single_input(future_demand_level, substitution_mode, vslp_input_control):
        "Run model with a set of parameters"
        single_run_with_combination_input(future_demand_level_input=future_demand_level,
                                          substitution_mode_input=substitution_mode,
                                          vslp_input_control_input=vslp_input_control)
        return

    def run_key_input_permutations():
        "Run the key BAU and CST without substitution, only for sensitivity analysis"
        for vslp_input_control in ['ALL']:
            for substitution_mode in ['NOSUB']:
                for future_demand_level in ['BAU', 'CST']:
                    single_run_with_combination_input(future_demand_level_input=future_demand_level, substitution_mode_input=substitution_mode, vslp_input_control_input=vslp_input_control)
        return

    run_key_input_permutations()

    return


if __name__ == "__main__": # to avoid import run

    ##################### Local run (single run) ########################
    # run_model_all_scenarios('100', '6p', '20230125', root)

    ################# Terminal run: through command line #################
    import argparse
    parser = argparse.ArgumentParser(prog='Driver', description='Run the CHARM regional model', usage='%(prog)s [options]')
    parser.add_argument('--run-main', default=False, type=lambda x: (str(x).lower() in ['true', '1', 'yes']), help='Determine if it is a main model run')
    parser.add_argument('--run-sensitivity', default=False, type=lambda x: (str(x).lower() in ['true', '1', 'yes']), help='Determine if it is a sensitivity run')
    parser.add_argument('--years-growth', default=40, help='The number of years of growth')
    parser.add_argument('--discount-rate', default='4p', help='The discount rate')
    parser.add_argument('--path', default=root, help='The root path of running the model')

    args = parser.parse_args()

    if args.run_main == True:
        for discount_rate in ['4p', '0p', '2p', '6p']:
            run_model_all_scenarios(args.years_growth, discount_rate, '20230125', args.path)

    if args.run_sensitivity == True:

        growth_exps = ['GR_25U', 'GR_25D', 'GR1_GR2_25D', 'GR1_GR2_25U', 'GR1_GR2_50U']
        rootshoot_exps = ['RSR_25U', 'RSR_25D']
        demand_exps = ['Demand_OECD', 'Demand_IIASA', 'Demand_LINE']
        trade_exps = ['Trade_50U', 'Trade_50D']
        # old_exps = ['Old_GRRL', 'Old_PGR', 'Old_SGR', 'Old_RL', 'Old_SR']

        for experiment in growth_exps:
            run_model_main_scenario(args.years_growth, args.discount_rate, '20230125', 'run_NatSensitivity_20230125', experiment, args.path)

