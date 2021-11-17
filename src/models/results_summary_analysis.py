#!/usr/bin/env python
"""
1. Grab the national results
2. Calculate the global results 
3. Calculate the new tropical plantation scneario based on global results
"""
__author__ = "Liqing Peng"
__copyright__ = "Copyright (C) 2020-2021 WRI, The Carbon Harvest Model (CHARM) Project"
__credits__ = ["Liqing Peng", "Jessica Zionts", "Tim Searchinger", "Richard Waite"]
__license__ = 1
__version__ = "2021.11.1"
__maintainer__ = "Liqing Peng"
__email__ = "liqing.peng@wri.org"
__status__ = "Dev"

import numpy as np
import pandas as pd
import Global_by_country, Agricultural_land_tropical_scenario
import matplotlib.pyplot as plt


### Datafile
root = '../..'
discount_filename = '6p'
datafile = '{}/data/processed/CHARM regional - DR_{} - Nov 1.xlsx'.format(root, discount_filename)
figdir = '{}/../Paper/Publication/Figure'.format(root)


#############################################Read in model inputs###########################################
### Default parameters
Global = Global_by_country.Parameters(datafile, country_iso='BRA')
nyears = Global.nyears
rotation_length = Global.rotation_length_harvest # this must be ten years


##############################################Read in model outputs##########################################
# Lists
carbon_lists = ['Default: Plantation supply wood (mega tC)', 'Default: Secondary forest supply wood (mega tC)', 'S1 regrowth: total PDV (mega tC)', 'S1 regrowth: PDV plantation (mega tC)', 'S1 regrowth: PDV secondary (mega tC)', 'S2 conversion: total PDV (mega tC)', 'S3 mixture: total PDV (mega tC)', 'S4 125% GR: total PDV (mega tC)', 'S5 WFL 50% less: total PDV (mega tC)']
area_lists = ['Plantation area (ha)', 'S1 regrowth: Secondary area (ha)', 'S2 conversion: Secondary area (ha)', 'S3 mixture: Secondary area (ha)', 'S3 mixture: Secondary middle aged area (ha)', 'S3 mixture: Secondary mature area (ha)', 'S4 125% GR: Secondary area (ha)', 'S5 WFL 50% less: Secondary area (ha)']


def extract_global_outputs_summary(results):
    """Extract the 1-5th scenarios output"""
    ###The major scenarios
    cf_MtC_GtCO2 = 1/1000 * 44 / 12
    cf_ha_mha = 1/1000000
    carbon_costs_annual = results[['S1 regrowth: total PDV (mega tC)','S2 conversion: total PDV (mega tC)', 'S3 mixture: total PDV (mega tC)', 'S4 125% GR: total PDV (mega tC)', 'S5 WFL 50% less: total PDV (mega tC)']].sum() / 0.8 * cf_MtC_GtCO2 / 40
    area_total = results[['Plantation area (ha)', 'S1 regrowth: Secondary area (ha)', 'S2 conversion: Secondary area (ha)', 'S3 mixture: Secondary area (ha)', 'S4 125% GR: Secondary area (ha)', 'S5 WFL 50% less: Secondary area (ha)']].sum() / 0.8 * cf_ha_mha

    return carbon_costs_annual, area_total

def extract_global_wood_supply(results):
    """Extract the 1-5th scenarios output"""
    ###The major scenarios
    wood_supply = results[['Default: Plantation supply wood (mega tC)', 'Default: Secondary forest supply wood (mega tC)','125% GR: Plantation supply wood (mega tC)', '125% GR: Secondary forest supply wood (mega tC)','WFL50less: Plantation supply wood (mega tC)', 'WFL50less: Secondary forest supply wood (mega tC)']].sum() / 0.8 * 1000000  # mega tC to tC

    return wood_supply

def prepare_global_outputs_for_new_tropical_scenario(results):
    """Extract outputs for the 6th scenario"""
    # Get global carbon and area numbers
    carbon_global = results[results.select_dtypes(include=['number']).columns][
                        carbon_lists].sum() / 0.8 * 1000000  # mega tC to tC
    area_global = results[results.select_dtypes(include=['number']).columns][area_lists].sum() / 0.8

    return carbon_global, area_global


