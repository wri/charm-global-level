#!/usr/bin/env python
__author__ = "Liqing Peng, Jessica Zionts, Tim Searchinger"
__copyright__ = "Copyright (C) 2020 WRI, The Carbon Harvest Model (CHarM) Project"
__maintainer__ = "Liqing Peng"
__email__ = "liqing.peng@wri.org"

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import Global_by_country, Plantation_scenario, Secondary_conversion_scenario, Secondary_regrowth_scenario, Land_area_calculator
# import Pasture_zero_counterfactual_scenario, Pasture_with_counterfactual_scenario
import Plantation_counterfactual_secondary_historic_scenario, Plantation_counterfactual_secondary_plantation_age_scenario, Plantation_counterfactual_unharvested_scenario


################################################### TESTING ####################################################

root = '../../'

def test_carbon_tracker():
    "TEST Carbon tracker"
    # set up the country
    iso = 'BRA'
    # datafile = './CHARM input Nancy Data v2 w substitution GR cap.xlsx'
    datafile = '{}/data/processed/CHARM input v3.xlsx'.format(root)
    global_settings = Global_by_country.Parameters(datafile, country_iso=iso)
    # Pasture_zero_counterfactual_scenario.CarbonTracker(global_settings, year_start_for_PDV=0).plot_C_pools_counterfactual_print_PDV()
    # Pasture_with_counterfactual_scenario.CarbonTracker(global_settings, year_start_for_PDV=0).plot_C_pools_counterfactual_print_PDV()

    Plantation_scenario.CarbonTracker(global_settings, year_start_for_PDV=0).plot_C_pools_counterfactual_print_PDV()
    # Secondary_conversion_scenario.CarbonTracker(global_settings, year_start_for_PDV=0).plot_C_pools_counterfactual_print_PDV()
    # Secondary_regrowth_scenario.CarbonTracker(global_settings, year_start_for_PDV=0).plot_C_pools_counterfactual()

    return

# test_carbon_tracker()
# exit()

def test_land_area_calculator():
    "TEST land area calculator"
    iso = 'USA'
    datafile = '{}/data/processed/CHARM input v3.xlsx'.format(root)
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

################################################### PLOTTING ####################################################

def plot_carbon_benefit_counterfactual_single_with_legend(pdv, df_stack, df_line, scenario_title, outfile):
    "Plot the one ha carbon storage graph, from old secondary conversion script"
    # Set up the figure
    fig, ax = plt.subplots(figsize=(11 ,8))
    colornames = ['DarkGreen', 'Sienna', 'Goldenrod', 'Darkgrey', 'Darkorange',  'Steelblue']

    # Positive carbon flux
    plt.stackplot(df_stack.index, df_stack['Stand and root storage'], df_stack['Slash and decaying root storage'], df_stack['Product storage'], df_stack['Displaced fossil emissions for concrete & steel'], df_stack['Landfill storage'], labels=df_stack.columns, colors=colornames[:-1])
    # Negative carbon flux
    plt.stackplot(df_stack.index, df_stack['Methane emission'], labels=['Methane emission'], color=colornames[-1])
    # Two lines
    df_line.plot(ax=ax, style=['k-', 'g--'], lw=2)

    # Fixme change pdv to some easily understandable name
    plt.text(2015, 80, 'PDV: {:.0f} tC/ha'.format(pdv), fontsize=16, fontweight='bold')

    ax.set_ylabel('Carbon sink/source (tC)', fontsize=20)
    ax.set_xlabel('Year', fontsize=18)
    ax.tick_params(axis = 'both', which = 'major', labelsize=16)
    plt.legend(bbox_to_anchor=(0.5, -0.25), loc='center', ncol=2, fontsize=14)
    plt.title(scenario_title, fontsize=20)
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.25)
    plt.show()
    # plt.savefig(outfile)
    # plt.close(fig)

    return


