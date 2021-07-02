#!/usr/bin/env python
__author__ = "Liqing Peng, Jessica Zionts, Tim Searchinger"
__copyright__ = "Copyright (C) 2020 WRI, The Carbon Harvest Model (CHarM) Project"
__maintainer__ = "Liqing Peng"
__email__ = "liqing.peng@wri.org"

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import Global_by_country, Plantation_scenario, Secondary_conversion_scenario, Secondary_regrowth_scenario, Secondary_mature_regrowth_scenario, Land_area_calculator
# import Pasture_zero_counterfactual_scenario, Pasture_with_counterfactual_scenario
import Plantation_counterfactual_secondary_historic_scenario, Plantation_counterfactual_secondary_plantation_age_scenario, Plantation_counterfactual_unharvested_scenario


################################################### TESTING ####################################################

root = '../../'

def test_carbon_tracker():
    "TEST Carbon tracker"
    # set up the country
    iso = 'BRA'
    # datafile = '{}/data/processed/CHARM regional - BAU SF_1.2 - May 12.xlsx'.format(root)
    datafile = '{}/data/processed/CHARM regional - BAU - SF_1.2 - DR_4p - Jun 3.xlsx'.format(root)
    # datafile = '{}/data/processed/CHARM regional - BAU SF_0 - May 12.xlsx'.format(root)

    global_settings = Global_by_country.Parameters(datafile, country_iso=iso)
    # Plantation_counterfactual_unharvested_scenario.CarbonTracker(global_settings, year_start_for_PDV=0).plot_C_pools_counterfactual_print_PDV()
    # Plantation_counterfactual_secondary_plantation_age_scenario.CarbonTracker(global_settings, year_start_for_PDV=0).plot_C_pools_counterfactual_print_PDV()
    Secondary_conversion_scenario.CarbonTracker(global_settings, year_start_for_PDV=0).plot_C_pools_counterfactual_print_PDV()
    # Secondary_regrowth_scenario.CarbonTracker(global_settings, year_start_for_PDV=0).plot_C_pools_counterfactual_print_PDV()
    # Secondary_mature_regrowth_scenario.CarbonTracker(global_settings, year_start_for_PDV=0).plot_C_pools_counterfactual_print_PDV()

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
    datafile = '{}/data/processed/CHARM regional - BAU - SF_1.2 - DR_4p - Jun 3.xlsx'.format(root)

    global_settings = Global_by_country.Parameters(datafile, country_iso=iso)
    # run the land area calculator
    LAC = Land_area_calculator.LandCalculator(global_settings, plantation_counterfactual_code='secondary_plantation_age')
    # print("T PDV regrowth", LAC.total_pdv_plantation_secondary_regrowth)
    # print("T PDV conversion", LAC.total_pdv_plantation_secondary_conversion)
    # print("Area regrowth", sum(LAC.area_harvested_new_secondary_regrowth)+sum(LAC.area_harvested_new_secondary_mature_regrowth))
    # print("Area conversion", sum(LAC.area_harvested_new_secondary_conversion))

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
    # Read excel, if the cell has formula, it will be read as NaN
    # datafile = '{}/data/processed/CHARM regional - BAU SF_1.2 - May 12.xlsx'.format(root)
    # datafile = '{}/data/processed/CHARM regional - BAU SF_0 - May 12.xlsx'.format(root)
    # datafile = '{}/data/processed/CHARM regional - constant demand SF_1.2 - May 12.xlsx'.format(root)
    # datafile = '{}/data/processed/CHARM regional - constant demand SF_0 - May 12.xlsx'.format(root)

    datafile = '{}/data/processed/CHARM regional - BAU - SF_1.2 - DR_4p - Jun 3.xlsx'.format(root)
    # datafile = '{}/data/processed/CHARM regional - BAU SF_0 - DR_0p - May 12.xlsx'.format(root)
    # datafile = '{}/data/processed/CHARM regional - constant demand SF_1.2 - DR_0p - May 12.xlsx'.format(root)
    # datafile = '{}/data/processed/CHARM regional - constant demand SF_0 - DR_0p - May 12.xlsx'.format(root)

    scenarios = pd.read_excel(datafile, sheet_name='Inputs', usecols="A:B", skiprows=1)
    input_data = pd.read_excel(datafile, sheet_name='Inputs', skiprows=1)

    scenarionames, codes = [], []
    pdv_per_ha_conversion, pdv_per_ha_regrowth = [], []
    area_conversion_legacy, area_regrowth_legacy, area_plantation = [], [], []
    # It doesn't matter which conversion or regrowth scenario, the wood supply from the secondary forest is the same
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
            area_regrowth_legacy.append(sum(LAC_legacy.area_harvested_new_secondary_regrowth_combined))
            area_plantation.append(sum(LAC_legacy.area_harvested_new_plantation))

            secondary_wood.append(sum(LAC_secondary_plantation_age.output_need_secondary / 1000000))
            plantation_wood.append(sum(LAC_secondary_plantation_age.product_total_carbon) / 1000000 - sum(LAC_legacy.output_need_secondary) / 1000000)

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
                              'Secondary forest supply wood (mega tC)': secondary_wood,

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

get_global_annual_carbon_flow()