def run_new_tropical_plantations_scenario(results):
    """
    VERY IMPORTANT FEATURE OF THIS SCRIPT!
    Tropical New Plantation Scenario
    This is the 4th scenario
    require the input from the existing model outputs
    """

    ### New plantation land area assumption
    # We assume the 60 Mha of agricultural land are harvested evenly from 2021-2050 (2Mha per year, allowing the first 10 years for growth)
    area_harvested_agriland_annual_global = 2 * 1000000  # Mha per year

    area_harvested_new_agriland = np.zeros((nyears))
    # starting from 2021, after one rotation period
    area_harvested_new_agriland[rotation_length+1:] = area_harvested_agriland_annual_global
    area_harvested_agriland = np.cumsum(area_harvested_new_agriland) # This is to show the accumulate agricultural land

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
    # only tropical countries that are 10 years rotation period: Brazil, Congo, Indonesia, Vietnam
    ### 3. Calculate average tropical plantation wood harvest
    # weighted average of the output per ha for each harvest
    tropical_countries_iso = ['BRA', 'COD', 'IDN', 'VNM']
    # Get the plantation area
    area_plantation_tropical = [results.loc[results['ISO']==iso]['Plantation area (ha)'].values[0] for iso in tropical_countries_iso]
    # Get the output per ha at the 2020 year
    output_ha_tropical = [results.loc[results['ISO']==iso]['Output per ha Agricultural land conversion (tC/ha)'].values[0] for iso in tropical_countries_iso]
    weighted_sum = sum([area_plantation_tropical[i] * output_ha_tropical[i] for i in range(len(output_ha_tropical))])
    # Get the weighted average output per ha for the four countries
    output_ha_tropical_average = weighted_sum / sum(area_plantation_tropical)

    ### 4. Calculate the total wood harvest/production from the new plantation from agricultural land
        # 2020-2030, 2Mha per year*10 years means that 20 Mha will be harvested in the first 10 years.
        # 2030-2040, the hectares harvested in the previous decade will be harvested a second time (assuming a 10 year rotation) for a total of 20Mha harvested PLUS the first harvest of 2Mha of new hectares each year (20Mha new) for a total of 40 Mha harvested.
        # 2040-2050, the previous 40 Mha are harvested for either a second or third time, and 20 Mha are harvested for the first time.
        # in year 2050, 2Mha * 4 = 8Mha will be harvested
    # As a stair theory, every time you harvest the plantation,
    area_harvested_agriland_accumulate = area_harvested_agriland_annual_global * rotation_length + area_harvested_agriland_annual_global * rotation_length * 2 + area_harvested_agriland_annual_global * rotation_length * 3 + area_harvested_agriland_annual_global * 1 * 4
    # New plantation wood production for 2020-2050, tC, from 60 Mha agricultural land with continuous harvest
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
        Global = Global_by_country.Parameters(datafile, country_iso=iso)
        annual_discounted_value_nyears_agriland = np.zeros((nyears + nyears - 1, nyears))
        for year in range(nyears):
            #### This is the only line that requires the CHARM model run ####
            annual_discounted_value_nyears_agriland[year:year + nyears, year] = Agricultural_land_tropical_scenario.CarbonTracker(Global, year_start_for_PDV=year).annual_discounted_value[:]
        pdv_yearly_agriland = np.sum(annual_discounted_value_nyears_agriland, axis=0)

        total_pdv_agriland = np.zeros((nyears))
        for year in range(nyears):
            total_pdv_agriland[year] = pdv_yearly_agriland[year] * area_harvested_new_agriland[year]
        total_pdv_agriland_sum_country.append(np.sum(total_pdv_agriland))

    # use plantation area to weighted average from the tropical countries
    pdv_weighted_sum = sum([area_plantation_tropical[i] * total_pdv_agriland_sum_country[i] for i in range(len(total_pdv_agriland_sum_country))])
    # Get the weighted average output per ha for the four countries
    total_pdv_tropical_weighted_average = pdv_weighted_sum / sum(area_plantation_tropical)

    ### 8. Calculate global PDV as Total PDV for existing plantation + Total PDV for new plantation + New total PDV for secondary
    global_pdv = total_pdv_plantation + total_pdv_secondary_after_replace + total_pdv_tropical_weighted_average

    # Convert tC to GtCO2 per year
    carbon_cost_annual = global_pdv / 1000000000 * 44 / 12 / 40
    # Convert ha to Mha
    updated_secondary_area = (area_harvested_new_secondary_sum - area_reduced_secondary) / 1000000
    new_plantation_area = sum(area_harvested_new_agriland) / 1000000

    ### 9. Calculate the total secondary wood supply reduced from the new plantation
    total_wood_secondary_after_replace = total_wood_secondary - wood_supply_agriland
    total_wood_plantation_after_replace = total_wood_plantation + wood_supply_agriland

    # TEST print
    # print('pdv_average_secondary_regrowth', pdv_average_secondary_regrowth)
    # print('total_wood_secondary', total_wood_secondary)
    # print('area_harvested_new_secondary_sum', area_harvested_new_secondary_sum)
    # print('yield_average_secondary', yield_average_secondary)
    # print('output_ha_tropical_average', output_ha_tropical_average)
    # print('wood_supply_agriland', wood_supply_agriland)
    # print('area_reduced_secondary', area_reduced_secondary)
    # print('total_pdv_secondary_after_replace', total_pdv_secondary_after_replace)
    # print('total_pdv_tropical_weighted_average', total_pdv_tropical_weighted_average)
    # print('total_pdv_secondary_after_replace', total_pdv_secondary_after_replace)
    # print('total_pdv_plantation', total_pdv_plantation)
    # print('global_pdv', global_pdv)
    # print('carbon_cost_annual', carbon_cost_annual)
    # print('updated_secondary_area', updated_secondary_area)

    return carbon_cost_annual, updated_secondary_area, new_plantation_area, total_wood_secondary_after_replace, total_wood_plantation_after_replace

def export_results_to_excel():
    carbon_costs = np.zeros((12, 6))
    required_area = np.zeros((12, 8))
    wood_supply = np.zeros((12, 8))
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
                carbon_costs[row, 4:6] = carbon_main.values[3:]
                required_area[row, :3] = land_main.values[1:4]
                required_area[row, 4:6] = land_main.values[4:]
                wood_supply[row, :2] = wood_main.values[:2]
                wood_supply[row, 4:8] = wood_main.values[2:]
                # The 4th scenario new tropical plantation
                carbon_costs[row, 3] = carbon_last
                required_area[row, 3] = secondary_land_last

                required_area[row, 6] = land_main.values[0]  # The existing plantation
                required_area[row, 7] = new_tropical_land_last  # The new plantation

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

    outfile = '{}/data/processed/derivative/CHARM_global_carbon_land_summary.xlsx'.format(root)
    # Convert to pandas dataframe
    scenarios = ['S1 Secondary forest harvest + regrowth', 'S2 Secondary forest harvest + conversion', 'S3 Secondary forest mixed harvest',
     'S4 New tropical plantations', 'S5 Higher plantation productivity', 'S6 50% less 2050 wood fuel demand']
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
                             'WFL50less: Plantation supply wood (mega tC)',
                             'WFL50less: Secondary forest supply wood (mega tC)']
        area_df = pd.DataFrame(required_area, index=row_index, columns=land_areas)
        wood_df = pd.DataFrame(wood_supply, index=row_index, columns=wood_supply_items)
        write_excel(outfile, 'Land (Mha) DR_{}'.format(discount_filename), area_df)
        write_excel(outfile, 'Wood supply (mega tC) DR_{}'.format(discount_filename), wood_df)

    return