def plot_carbon_benefit_counterfactual_scenario(ax, result, pdv, scenario_title, yearlabel=False):
    "Plot the one ha carbon storage graph"
    df_stack = pd.DataFrame({'Stand and root storage': result.totalC_stand_pool[1:],
                             'Slash and decaying root storage': result.totalC_slash_root[1:],
                             'Product storage': result.totalC_product_pool[1:],
                             'Displaced concrete & steel fossil emissions': result.LLP_substitution_benefit[1:],
                             'Landfill storage': result.totalC_landfill_pool[1:],
                             'Methane emission': result.totalC_methane_emission[1:]
                             }, index=np.arange(2010, 2051))
    df_line = pd.DataFrame({'Total carbon benefit': result.total_carbon_benefit[1:],
                            'No-harvest scenario': result.counterfactual_biomass[1:]}, index=np.arange(2010, 2051))

    colornames = ['DarkGreen', 'Sienna', 'Goldenrod', 'Darkgrey', 'Darkorange',  'Steelblue']

    # Positive carbon flux
    plt.stackplot(df_stack.index, df_stack['Stand and root storage'], df_stack['Slash and decaying root storage'], df_stack['Product storage'], df_stack['Displaced concrete & steel fossil emissions'], df_stack['Landfill storage'], labels=df_stack.columns, colors=colornames[:-1])
    # Negative carbon flux
    plt.stackplot(df_stack.index, df_stack['Methane emission'], labels=['Methane emission'], color=colornames[-1])
    # Two lines
    df_line.plot(ax=ax, style=['-', '--'], color=["k", "limegreen"], lw=2.5, legend=False)

    ax.set_ylabel('Carbon sink/source (tC)', fontsize=20)
    if yearlabel is True:
        ax.set_xlabel('Year', fontsize=18)
    ax.tick_params(axis = 'both', which = 'major', labelsize=16)
    ax.annotate('2010-2050 Present Discounted Value: {:.0f} tC/ha'.format(pdv), xy=(0.1, 0.9), xycoords='axes fraction', fontsize=16, fontweight='bold')
    ax.set_title(scenario_title, fontsize=20)

    return


def one_ha_visualization_country(iso, datafile, dataversion, outfile):

    global_settings = Global_by_country.Parameters(datafile, country_iso=iso)
    result_plantation = Plantation_scenario.CarbonTracker(global_settings, year_start_for_PDV=0)
    result_conversion = Secondary_conversion_scenario.CarbonTracker(global_settings, year_start_for_PDV=0)
    result_regrowth = Secondary_regrowth_scenario.CarbonTracker(global_settings, year_start_for_PDV=0)

    df_parameters_1 = pd.DataFrame({'Rotation length (year)': global_settings.rotation_length_harvest,
                                  'Plantation growth rate (MgC/ha/year)': global_settings.GR_plantation,
                                  'Young secondary forest growth rate (MgC/ha/year)': global_settings.GR_young_secondary,
                                  'Old secondary forest growth rate (MgC/ha/year)': global_settings.GR_old_secondary,
                                  'Secondary forest initial carbon density (MgC/ha)': global_settings.C_harvest_density_secondary,
                                  '% LLP used for construction': global_settings.llp_construct_ratio*100,
                                  '% LLP that displaces concrete and steel': global_settings.llp_displaced_CS_ratio*100,
                                  'Substitution factor (tC/tC)': global_settings.coef_construt_substitution,
                                  '% C in landfill converted to methane': global_settings.landfill_methane_ratio*100
                                  }, index=['Value'])

    df_parameters_2 = pd.DataFrame({'% Slash plantation': global_settings.product_share_slash_plantation*100,
                                    '% Slash secondary': global_settings.product_share_slash_secondary*100,
                                    '% Slash thinning': global_settings.product_share_slash_thinning*100,
                                    '% Slash burning': global_settings.slash_burn*100,
                                    '% LLP': np.mean(global_settings.product_share_LLP)*100,
                                    '% SLP': np.mean(global_settings.product_share_SLP)*100,
                                    '% VSLP': np.mean(global_settings.product_share_VSLP)*100,
                                    'LLP half life': global_settings.half_life_LLP,
                                    'SLP half life': global_settings.half_life_SLP,
                                    'VSLP half life': global_settings.half_life_VSLP
                                    }, index=['Value'])

    # Set up the figure
    fig = plt.figure(figsize=(18, 12))
    ax1 = fig.add_subplot(2, 2, 1)
    plot_carbon_benefit_counterfactual_scenario(ax1, result_plantation, np.sum(result_plantation.annual_discounted_value), 'Plantation in {}'.format(global_settings.country_name))
    ax2 = fig.add_subplot(2, 2, 2)
    plot_carbon_benefit_counterfactual_scenario(ax2, result_conversion, np.sum(result_conversion.annual_discounted_value),
                                                'Secondary forest conversion to plantation in {}'.format(global_settings.country_name))
    ax3 = fig.add_subplot(2, 2, 3)
    plot_carbon_benefit_counterfactual_scenario(ax3, result_regrowth, np.sum(result_regrowth.annual_discounted_value),
                                                'Secondary forest regrowth in {}'.format(global_settings.country_name), yearlabel=True)
    # uniform the ylims
    maxylim = max(ax1.get_ylim()[1], ax2.get_ylim()[1], ax3.get_ylim()[1])
    minylim = min(ax1.get_ylim()[0], ax2.get_ylim()[0], ax3.get_ylim()[0])

    plt.setp(ax1, ylim=(minylim, maxylim))
    plt.setp(ax2, ylim=(minylim, maxylim))
    plt.setp(ax3, ylim=(minylim, maxylim))

    # set up the legend
    handles, labels = ax3.get_legend_handles_labels()
    fig.legend(handles, labels, loc=(0.49, 0.08), ncol=2, fontsize=14)
    # print out the parameters
    params = df_parameters_1.keys().tolist()
    for ip, param in enumerate(params):
        fig.text(0.51, 0.46-0.3/10*ip, '{}: {:.1f}'.format(param, df_parameters_1[param].values[0]), fontsize=14)
    params = df_parameters_2.keys().tolist()
    for ip, param in enumerate(params):
        fig.text(0.83, 0.48-0.3/10 * ip, '{}: {:.0f}'.format(param, df_parameters_2[param].values[0]), fontsize=14)

    fig.suptitle(dataversion, fontsize=16)
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.08)

    # plt.show(); exit()
    plt.savefig(outfile)
    plt.close()

    return

