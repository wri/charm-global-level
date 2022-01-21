#!/usr/bin/env python
"""
This is the main file for model execution.
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
import matplotlib.pyplot as plt
import Global_by_country, Plantation_counterfactual_secondary_plantation_age_scenario, Secondary_conversion_scenario, Secondary_regrowth_scenario, Secondary_mature_regrowth_scenario, Agricultural_land_tropical_scenario, Land_area_calculator
# import Pasture_with_counterfactual_scenario, Pasture_zero_counterfactual_scenario

################################################### TESTING ####################################################

root = '../../'

def test_carbon_tracker():
    "TEST Carbon tracker"
    # set up the country
    iso = 'BRA'
    # datafile = '{}/data/processed/CHARM regional - DR_4p - Nov 1.xlsx'.format(root)
    datafile = '{}/data/processed/CHARM regional - DR_4p - Jan 11 2022.xlsx'.format(root)

    global_settings = Global_by_country.Parameters(datafile, country_iso=iso, future_demand_level='BAU')
    # Plantation_counterfactual_secondary_plantation_age_scenario.CarbonTracker(global_settings, year_start_for_PDV=0).plot_C_pools_counterfactual_print_PDV()
    # Plantation_counterfactual_unharvested_scenario.CarbonTracker(global_settings, year_start_for_PDV=0).plot_C_pools_counterfactual_print_PDV()
    # Plantation_scenario.CarbonTracker(global_settings, year_start_for_PDV=0).plot_C_pools_counterfactual_print_PDV()
    # Secondary_conversion_scenario.CarbonTracker(global_settings, year_start_for_PDV=0).plot_C_pools_counterfactual_print_PDV()
    # Secondary_regrowth_scenario.CarbonTracker(global_settings, year_start_for_PDV=0).plot_C_pools_counterfactual_print_PDV()
    Secondary_mature_regrowth_scenario.CarbonTracker(global_settings, year_start_for_PDV=0).plot_C_pools_counterfactual_print_PDV()
    # Pasture_with_counterfactual_scenario.CarbonTracker(global_settings, year_start_for_PDV=0).plot_C_pools_counterfactual_print_PDV()
    # Pasture_zero_counterfactual_scenario.CarbonTracker(global_settings, year_start_for_PDV=0).plot_C_pools_counterfactual_print_PDV()
    # Agricultural_land_tropical_scenario.CarbonTracker(global_settings, year_start_for_PDV=0).plot_C_pools_counterfactual_print_PDV()

    return

# test_carbon_tracker()
# exit()

def test_PDV_module():

    # datafile = '{}/data/processed/CHARM regional - BAU SF_0 - DR_0p - May 12.xlsx'.format(root)
    # datafile = '{}/data/processed/CHARM regional - BAU SF_1.2 - DR_6p - May 10.xlsx'.format(root)
    # datafile = '{}/data/processed/CHARM regional - BAU SF_1.2 - DR_2p - May 10.xlsx'.format(root)
    iso = 'BRA'

    datafile = '{}/data/processed/CHARM regional - BAU SF_0 - DR_0p - May 12.xlsx'.format(root)
    global_settings = Global_by_country.Parameters(datafile, country_iso=iso)
    obj = Plantation_counterfactual_secondary_plantation_age_scenario.CarbonTracker(global_settings, year_start_for_PDV=0)

    # obj = Secondary_conversion_scenario.CarbonTracker(global_settings, year_start_for_PDV=0)
    # obj = Secondary_regrowth_scenario.CarbonTracker(global_settings, year_start_for_PDV=0)
    df = pd.DataFrame({'Harvest scenario': obj.total_carbon_benefit[1:],
                       'Counterfactual': obj.counterfactual_biomass[1:],
                       'Annual carbon impact': obj.annual_discounted_value,
                       'Harvest scenario - Counterfactual': obj.total_carbon_benefit[1:]-obj.counterfactual_biomass[1:]
                       }, index=np.arange(2010, 2051))
    df.plot(color=["k", "limegreen", 'Red', 'Blue'], lw=2)

    plt.title('Brazil Secondary Regrowth Carbon impact (tC/ha)')
    plt.annotate('Harvest scenario - Counterfactual SUM: {:.0f}'.format(np.sum(df['Harvest scenario - Counterfactual'])), xy=(0.05, 0.45), xycoords='axes fraction', fontsize=12)
    plt.annotate('Annual carbon impact (0% discount) SUM: {:.0f}'.format(np.sum(df['Annual carbon impact'])), xy=(0.05, 0.38), xycoords='axes fraction', fontsize=12)
    plt.show()

    return

# test_PDV_module()
# exit()

def test_land_area_calculator():
    "TEST land area calculator"
    iso = 'BRA'
    # datafile = '{}/data/processed/CHARM regional - BAU SF_1.2 - Apr 14.xlsx'.format(root)
    # datafile = '{}/data/processed/CHARM regional - BAU SF_1.2 - Apr 21.xlsx'.format(root)
    # datafile = '{}/data/processed/CHARM regional - BAU SF_1.2 - DR_2p - May 10.xlsx'.format(root)
    # datafile = '{}/data/processed/CHARM regional - DR_4p - Nov 1.xlsx'.format(root)
    datafile = '{}/data/processed/CHARM regional - DR_4p - Jan 11 2022.xlsx'.format(root)

    # global_settings = Global_by_country.Parameters(datafile, country_iso=iso)
    global_settings = Global_by_country.Parameters(datafile, country_iso=iso, future_demand_level='CST', secondary_mature_wood_share=0)

    # global_settings = Global_by_country.Parameters(datafile, country_iso=iso, vslp_future_demand='WFL50less')
    # run the land area calculator
    LAC = Land_area_calculator.LandCalculator(global_settings)
    # print("T PDV regrowth", LAC.total_pdv_plantation_secondary_regrowth)
    # print("T PDV conversion", LAC.total_pdv_plantation_secondary_conversion)
    print("Area regrowth", sum(LAC.area_harvested_new_secondary_regrowth)+sum(LAC.area_harvested_new_secondary_mature_regrowth))
    # print("Area conversion", sum(LAC.area_harvested_new_secondary_conversion))

    return
# test_land_area_calculator()
# exit()


#############################################RUNNING MODEL###########################################
def run_model_five_scenarios():
    """
    Created and Edited: 2021/08-10
    This is a driver for running global analysis for forestry land and carbon consequences.
    """
    # Read input/output data excel file.
    datafile = '{}/data/processed/CHARM regional - DR_6p - Nov 1.xlsx'.format(root)
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
        secondary_wood_default, plantation_wood_default, secondary_wood_highGR, plantation_wood_highGR, secondary_wood_WFL50less, plantation_wood_WFL50less = [], [], [], [], [], []
        pdv_per_ha_plantation_default, pdv_per_ha_regrowth, pdv_per_ha_conversion = [], [], []
        pdv_per_ha_mature_regrowth, pdv_per_ha_plantation_highGR, pdv_per_ha_agriland = [], [], []
        area_plantation = []
        area_regrowth, carbon_regrowth, carbon_existing_plantation, carbon_secondary_regrowth = [], [], [], []
        area_conversion, carbon_conversion = [], []
        area_mixture, carbon_mixture, area_mixture_middle, area_mixture_mature = [], [], [], []
        area_regrowth_highGR, carbon_regrowth_highGR = [], []
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
                ### Default plantation scenarios, (1) secondary harvest regrowth and (2) conversion
                ### Read in global parameters ###
                global_settings = Global_by_country.Parameters(datafile, country_iso=code, future_demand_level=future_demand_level_input, substitution_mode=substitution_mode_input, vslp_input_control=vslp_input_control_input)
                # run different policy scenarios
                result_plantation_default = Plantation_counterfactual_secondary_plantation_age_scenario.CarbonTracker(global_settings)
                result_conversion_default = Secondary_conversion_scenario.CarbonTracker(global_settings)
                result_regrowth_default = Secondary_regrowth_scenario.CarbonTracker(global_settings)
                result_agriland_default = Agricultural_land_tropical_scenario.CarbonTracker(global_settings)

                # run the land area calculator
                LAC_default = Land_area_calculator.LandCalculator(global_settings)
                if global_settings.rotation_length_harvest == 10:
                    output_ha_agriland_default = LAC_default.output_ha_agriland[global_settings.year_index_harvest_plantation[1]-1]
                else:
                    output_ha_agriland_default = 0

                ### scenario (3) secondary harvest regrowth: 50% middle aged and 50% mature secondary forest
                ### Read in global parameters ###
                global_settings = Global_by_country.Parameters(datafile, country_iso=code, future_demand_level=future_demand_level_input, substitution_mode=substitution_mode_input, vslp_input_control=vslp_input_control_input, secondary_mature_wood_share=0.5)
                # run different policy scenarios
                # result_plantation_mixture = Plantation_counterfactual_secondary_plantation_age_scenario.CarbonTracker(global_settings)
                # result_regrowth_mixture = Secondary_regrowth_scenario.CarbonTracker(global_settings)
                result_mature_regrowth_mixture = Secondary_mature_regrowth_scenario.CarbonTracker(global_settings)

                # run the land area calculator
                LAC_mixture = Land_area_calculator.LandCalculator(global_settings)

                ### scenario (4) secondary harvest regrowth: 125% productivity increase in plantation
                ### Read in global parameters ###
                global_settings = Global_by_country.Parameters(datafile, country_iso=code, future_demand_level=future_demand_level_input, substitution_mode=substitution_mode_input, vslp_input_control=vslp_input_control_input, plantation_growth_increase_ratio=1.25)
                # run different policy scenarios
                result_plantation_highGR = Plantation_counterfactual_secondary_plantation_age_scenario.CarbonTracker(
                    global_settings)

                # run the land area calculator
                LAC_highGR = Land_area_calculator.LandCalculator(global_settings)

                ### scenario (5) secondary harvest regrowth: 50% reduction in VSLP-WFL production
                # read in global parameters
                global_settings = Global_by_country.Parameters(datafile, country_iso=code, future_demand_level=future_demand_level_input, substitution_mode=substitution_mode_input, vslp_input_control=vslp_input_control_input, vslp_future_demand='WFL50less')
                # run the land area calculator
                LAC_WFL50less = Land_area_calculator.LandCalculator(global_settings)

                ################################### Prepare output ##################################
                countrynames.append(country)
                codes.append(code)

                # Carbon tracker
                pdv_per_ha_plantation_default.append(np.sum(result_plantation_default.annual_discounted_value))
                pdv_per_ha_regrowth.append(np.sum(result_regrowth_default.annual_discounted_value))
                pdv_per_ha_conversion.append(np.sum(result_conversion_default.annual_discounted_value))
                pdv_per_ha_mature_regrowth.append(np.sum(result_mature_regrowth_mixture.annual_discounted_value))
                pdv_per_ha_plantation_highGR.append(np.sum(result_plantation_highGR.annual_discounted_value))
                pdv_per_ha_agriland.append(np.sum(result_agriland_default.annual_discounted_value))

                # Get output per ha for new plantation
                output_ha_agriland.append(output_ha_agriland_default)

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

                # Scenario 3: 50:50 secondary supply
                area_mixture.append(sum(LAC_mixture.area_harvested_new_secondary_regrowth_combined))
                carbon_mixture.append(LAC_mixture.total_pdv_plantation_secondary_regrowth)
                area_mixture_middle.append(sum(LAC_mixture.area_harvested_new_secondary_regrowth))
                area_mixture_mature.append(sum(LAC_mixture.area_harvested_new_secondary_mature_regrowth))

                # Scenario 4: Plantation productivity increase
                # Productivity increase
                secondary_wood_highGR.append(sum(LAC_highGR.output_need_secondary / 1000000))
                plantation_wood_highGR.append(sum(LAC_highGR.product_total_carbon) / 1000000 - sum(LAC_highGR.output_need_secondary) / 1000000)
                area_regrowth_highGR.append(sum(LAC_highGR.area_harvested_new_secondary_regrowth_combined))
                carbon_regrowth_highGR.append(LAC_highGR.total_pdv_plantation_secondary_regrowth)

                # Scenario 5: VSLP-WFL 50% reduction
                secondary_wood_WFL50less.append(sum(LAC_WFL50less.output_need_secondary / 1000000))
                plantation_wood_WFL50less.append( sum(LAC_WFL50less.product_total_carbon) / 1000000 - sum(LAC_WFL50less.output_need_secondary) / 1000000)
                area_regrowth_WFL50less.append(sum(LAC_WFL50less.area_harvested_new_secondary_regrowth_combined))
                carbon_regrowth_WFL50less.append(LAC_WFL50less.total_pdv_plantation_secondary_regrowth)


        # Save to the excel file
        dataframe = pd.DataFrame({'Country': countrynames,
                                  'ISO': codes,
                                  # Save PDV
                                  'PDV per ha Secondary middle regrowth (tC/ha)': pdv_per_ha_regrowth,
                                  'PDV per ha Secondary mature regrowth (tC/ha)': pdv_per_ha_mature_regrowth,
                                  'PDV per ha Secondary conversion (tC/ha)': pdv_per_ha_conversion,
                                  'PDV per ha Plantation (tC/ha)': pdv_per_ha_plantation_default,
                                  'PDV per ha Plantation 125% GR (tC/ha)': pdv_per_ha_plantation_highGR,
                                  'PDV per ha Agricultural land conversion (tC/ha)': pdv_per_ha_agriland,
                                  # Save output
                                  'Output per ha Agricultural land conversion (tC/ha)': output_ha_agriland,
                                  # Save wood supply
                                  'Default: Plantation supply wood (mega tC)': plantation_wood_default,
                                  'Default: Secondary forest supply wood (mega tC)': secondary_wood_default,
                                  '125% GR: Plantation supply wood (mega tC)': plantation_wood_highGR,
                                  '125% GR: Secondary forest supply wood (mega tC)': secondary_wood_highGR,
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
                                  'S5 WFL 50% less: Secondary area (ha)': area_regrowth_WFL50less,
                                  'S5 WFL 50% less: total PDV (mega tC)': carbon_regrowth_WFL50less,

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

    def run_all_input_permutations():
        "Run model based on the different combination of the three parameters"
        for vslp_input_control in ['ALL', 'IND', 'WFL']:
            for substitution_mode in ['NOSUB', 'SUBON']:
                for future_demand_level in ['BAU', 'CST']:
                    single_run_with_combination_input(future_demand_level_input=future_demand_level, substitution_mode_input=substitution_mode, vslp_input_control_input=vslp_input_control)
        return

    run_all_input_permutations()

    return


def run_model_baseline_scenarios():
    """
    Created and Edited: 2022/1/11
    This is a driver for running global analysis for the first three baseline scenarios testing.
    """
    # Read input/output data excel file.
    datafile = '{}/data/processed/CHARM regional - DR_4p - Feb 11 2022.xlsx'.format(root)
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
        secondary_wood_default, plantation_wood_default  = [], []
        pdv_per_ha_plantation_default, pdv_per_ha_regrowth, pdv_per_ha_conversion = [], [], []
        pdv_per_ha_mature_regrowth = []
        area_plantation = []
        area_regrowth, carbon_regrowth, carbon_existing_plantation, carbon_secondary_regrowth = [], [], [], []
        area_conversion, carbon_conversion = [], []
        area_mixture, carbon_mixture, area_mixture_middle, area_mixture_mature = [], [], [], []

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

                ### scenario (3) secondary harvest regrowth: 50% middle aged and 50% mature secondary forest
                ### Read in global parameters ###
                global_settings = Global_by_country.Parameters(datafile, country_iso=code, future_demand_level=future_demand_level_input, substitution_mode=substitution_mode_input, vslp_input_control=vslp_input_control_input, secondary_mature_wood_share=0.5)
                # run different policy scenarios
                # result_plantation_mixture = Plantation_counterfactual_secondary_plantation_age_scenario.CarbonTracker(global_settings)
                # result_regrowth_mixture = Secondary_regrowth_scenario.CarbonTracker(global_settings)
                result_mature_regrowth_mixture = Secondary_mature_regrowth_scenario.CarbonTracker(global_settings)

                # run the land area calculator
                LAC_mixture = Land_area_calculator.LandCalculator(global_settings, plantation_counterfactual_code='secondary_plantation_age')

                ################################### Prepare output ##################################
                countrynames.append(country)
                codes.append(code)

                # Carbon tracker
                pdv_per_ha_plantation_default.append(np.sum(result_plantation_default.annual_discounted_value))
                pdv_per_ha_regrowth.append(np.sum(result_regrowth_default.annual_discounted_value))
                pdv_per_ha_conversion.append(np.sum(result_conversion_default.annual_discounted_value))
                pdv_per_ha_mature_regrowth.append(np.sum(result_mature_regrowth_mixture.annual_discounted_value))

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

                # Scenario 3: 50:50 secondary supply
                area_mixture.append(sum(LAC_mixture.area_harvested_new_secondary_regrowth_combined))
                carbon_mixture.append(LAC_mixture.total_pdv_plantation_secondary_regrowth)
                area_mixture_middle.append(sum(LAC_mixture.area_harvested_new_secondary_regrowth))
                area_mixture_mature.append(sum(LAC_mixture.area_harvested_new_secondary_mature_regrowth))


        # Save to the excel file
        dataframe = pd.DataFrame({'Country': countrynames,
                                  'ISO': codes,
                                  # Save PDV
                                  'PDV per ha Secondary middle regrowth (tC/ha)': pdv_per_ha_regrowth,
                                  'PDV per ha Secondary mature regrowth (tC/ha)': pdv_per_ha_mature_regrowth,
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

    def run_all_input_permutations():
        "Run model based on the different combination of the three parameters"
        for vslp_input_control in ['ALL', 'IND', 'WFL']:
            for substitution_mode in ['NOSUB', 'SUBON']:
                for future_demand_level in ['BAU', 'CST']:
                    single_run_with_combination_input(future_demand_level_input=future_demand_level, substitution_mode_input=substitution_mode, vslp_input_control_input=vslp_input_control)
        return

    # run_all_input_permutations()

    run_single_input('BAU', 'NOSUB', 'ALL')
    run_single_input('CST', 'NOSUB', 'ALL')

    return


if __name__ == "__main__":
    # run_model_five_scenarios()
    run_model_baseline_scenarios()

    exit()


def get_global_annual_carbon_impact():
    demand_levels = ['BAU SF_1.2', 'BAU SF_0', 'constant demand SF_1.2', 'constant demand SF_0']
    demand_names = ['BAU 1.2', 'BAU 0', 'CON 1.2', 'CON 0']

    outfile = '{}/data/processed/derivative/carbon_impact_nodiscount_4scenario_3foresttype.xlsx'.format(root)
    writer = pd.ExcelWriter(outfile)

    for demand_level, demand_name in zip(demand_levels, demand_names):
        datafile = '{}/data/processed/CHARM regional - {} - DR_0p - May 12.xlsx'.format(root, demand_level)
        scenarios = pd.read_excel(datafile, sheet_name='Inputs', usecols="A:B", skiprows=1)
        input_data = pd.read_excel(datafile, sheet_name='Inputs', skiprows=1)

        array_plantation = np.zeros((len(scenarios['Country']), Global_by_country.Parameters(datafile).nyears))
        array_conversion = np.zeros((len(scenarios['Country']), Global_by_country.Parameters(datafile).nyears))
        array_regrowth = np.zeros((len(scenarios['Country']), Global_by_country.Parameters(datafile).nyears))
        nc = 0

        for scenario, code in zip(scenarios['Country'], scenarios['ISO']):
            # Test if the parameters are set up for this scenario, if there is one missing, will not do any calculation
            input_scenario = input_data.loc[input_data['Country'] == scenario]
            input_scenario = input_scenario.drop(['Emissions substitution factor for LLP (tC saved/tons C in LLP)'], axis=1)
            if input_scenario.isnull().values.any():
                print("Please fill in the abbreviation and all the missing parameters for scenario '{}'!".format(scenario))
            else:
                # read in global parameters
                global_settings = Global_by_country.Parameters(datafile, country_iso=code)
                LAC_secondary_plantation_age = Land_area_calculator.LandCalculator(global_settings, plantation_counterfactual_code='secondary_plantation_age')

                array_plantation[nc, :] = LAC_secondary_plantation_age.total_pdv_plantation / 1000000
                array_conversion[nc, :] = LAC_secondary_plantation_age.total_pdv_secondary_conversion / 1000000
                array_regrowth[nc, :] = LAC_secondary_plantation_age.total_pdv_secondary_regrowth / 1000000

                nc = nc + 1

        df_plantation = pd.DataFrame(data=array_plantation, index=scenarios['Country'], columns=range(2010, 2051, 1))
        df_conversion = pd.DataFrame(data=array_conversion, index=scenarios['Country'], columns=range(2010, 2051, 1))
        df_regrowth = pd.DataFrame(data=array_regrowth, index=scenarios['Country'], columns=range(2010, 2051, 1))

        df_plantation.loc['Global'] = df_plantation.sum()/0.8
        df_conversion.loc['Global'] = df_conversion.sum()/0.8
        df_regrowth.loc['Global'] = df_regrowth.sum()/0.8

        df_plantation.to_excel(writer, sheet_name='{} plantation'.format(demand_name))
        df_conversion.to_excel(writer, sheet_name='{} conversion'.format(demand_name))
        df_regrowth.to_excel(writer, sheet_name='{} Regrowth'.format(demand_name))

    writer.save()
    writer.close()


    return

# get_global_annual_carbon_impact()

def get_global_annual_carbon_flow():
    demand_levels = ['BAU SF_1.2', 'BAU SF_0', 'constant demand SF_1.2', 'constant demand SF_0']
    demand_names = ['BAU 1.2', 'BAU 0', 'CON 1.2', 'CON 0']

    # outfile = '{}/data/processed/derivative/carbon_flow_nodiscount_4scenario_3foresttype.xlsx'.format(root)
    # writer = pd.ExcelWriter(outfile)

    for demand_level, demand_name in zip(demand_levels, demand_names):
        datafile = '{}/data/processed/CHARM regional - {} - DR_0p - May 12.xlsx'.format(root, demand_level)
        scenarios = pd.read_excel(datafile, sheet_name='Inputs', usecols="A:B", skiprows=1)
        input_data = pd.read_excel(datafile, sheet_name='Inputs', skiprows=1)

        # Define the empty arrays
        total_carbon = np.zeros((len(scenarios['Country']), Global_by_country.Parameters(datafile).nyears))
        product_storage_plantation = np.zeros((len(scenarios['Country']), Global_by_country.Parameters(datafile).nyears))
        product_storage_conversion = np.zeros((len(scenarios['Country']), Global_by_country.Parameters(datafile).nyears))
        product_storage_regrowth = np.zeros((len(scenarios['Country']), Global_by_country.Parameters(datafile).nyears))
        net_regrowth_regrowth = np.zeros((len(scenarios['Country']), Global_by_country.Parameters(datafile).nyears))
        substitution_plantation = np.zeros((len(scenarios['Country']), Global_by_country.Parameters(datafile).nyears))
        substitution_conversion = np.zeros((len(scenarios['Country']), Global_by_country.Parameters(datafile).nyears))
        substitution_regrowth = np.zeros((len(scenarios['Country']), Global_by_country.Parameters(datafile).nyears))
        wood_removed_plantation = np.zeros((len(scenarios['Country']), Global_by_country.Parameters(datafile).nyears))
        wood_in_plantation = np.zeros((len(scenarios['Country']), Global_by_country.Parameters(datafile).nyears))
        wood_counterfactual_plantation = np.zeros((len(scenarios['Country']), Global_by_country.Parameters(datafile).nyears))

        nc = 0

        for scenario, code in zip(scenarios['Country'], scenarios['ISO']):
            # Test if the parameters are set up for this scenario, if there is one missing, will not do any calculation
            input_scenario = input_data.loc[input_data['Country'] == scenario]
            input_scenario = input_scenario.drop(['Emissions substitution factor for LLP (tC saved/tons C in LLP)'], axis=1)
            if input_scenario.isnull().values.any():
                print("Please fill in the abbreviation and all the missing parameters for scenario '{}'!".format(scenario))
            else:
                # read in global parameters
                global_settings = Global_by_country.Parameters(datafile, country_iso=code)
                result_plantation = Plantation_counterfactual_secondary_plantation_age_scenario.CarbonTracker(global_settings)
                result_secondary_conversion = Secondary_conversion_scenario.CarbonTracker(global_settings)
                result_secondary_regrowth = Secondary_regrowth_scenario.CarbonTracker(global_settings)
                LAC_secondary_plantation_age = Land_area_calculator.LandCalculator(global_settings, plantation_counterfactual_code='secondary_plantation_age')

                # A. total wood harvested divided by the total reduction in carbon in the forest
                total_carbon[nc, :] = LAC_secondary_plantation_age.product_total_carbon

                # B. Net wood product carbon storage due to harvest after 40 years. This is the amount of wood still left in LLP & SLP or in landfills
                product_storage_plantation[nc, :] = result_plantation.totalC_product_pool[1:] + result_plantation.totalC_landfill_pool[1:]
                product_storage_conversion[nc, :] = result_secondary_conversion.totalC_product_pool[1:] + result_secondary_conversion.totalC_landfill_pool[1:]
                product_storage_regrowth[nc, :] = result_secondary_regrowth.totalC_product_pool[1:] + result_secondary_regrowth.totalC_landfill_pool[1:]

                # C. Net regrowth in the secondary regrowth scenario = means gross regrowth minus the ongoing growth in the counterfactual
                # Example: Counterfactual year 1 = 50, Counterfactual year 40 = 75
                # Regrowth year 1 = 0, Regrowth year 40 = 50
                # Net regrowth = 50-(75-50)=25
                net_regrowth_regrowth[nc, :] = (result_secondary_regrowth.totalC_stand_pool[1:] - result_secondary_regrowth.totalC_stand_pool[1]) - (result_secondary_regrowth.counterfactual_biomass[1:] - result_secondary_regrowth.counterfactual_biomass[1])

                # D. Total substitution benefits and subtotals, total substitution for concrete & steel and total substitution for traditional bioenergy
                substitution_plantation[nc, :] = result_plantation.LLP_substitution_benefit[1:] + result_plantation.VSLP_substitution_benefit[1:]
                substitution_conversion[nc, :] = result_secondary_conversion.LLP_substitution_benefit[1:] + result_secondary_conversion.VSLP_substitution_benefit[1:]
                substitution_regrowth[nc, :] = result_secondary_regrowth.LLP_substitution_benefit[1:] + result_secondary_regrowth.VSLP_substitution_benefit[1:]

                ### Plantation specific
                # E. Quantity of wood removed
                wood_removed_plantation[nc, :] = result_plantation.totalC_stand_pool[1:]

                # F. Quantity of carbon stored in plantations after 40 years
                wood_in_plantation[nc, :] = result_plantation.totalC_stand_pool[1:]

                # G. Quantity of carbon that would be stored in the counterfactual
                wood_counterfactual_plantation[nc, :] = result_plantation.counterfactual_biomass[1:]




                nc = nc + 1

        def global_sum(array):
            return array.sum(axis=0)

        global_total_carbon = global_sum(total_carbon)
        global_product_storage_plantation = global_sum(product_storage_plantation)
        global_product_storage_conversion = global_sum(product_storage_conversion)
        global_product_storage_regrowth = global_sum(product_storage_regrowth)

        # The ratio of wood harvest divided by the total reduction in the secondary forest
        print(global_total_carbon/(global_plantation+global_regrowth))
        print(sum(global_plantation+global_regrowth))

        exit()
        # df_plantation = pd.DataFrame(data=array_plantation, index=scenarios['Country'], columns=range(2010, 2051, 1))
        # df_conversion = pd.DataFrame(data=array_conversion, index=scenarios['Country'], columns=range(2010, 2051, 1))
        # df_regrowth = pd.DataFrame(data=array_regrowth, index=scenarios['Country'], columns=range(2010, 2051, 1))

        # df_plantation.loc['Global'] = df_plantation.sum()/0.8
        # df_conversion.loc['Global'] = df_conversion.sum()/0.8
        # df_regrowth.loc['Global'] = df_regrowth.sum()/0.8

    #     df_plantation.to_excel(writer, sheet_name='{} plantation'.format(demand_name))
    #     df_conversion.to_excel(writer, sheet_name='{} conversion'.format(demand_name))
    #     df_regrowth.to_excel(writer, sheet_name='{} Regrowth'.format(demand_name))
    #
    # writer.save()
    # writer.close()


    return

# get_global_annual_carbon_flow()