# export_results_to_excel()
# exit()

def collect_all_discount_rates_results():
    "For Appendix 3"
    infile = '{}/data/processed/derivative/CHARM_global_carbon_land_summary.xlsx'.format(root)
    df_list = []
    for dr in ('0p', '2p', '4p', '6p'):
        carbon = pd.read_excel(infile, sheet_name='CO2 (Gt per yr) DR_{}'.format(dr), index_col=0)
        carbon_sel = carbon.loc[['BAU_NOSUB_ALL', 'BAU_SUBON_ALL']]
        df_list.append(carbon_sel.rename(index={'BAU_NOSUB_ALL': 'Gross emissions', 'BAU_SUBON_ALL':'Net emissions including substitution savings'}))
    big_table = pd.concat(df_list)
    big_table.to_csv('{}/data/processed/derivative/carbon_results_all_discountrate.csv'.format(root))

# collect_all_discount_rates_results()
# exit()

def barplot_all_scenarios_percentage():

    def read_dataframe(tabname):
        infile = '{}/data/processed/derivative/CHARM_global_carbon_land_summary.xlsx'.format(root)
        # Read in the excel file using the first column as the index
        df = pd.read_excel(infile, sheet_name=tabname, index_col=0)
        # Prepare data for the BAU vs CST plot
        df.loc['NewDemand_NOSUB_ALL'] = df.loc['BAU_NOSUB_ALL'] - df.loc['CST_NOSUB_ALL']
        df.loc['BAU_SubEffect_ALL'] = df.loc['BAU_SUBON_ALL'] - df.loc['BAU_NOSUB_ALL']
        return df

    def stacked_barplot_attribute_demand_substitution_carbon(result_df, title, ylabel):
        "Plot multiple scenarios"
        fig, ax = plt.subplots(1, figsize=(14, 8))
        result_df[result_df.select_dtypes(include=['number']).columns] *= -1
        plt.bar(result_df.columns, result_df.loc['CST_NOSUB_ALL'], color='#DB4444', width=0.5)
        plt.bar(result_df.columns, result_df.loc['NewDemand_NOSUB_ALL'], bottom=result_df.loc['CST_NOSUB_ALL'], color='#E17979', width=0.5)
        plt.bar(result_df.columns, result_df.loc['BAU_SubEffect_ALL'], color='#337AE3', width=0.5)
        plt.bar(result_df.columns, result_df.loc['BAU_SUBON_ALL'], ls='dashed', facecolor="None", edgecolor='k', width=0.5)
        # x and y limits
        # plt.xlim(-0.6, 10.5)
        # plt.ylim(-1600, 2000)
        plt.ylabel(ylabel, fontsize=14)
        # remove spines
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['top'].set_visible(False)
        # ax.spines['bottom'].set_visible(False)
        plt.axhline(y=0, color='k', lw=1, linestyle='-', label='_nolegend_') # skip legend
        # grid
        ax.set_axisbelow(True)
        ax.yaxis.grid(color='gray', linestyle='dashed', alpha=0.7)
        # x ticks
        xticks_labels = ['S1 Secondary forest\nHarvest + Regrowth', 'S2 Secondary forest\nHarvest + Conversion', 'S3 Secondary forest\nMixed harvest',
                         'S4 New\nTropical plantations', 'S5 Higher\nPlantation productivity', 'S6 50% less 2050\nWood fuel demand']
        plt.xticks(result_df.columns, labels=xticks_labels)
        # bar labels
        base = result_df.loc['BAU_NOSUB_ALL']
        for number, rec in enumerate(ax.patches[:18]):
            height = rec.get_height()
            # This is to make sure the turn of the group of scenario
            bar_scenario_group = number%6
            ax.text(rec.get_x() + rec.get_width() / 2, rec.get_y() + height / 2,
                    "{:.0f}%".format(height/base[bar_scenario_group]*100),
                      ha='center', va='bottom')

        for number, rec in enumerate(ax.patches[18:]):
            height = rec.get_height()
            # This is to make sure the turn of the group of scenario
            ax.text(rec.get_x() + rec.get_width() / 2, rec.get_y() + height,
                    "{:.1f}".format(height),
                      ha='center', va='bottom', fontweight='bold')

        # title and legend
        legend_label = ['2010 supply level', 'Additional BAU demand', 'Substitution benefit', 'Net carbon impact']
        plt.legend(legend_label, ncol=4, bbox_to_anchor=([1, 1.05, 0, 0]), frameon=False, fontsize=13)
        plt.title('{}\n'.format(title), loc='left', fontsize=16)
        # plt.show()
        plt.savefig('{}/carbon_cost_annual_percentage_6scenarios.png'.format(figdir))

        return

    def stacked_barplot_attribute_demand_substitution_land(result_df, title, ylabel):
        "Plot multiple scenarios"
        # Land area requirement from additional demand is the secondary area added upon the CST.
        result_df_secondary = result_df.iloc[:, range(6)]
        result_df_secondary.loc['Existing plantations'] = result_df.loc['BAU_SUBON_ALL', 'Existing plantations']
        result_df_secondary.loc['New plantations'] = 0
        result_df_secondary.loc['New plantations', 'S4 New tropical plantations'] = result_df.loc['BAU_SUBON_ALL', 'New plantations']

        fig, ax = plt.subplots(1, figsize=(14, 8))
        plt.bar(result_df_secondary.columns, result_df_secondary.loc['Existing plantations'], color='#7cc096', edgecolor='w', width=0.5, hatch='//')
        plt.bar(result_df_secondary.columns, result_df_secondary.loc['CST_NOSUB_ALL'], bottom=result_df_secondary.loc['Existing plantations'], color='#408107', width=0.5)
        plt.bar(result_df_secondary.columns, result_df_secondary.loc['NewDemand_NOSUB_ALL'], bottom=result_df_secondary.loc['Existing plantations']+result_df_secondary.loc['CST_NOSUB_ALL'], color='#76aa08', width=0.5)
        plt.bar(result_df_secondary.columns, result_df_secondary.loc['New plantations'], bottom=result_df_secondary.loc['Existing plantations']+result_df_secondary.loc['CST_NOSUB_ALL']+result_df_secondary.loc['NewDemand_NOSUB_ALL'], edgecolor='w', color='#48f2a8', width=0.5, hatch='//')
        plt.bar(result_df_secondary.columns, result_df_secondary.loc['BAU_SUBON_ALL'], bottom=result_df_secondary.loc['Existing plantations'], facecolor="None", edgecolor='k', width=0.5)
        # x and y limits
        # plt.xlim(-0.6, 10.5)
        # plt.ylim(-1600, 2000)
        plt.ylabel(ylabel, fontsize=14)
        # remove spines
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['top'].set_visible(False)
        # ax.spines['bottom'].set_visible(False)
        # grid
        ax.set_axisbelow(True)
        ax.yaxis.grid(color='gray', linestyle='dashed', alpha=0.7)
        # x ticks
        xticks_labels = ['S1 Secondary forest\nHarvest + Regrowth', 'S2 Secondary forest\nHarvest + Conversion', 'S3 Secondary forest\nMixed harvest',
     'S4 New\nTropical plantations', 'S5 Higher\nPlantation productivity', 'S6 50% less 2050\nWood fuel demand']
        plt.xticks(result_df_secondary.columns, labels=xticks_labels)
        # bar labels
        base = result_df_secondary.loc['BAU_NOSUB_ALL'] + result_df_secondary.loc['Existing plantations'] + result_df_secondary.loc['New plantations']
        for number, rec in enumerate(ax.patches[:18]):
            height = rec.get_height()
            # This is to make sure the turn of the group of scenario
            bar_scenario_group = number%6
            ax.text(rec.get_x() + rec.get_width() / 2, rec.get_y() + height / 2,
                    "{:.0f}%".format(height/base[bar_scenario_group]*100),
                      ha='center', va='bottom')
        # Add the fourth scenario's new tropical plantations percentage
        ax.text(ax.patches[21].get_x() + ax.patches[21].get_width() / 2, ax.patches[21].get_y() + ax.patches[21].get_height()/2,
                "{:.0f}%".format(ax.patches[21].get_height() / base[3] * 100),
                ha='center', va='bottom')
        # Add the final absolute numbers at the top
        area_total = result_df_secondary.loc['Existing plantations'] + result_df_secondary.loc['CST_NOSUB_ALL'] + result_df_secondary.loc['NewDemand_NOSUB_ALL'] + result_df_secondary.loc['New plantations']
        for number, rec in enumerate(ax.patches[:6]):
            # This is to make sure the turn of the group of scenario
            ax.text(rec.get_x() + rec.get_width() / 2, rec.get_y() + area_total[number],
                    "{:.0f}".format(area_total[number]),
                      ha='center', va='bottom', fontweight='bold')

        # title and legend
        legend_label = ['Existing plantations', '2010 supply level', 'Additional BAU demand', 'New tropical plantations', 'Total secondary forest area']
        plt.legend(legend_label, ncol=2, bbox_to_anchor=([1, 1.15, 0, 0]), frameon=False, fontsize=14)

        # sort both labels and handles by labels
        plt.subplots_adjust(top=0.83)
        plt.title('{}\n'.format(title), loc='left', fontsize=16, y=1.08)
        # plt.savefig('{}/land_requirement_6scenarios.png'.format(figdir))
        plt.show()

        return

    def stacked_barplot_attribute_IND_WFL_carbon(result_df, title, ylabel):
        "Plot multiple scenarios"
        fig, ax = plt.subplots(1, figsize=(14, 8))
        # Convert carbon impact to carbon cost
        result_df[result_df.select_dtypes(include=['number']).columns] *= -1
        # Calculate the area for IND and the area for WFL
        plt.bar(result_df.columns, result_df.loc['BAU_SUBON_ALL']*result_df.loc['BAU_SUBON_IND']/(result_df.loc['BAU_SUBON_IND']+result_df.loc['BAU_SUBON_WFL']), color='#ab5b1a', width=0.5)
        plt.bar(result_df.columns, result_df.loc['BAU_SUBON_ALL']*result_df.loc['BAU_SUBON_WFL']/(result_df.loc['BAU_SUBON_IND']+result_df.loc['BAU_SUBON_WFL']), bottom=result_df.loc['BAU_SUBON_ALL']*result_df.loc['BAU_SUBON_IND']/(result_df.loc['BAU_SUBON_IND']+result_df.loc['BAU_SUBON_WFL']), color='#d48f57', width=0.5)
        # plt.bar(result_df.columns, result_df.loc['BAU_SUBON_ALL'], ls='dashed', facecolor="None", edgecolor='k', width=0.5)
        # x and y limits
        # plt.xlim(-0.6, 10.5)
        # plt.ylim(-1600, 2000)
        plt.ylabel(ylabel, fontsize=14)
        # remove spines
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['top'].set_visible(False)
        # ax.spines['bottom'].set_visible(False)
        # grid
        ax.set_axisbelow(True)
        ax.yaxis.grid(color='gray', linestyle='dashed', alpha=0.7)
        # x ticks
        xticks_labels = ['S1 Secondary forest\nHarvest + Regrowth', 'S2 Secondary forest\nHarvest + Conversion', 'S3 Secondary forest\nMixed harvest', 'S4 New\nTropical plantations', 'S5 Higher\nPlantation productivity', 'S6 50% less 2050\nWood fuel demand']
        plt.xticks(result_df.columns, labels=xticks_labels)
        # bar labels
        base = result_df.loc['BAU_SUBON_ALL']
        for number, rec in enumerate(ax.patches[:12]):
            height = rec.get_height()
            # This is to make sure the turn of the group of scenario
            bar_scenario_group = number%6
            ax.text(rec.get_x() + rec.get_width() / 2, rec.get_y() + height / 2,
                    "{:.0f}%".format(height/base[bar_scenario_group]*100),
                      ha='center', va='bottom')
        # Add the final absolute numbers at the top
        for number, rec in enumerate(ax.patches[:6]):
            # This is to make sure the turn of the group of scenario
            ax.text(rec.get_x() + rec.get_width() / 2, rec.get_y() + base[number],
                    "{:.1f}".format(base[number]),
                    ha='center', va='bottom', fontweight='bold')
        # title and legend
        legend_label = ['Industrial roundwood', 'Wood fuel', 'Total carbon impact']
        plt.legend(legend_label, ncol=4, bbox_to_anchor=([1, 1.05, 0, 0]), frameon=False, fontsize=13)
        plt.title('{}\n'.format(title), loc='left', fontsize=16)
        # plt.show()
        plt.savefig('{}/carbon_cost_annual_IND_WFL_6scenarios.png'.format(figdir))

        return

    def stacked_barplot_attribute_IND_WFL_land(result_df, title, ylabel):
        "Plot multiple scenarios"
        result_df_secondary = result_df.iloc[:, range(6)]
        # Land area requires extra steps.
        # 0. Copy the existing plantations data to a new row
        result_df_secondary.loc['Existing plantations ALL'] = result_df.loc['BAU_SUBON_ALL', 'Existing plantations']
        result_df_secondary.loc['Existing plantations IND'] = result_df.loc['BAU_SUBON_IND', 'Existing plantations']
        result_df_secondary.loc['Existing plantations WFL'] = result_df.loc['BAU_SUBON_WFL', 'Existing plantations']
        result_df_secondary.loc['New plantations'] = 0
        result_df_secondary.loc['New plantations', 'S4 New tropical plantations'] = result_df.loc['BAU_SUBON_ALL', 'New plantations']
        # 1. Add the secondary area and plantation area together to get total area
        area_ALL = result_df_secondary.loc['BAU_SUBON_ALL'] + result_df_secondary.loc['Existing plantations ALL'] + result_df_secondary.loc['New plantations']
        area_IND = result_df_secondary.loc['BAU_SUBON_IND'] + result_df_secondary.loc['Existing plantations IND'] + result_df_secondary.loc['New plantations']
        area_WFL = result_df_secondary.loc['BAU_SUBON_WFL'] + result_df_secondary.loc['Existing plantations WFL'] + result_df_secondary.loc['New plantations']
        # 2. compare IND and WFL with percentage/ratio
        # 3. multiply by ALL to get the quantity
        fig, ax = plt.subplots(1, figsize=(14, 8))
        # plt.bar(result_df_secondary.columns, result_df_secondary.loc['Existing plantations'], color='#7c3d16', edgecolor='k', width=0.5)
        plt.bar(result_df_secondary.columns, area_ALL*area_IND/(area_IND+area_WFL), color='#ab5b1a', width=0.5)
        plt.bar(result_df_secondary.columns, area_ALL*area_WFL/(area_IND+area_WFL), bottom=area_ALL*area_IND/(area_IND+area_WFL), color='#d48f57', width=0.5)
        # plt.bar(result_df_secondary.columns, area_ALL, facecolor="None", edgecolor='k', width=0.5)
        # x and y limits
        # plt.xlim(-0.6, 10.5)
        # plt.ylim(-1600, 2000)
        plt.ylabel(ylabel, fontsize=14)
        # remove spines
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['top'].set_visible(False)
        # ax.spines['bottom'].set_visible(False)
        # grid
        ax.set_axisbelow(True)
        ax.yaxis.grid(color='gray', linestyle='dashed', alpha=0.7)
        # x ticks
        xticks_labels = ['S1 Secondary forest\nHarvest + Regrowth', 'S2 Secondary forest\nHarvest + Conversion', 'S3 Secondary forest\nMixed harvest', 'S4 New\nTropical plantations', 'S5 Higher\nPlantation productivity', 'S6 50% less 2050\nWood fuel demand']
        plt.xticks(result_df_secondary.columns, labels=xticks_labels)
        # bar labels
        for number, rec in enumerate(ax.patches[:12]):
            height = rec.get_height()
            # This is to make sure the turn of the group of scenario
            bar_scenario_group = number%6
            ax.text(rec.get_x() + rec.get_width() / 2, rec.get_y() + height / 2,
                    "{:.0f}%".format(height/area_ALL[bar_scenario_group]*100),
                      ha='center', va='bottom')
        # Add the final absolute numbers at the top
        for number, rec in enumerate(ax.patches[:6]):
            # This is to make sure the turn of the group of scenario
            ax.text(rec.get_x() + rec.get_width() / 2, rec.get_y() + area_ALL[number],
                    "{:.0f}".format(area_ALL[number]),
                      ha='center', va='bottom', fontweight='bold')

        # title and legend
        legend_label = ['Industrial roundwood', 'Wood fuel']
        plt.legend(legend_label, ncol=2, bbox_to_anchor=([1, 1.15, 0, 0]), frameon=False, fontsize=14)

        # sort both labels and handles by labels
        plt.subplots_adjust(top=0.83)
        plt.title('{}\n'.format(title), loc='left', fontsize=16, y=1.08)
        plt.savefig('{}/land_requirement_IND_WFL_6scenarios.png'.format(figdir))
        # plt.show()

        return


    # carbon_df = read_dataframe('CO2 (Gt per yr) DR_{}'.format(discount_filename))
    # stacked_barplot_attribute_IND_WFL_carbon(carbon_df, 'Carbon costs', 'GtCO2/year')
    # stacked_barplot_attribute_demand_substitution_carbon(carbon_df, 'Carbon costs', 'GtCO2/year')

    # land_df = read_dataframe('Land (Mha) DR_{}'.format(discount_filename))
    # stacked_barplot_attribute_IND_WFL_land(land_df, 'Land requirements 2010-2050', 'Mha')

    return