def plot_36countries():
    dataversion = 'v1'
    datafile = './CHARM input Nancy Data v1 w substitution.xlsx'
    outputdir = './Figure/Nancy v1/'

    # dataversion = 'v2'
    # datafile = './CHARM input Nancy Data v2 w substitution GR cap.xlsx'
    # outputdir = './Figure/Nancy v2 GR cap/'

    dataframe = pd.read_excel(datafile, sheet_name='Outputs', usecols="A:B", skiprows=1)

    for iso in dataframe['ISO'][1:]:
        print(iso)
        outputfile = os.path.join(outputdir, 'Cpools_1ha_{}_country_{}.png'.format(dataversion, iso))
        one_ha_visualization_country(iso, datafile, dataversion, outputfile)

# plot_36countries()
# exit()


def run_model():

    datafile = '{}/data/processed/CHARM input v3.xlsx'.format(root)

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
    datafile = '{}/data/processed/CHARM input v3 - new plantation scenarios.xlsx'.format(root)

    scenarios = pd.read_excel(datafile, sheet_name='Inputs', usecols="A:B", skiprows=1)
    input_data = pd.read_excel(datafile, sheet_name='Inputs', skiprows=1)

    scenarionames, codes = [], []
    pdv_per_ha_conversion, pdv_per_ha_regrowth = [], []
    area_conversion_legacy, area_regrowth_legacy = [], []
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
            # FIXME select one final plantation scenario
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
            LAC_secondary_plantation_age = Land_area_calculator.LandCalculator(global_settings,                                  plantation_counterfactual_code='secondary_plantation_age')
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

                              'PDV Secondary forest conversion (tC/ha)': pdv_per_ha_conversion,
                              'PDV Secondary regrowth conversion (tC/ha)': pdv_per_ha_regrowth,
                              'PDV Plantation old (tC/ha)': pdv_per_ha_plantation_legacy,
                              'PDV Plantation secondary_historic (tC/ha)': pdv_per_ha_plantation_secondary_historic,
                              'PDV Plantation secondary_plantation_age (tC/ha)': pdv_per_ha_plantation_secondary_plantation_age,
                              'PDV Plantation unharvested (tC/ha)': pdv_per_ha_plantation_unharvested,

                              'PDV secondary conversion plantation old (tC)': pdv_conversion_legacy,
                              'PDV secondary conversion plantation secondary_historic (tC)': pdv_conversion_secondary_historic,
                              'PDV secondary conversion plantation secondary_plantation_age (tC)': pdv_conversion_secondary_plantation_age,
                              'PDV secondary conversion plantation unharvested (tC)': pdv_conversion_unharvested,

                              'PDV secondary regrowth plantation old (tC)': pdv_regrowth_legacy,
                              'PDV secondary regrowth plantation secondary_historic (tC)': pdv_regrowth_secondary_historic,
                              'PDV secondary regrowth plantation scenario (tC)': pdv_regrowth_secondary_plantation_age,
                              'PDV secondary regrowth plantation unharvested (tC)': pdv_regrowth_unharvested,

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