barplot_all_scenarios_percentage()

def barplot_all_scenarios_quantity():
    "Use quantity in the report"
    def read_dataframe(tabname):
        infile = '{}/data/processed/derivative/CHARM_global_carbon_land_summary.xlsx'.format(root)
        # Read in the excel file using the first column as the index
        df = pd.read_excel(infile, sheet_name=tabname, index_col=0)
        # Prepare data for the BAU vs CST plot
        df.loc['NewDemand_NOSUB_ALL'] = df.loc['BAU_NOSUB_ALL'] - df.loc['CST_NOSUB_ALL']
        df.loc['BAU_SubEffect_ALL'] = df.loc['BAU_SUBON_ALL'] - df.loc['BAU_NOSUB_ALL']
        return df

    def stacked_barplot_attribute_demand_substitution_carbon(result_df, title, ylabel):
        "Plot multiple scenarios"
        fig, ax = plt.subplots(1, figsize=(14, 8))
        result_df[result_df.select_dtypes(include=['number']).columns] *= -1
        plt.bar(result_df.columns, result_df.loc['CST_NOSUB_ALL'], color='#DB4444', width=0.5)
        plt.bar(result_df.columns, result_df.loc['NewDemand_NOSUB_ALL'], bottom=result_df.loc['CST_NOSUB_ALL'], color='#E17979', width=0.5)
        plt.bar(result_df.columns, result_df.loc['BAU_SubEffect_ALL'], color='#337AE3', width=0.5)
        plt.bar(result_df.columns, result_df.loc['BAU_SUBON_ALL'], ls='dashed', facecolor="None", edgecolor='k', width=0.5)
        # x and y limits
        # plt.xlim(-0.6, 10.5)
        # plt.ylim(-1600, 2000)
        plt.ylabel(ylabel, fontsize=14)
        # remove spines
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['top'].set_visible(False)
        # ax.spines['bottom'].set_visible(False)
        plt.axhline(y=0, color='k', lw=1, linestyle='-', label='_nolegend_') # skip legend
        # grid
        ax.set_axisbelow(True)
        ax.yaxis.grid(color='gray', linestyle='dashed', alpha=0.7)
        # x ticks
        xticks_labels = ['S1 Secondary forest\nHarvest + Regrowth', 'S2 Secondary forest\nHarvest + Conversion', 'S3 Secondary forest\nMixed harvest',
                         'S4 New\nTropical plantations', 'S5 Higher\nPlantation productivity', 'S6 50% less 2050\nWood fuel demand']
        plt.xticks(result_df.columns, labels=xticks_labels)
        # bar labels
        # base = result_df.loc['BAU_NOSUB_ALL']
        for number, rec in enumerate(ax.patches[:18]):
            height = rec.get_height()
            # This is to make sure the turn of the group of scenario
            ax.text(rec.get_x() + rec.get_width() / 2, rec.get_y() + height / 2,
                    "{:.1f}".format(height),
                      ha='center', va='bottom')

        for number, rec in enumerate(ax.patches[18:]):
            height = rec.get_height()
            # This is to make sure the turn of the group of scenario
            ax.text(rec.get_x() + rec.get_width() / 2, rec.get_y() + height,
                    "{:.1f}".format(height),
                      ha='center', va='bottom', fontweight='bold')

        # title and legend
        legend_label = ['2010 supply level', 'Additional BAU demand', 'Substitution benefit', 'Net carbon impact']
        plt.legend(legend_label, ncol=4, bbox_to_anchor=([1, 1.05, 0, 0]), frameon=False, fontsize=13)
        plt.title('{}\n'.format(title), loc='left', fontsize=16)
        # plt.show()
        plt.savefig('{}/annual_carbon_cost_6scenarios.png'.format(figdir))

        return

    def stacked_barplot_attribute_demand_substitution_land(result_df, title, ylabel):
        "Plot multiple scenarios"
        # Land area requirement from additional demand is the secondary area added upon the CST.
        result_df_secondary = result_df.iloc[:, range(6)]
        result_df_secondary.loc['Existing plantations'] = result_df.loc['BAU_SUBON_ALL', 'Existing plantations']
        result_df_secondary.loc['New plantations'] = 0
        result_df_secondary.loc['New plantations', 'S4 New tropical plantations'] = result_df.loc['BAU_SUBON_ALL', 'New plantations']

        fig, ax = plt.subplots(1, figsize=(14, 8))
        plt.bar(result_df_secondary.columns, result_df_secondary.loc['Existing plantations'], color='#7cc096', edgecolor='w', width=0.5, hatch='//')
        plt.bar(result_df_secondary.columns, result_df_secondary.loc['CST_NOSUB_ALL'], bottom=result_df_secondary.loc['Existing plantations'], color='#408107', width=0.5)
        plt.bar(result_df_secondary.columns, result_df_secondary.loc['NewDemand_NOSUB_ALL'], bottom=result_df_secondary.loc['Existing plantations']+result_df_secondary.loc['CST_NOSUB_ALL'], color='#76aa08', width=0.5)
        plt.bar(result_df_secondary.columns, result_df_secondary.loc['New plantations'], bottom=result_df_secondary.loc['Existing plantations']+result_df_secondary.loc['CST_NOSUB_ALL']+result_df_secondary.loc['NewDemand_NOSUB_ALL'], edgecolor='w', color='#48f2a8', width=0.5, hatch='//')
        plt.bar(result_df_secondary.columns, result_df_secondary.loc['BAU_SUBON_ALL'], bottom=result_df_secondary.loc['Existing plantations'], facecolor="None", edgecolor='k', width=0.5)
        # x and y limits
        # plt.xlim(-0.6, 10.5)
        # plt.ylim(-1600, 2000)
        plt.ylabel(ylabel, fontsize=14)
        # remove spines
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['top'].set_visible(False)
        # ax.spines['bottom'].set_visible(False)
        # grid
        ax.set_axisbelow(True)
        ax.yaxis.grid(color='gray', linestyle='dashed', alpha=0.7)
        # x ticks
        xticks_labels = ['S1 Secondary forest\nHarvest + Regrowth', 'S2 Secondary forest\nHarvest + Conversion', 'S3 Secondary forest\nMixed harvest',
     'S4 New\nTropical plantations', 'S5 Higher\nPlantation productivity', 'S6 50% less 2050\nWood fuel demand']
        plt.xticks(result_df_secondary.columns, labels=xticks_labels)
        # bar labels
        base = result_df_secondary.loc['BAU_NOSUB_ALL'] + result_df_secondary.loc['Existing plantations'] + result_df_secondary.loc['New plantations']
        for number, rec in enumerate(ax.patches[:18]):
            height = rec.get_height()
            # This is to make sure the turn of the group of scenario
            ax.text(rec.get_x() + rec.get_width() / 2, rec.get_y() + height / 2,
                    "{:.0f}".format(height),
                      ha='center', va='bottom')
        # Add the fourth scenario's new tropical plantations percentage
        ax.text(ax.patches[21].get_x() + ax.patches[21].get_width() / 2, ax.patches[21].get_y() + ax.patches[21].get_height()/2,
                "{:.0f}".format(ax.patches[21].get_height()),
                ha='center', va='bottom')
        # Add the final absolute numbers at the top
        area_total = result_df_secondary.loc['Existing plantations'] + result_df_secondary.loc['CST_NOSUB_ALL'] + result_df_secondary.loc['NewDemand_NOSUB_ALL'] + result_df_secondary.loc['New plantations']
        for number, rec in enumerate(ax.patches[:6]):
            # This is to make sure the turn of the group of scenario
            ax.text(rec.get_x() + rec.get_width() / 2, rec.get_y() + area_total[number],
                    "{:.0f}".format(area_total[number]),
                      ha='center', va='bottom', fontweight='bold')

        # title and legend
        legend_label = ['Existing plantations', '2010 supply level', 'Additional BAU demand', 'New tropical plantations', 'Total secondary forest area']
        plt.legend(legend_label, ncol=2, bbox_to_anchor=([1, 1.15, 0, 0]), frameon=False, fontsize=14)

        # sort both labels and handles by labels
        plt.subplots_adjust(top=0.83)
        plt.title('{}\n'.format(title), loc='left', fontsize=16, y=1.08)
        plt.savefig('{}/land_requirement_6scenarios.png'.format(figdir))
        # plt.show()

        return

    def stacked_barplot_attribute_IND_WFL_carbon(result_df, title, ylabel):
        "Plot multiple scenarios"
        fig, ax = plt.subplots(1, figsize=(14, 8))
        # Convert carbon impact to carbon cost
        result_df[result_df.select_dtypes(include=['number']).columns] *= -1
        # Calculate the area for IND and the area for WFL
        plt.bar(result_df.columns, result_df.loc['BAU_SUBON_ALL']*result_df.loc['BAU_SUBON_IND']/(result_df.loc['BAU_SUBON_IND']+result_df.loc['BAU_SUBON_WFL']), color='#ab5b1a', width=0.5)
        plt.bar(result_df.columns, result_df.loc['BAU_SUBON_ALL']*result_df.loc['BAU_SUBON_WFL']/(result_df.loc['BAU_SUBON_IND']+result_df.loc['BAU_SUBON_WFL']), bottom=result_df.loc['BAU_SUBON_ALL']*result_df.loc['BAU_SUBON_IND']/(result_df.loc['BAU_SUBON_IND']+result_df.loc['BAU_SUBON_WFL']), color='#d48f57', width=0.5)
        # plt.bar(result_df.columns, result_df.loc['BAU_SUBON_ALL'], ls='dashed', facecolor="None", edgecolor='k', width=0.5)
        # x and y limits
        # plt.xlim(-0.6, 10.5)
        # plt.ylim(-1600, 2000)
        plt.ylabel(ylabel, fontsize=14)
        # remove spines
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['top'].set_visible(False)
        # ax.spines['bottom'].set_visible(False)
        # grid
        ax.set_axisbelow(True)
        ax.yaxis.grid(color='gray', linestyle='dashed', alpha=0.7)
        # x ticks
        xticks_labels = ['S1 Secondary forest\nHarvest + Regrowth', 'S2 Secondary forest\nHarvest + Conversion', 'S3 Secondary forest\nMixed harvest', 'S4 New\nTropical plantations', 'S5 Higher\nPlantation productivity', 'S6 50% less 2050\nWood fuel demand']
        plt.xticks(result_df.columns, labels=xticks_labels)
        # bar labels
        base = result_df.loc['BAU_SUBON_ALL']
        for number, rec in enumerate(ax.patches[:12]):
            height = rec.get_height()
            # This is to make sure the turn of the group of scenario
            ax.text(rec.get_x() + rec.get_width() / 2, rec.get_y() + height / 2,
                    "{:.1f}".format(height),
                      ha='center', va='bottom')
        # Add the final absolute numbers at the top
        for number, rec in enumerate(ax.patches[:6]):
            # This is to make sure the turn of the group of scenario
            ax.text(rec.get_x() + rec.get_width() / 2, rec.get_y() + base[number],
                    "{:.1f}".format(base[number]),
                    ha='center', va='bottom', fontweight='bold')
        # title and legend
        legend_label = ['Industrial roundwood', 'Wood fuel', 'Total carbon impact']
        plt.legend(legend_label, ncol=4, bbox_to_anchor=([1, 1.05, 0, 0]), frameon=False, fontsize=13)
        plt.title('{}\n'.format(title), loc='left', fontsize=16)
        plt.show()
        # plt.savefig('{}/annual_carbon_cost_IND_WFL_6scenarios.png'.format(figdir))

        return

    def stacked_barplot_attribute_IND_WFL_land(result_df, title, ylabel):
        "Plot multiple scenarios"
        result_df_secondary = result_df.iloc[:, range(6)]
        # Land area requires extra steps.
        # 0. Copy the existing plantations data to a new row
        result_df_secondary.loc['Existing plantations ALL'] = result_df.loc['BAU_SUBON_ALL', 'Existing plantations']
        result_df_secondary.loc['Existing plantations IND'] = result_df.loc['BAU_SUBON_IND', 'Existing plantations']
        result_df_secondary.loc['Existing plantations WFL'] = result_df.loc['BAU_SUBON_WFL', 'Existing plantations']
        result_df_secondary.loc['New plantations'] = 0
        result_df_secondary.loc['New plantations', 'S4 New tropical plantations'] = result_df.loc['BAU_SUBON_ALL', 'New plantations']
        # 1. Add the secondary area and plantation area together to get total area
        area_ALL = result_df_secondary.loc['BAU_SUBON_ALL'] + result_df_secondary.loc['Existing plantations ALL'] + result_df_secondary.loc['New plantations']
        area_IND = result_df_secondary.loc['BAU_SUBON_IND'] + result_df_secondary.loc['Existing plantations IND'] + result_df_secondary.loc['New plantations']
        area_WFL = result_df_secondary.loc['BAU_SUBON_WFL'] + result_df_secondary.loc['Existing plantations WFL'] + result_df_secondary.loc['New plantations']
        # 2. compare IND and WFL with percentage/ratio
        # 3. multiply by ALL to get the quantity
        fig, ax = plt.subplots(1, figsize=(14, 8))
        # plt.bar(result_df_secondary.columns, result_df_secondary.loc['Existing plantations'], color='#7c3d16', edgecolor='k', width=0.5)
        plt.bar(result_df_secondary.columns, area_ALL*area_IND/(area_IND+area_WFL), color='#ab5b1a', width=0.5)
        plt.bar(result_df_secondary.columns, area_ALL*area_WFL/(area_IND+area_WFL), bottom=area_ALL*area_IND/(area_IND+area_WFL), color='#d48f57', width=0.5)
        # plt.bar(result_df_secondary.columns, area_ALL, facecolor="None", edgecolor='k', width=0.5)
        # x and y limits
        # plt.xlim(-0.6, 10.5)
        # plt.ylim(-1600, 2000)
        plt.ylabel(ylabel, fontsize=14)
        # remove spines
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['top'].set_visible(False)
        # ax.spines['bottom'].set_visible(False)
        # grid
        ax.set_axisbelow(True)
        ax.yaxis.grid(color='gray', linestyle='dashed', alpha=0.7)
        # x ticks
        xticks_labels = ['S1 Secondary forest\nHarvest + Regrowth', 'S2 Secondary forest\nHarvest + Conversion', 'S3 Secondary forest\nMixed harvest', 'S4 New\nTropical plantations', 'S5 Higher\nPlantation productivity', 'S6 50% less 2050\nWood fuel demand']
        plt.xticks(result_df_secondary.columns, labels=xticks_labels)
        # bar labels
        for number, rec in enumerate(ax.patches[:12]):
            height = rec.get_height()
            # This is to make sure the turn of the group of scenario
            # bar_scenario_group = number%6
            ax.text(rec.get_x() + rec.get_width() / 2, rec.get_y() + height / 2,
                    "{:.1f}".format(height),
                      ha='center', va='bottom')
        # Add the final absolute numbers at the top
        for number, rec in enumerate(ax.patches[:6]):
            # This is to make sure the turn of the group of scenario
            ax.text(rec.get_x() + rec.get_width() / 2, rec.get_y() + area_ALL[number],
                    "{:.0f}".format(area_ALL[number]),
                      ha='center', va='bottom', fontweight='bold')

        # title and legend
        legend_label = ['Industrial roundwood', 'Wood fuel']
        plt.legend(legend_label, ncol=2, bbox_to_anchor=([1, 1.15, 0, 0]), frameon=False, fontsize=14)

        # sort both labels and handles by labels
        plt.subplots_adjust(top=0.83)
        plt.title('{}\n'.format(title), loc='left', fontsize=16, y=1.08)
        # plt.savefig('{}/land_requirement_IND_WFL_6scenarios.png'.format(figdir))
        plt.show()

        return


    carbon_df = read_dataframe('CO2 (Gt per yr) DR_{}'.format(discount_filename))
    stacked_barplot_attribute_demand_substitution_carbon(carbon_df, 'Carbon costs', 'GtCO2/year')
    land_df = read_dataframe('Land (Mha) DR_{}'.format(discount_filename))
    stacked_barplot_attribute_demand_substitution_land(land_df, 'Land requirements 2010-2050', 'Mha')

    return

# barplot_all_scenarios_quantity()