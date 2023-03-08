#!/usr/bin/env python
"""
Main calculation original excel file: Churkina_Calculation_Synthesis.xlsx
Timber demand scenarios from Churkina 2020:
10%
50%
90% 
The global new urban timber demand is calculated from the Analysis_Phase4/urban_builtup_timber_demand.py

"""
__author__ = "Liqing Peng"
__copyright__ = "Copyright (C) 2023 World Resources Institute, The Carbon Harvest Model (CHARM) Project"
__credits__ = ["Liqing Peng", "Jessica Zionts", "Tim Searchinger", "Richard Waite"]
__license__ = "MIT"
__version__ = "2021.11.1"
__maintainer__ = "Liqing Peng"
__email__ = "liqing.peng@wri.org"
__status__ = "Dev"

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = "Arial"
matplotlib.rcParams['font.family'] = "sans-serif"

### Datafile
root = '../../'
version = '20230125'
years = '40'
discount_filename = '4p'
sumfile = '{}/data/processed/derivative/CHARM_global_carbon_land_summary - YR_{} - V{}.xlsx'.format(root, years, version)
figdir = '{}/../Paper/Figure'.format(root)


def get_wood_demand_for_construction():
    "Calculate wood demand"
    # Step 1. Build the Churkina numbers for different scenarios
    pop_increase_40yr = 2760704246  # 2050 - 2010 Urban population increass: capita
    # Material intensity of Timber for primary structral system mean (Churkina 2020 SI Table 3): kg/capita
    MI_primary_avg = 5942.50
    # Material intensity of Timber for Enclosure system mean (Churkina 2020 SI Table 4):	kg/capita
    MI_enclosure_avg = 1104.53
    # Material intensity of Wood Fibre for Enclosure system mean (Churkina 2020 SI Table 4)	kg/capita
    MI_fibre_avg = 391.98
    # Total material intensity of Wood in construction mean:	t/capita
    MI_construction_sum = (MI_primary_avg + MI_enclosure_avg + MI_fibre_avg)/1000
    # Conversion factors
    # cf_MegatC_tC = 1000000
    C_wood_ratio = 0.5 # 	tC in wood / tDM wood
    product_roundwood_ratio = 0.5 # t product/t industrial roundwood
    overbark_underbark_ratio = 1.15

    ### Calculate Cumulative carbon in timber demand for wood construction: tC/yr
    wood_in_product = pop_increase_40yr * MI_construction_sum  # t wood product for 40 years
    tree_for_material = wood_in_product / product_roundwood_ratio * overbark_underbark_ratio  # t trees (roundwood + bark)
    carbon_in_trees = tree_for_material * C_wood_ratio  # tC for 40 years
    percentage_wood = [0.1, 0.5, 0.9]
    # wood demand: tC
    carbon_for_wood_construction = [carbon_in_trees * perc for perc in percentage_wood]

    return carbon_for_wood_construction


def get_additional_secondary_wood_CHARM(vslp_input_control_input):
    "CHARM model output"
    # Step 2. Read in the output from the results summary file for secondary wood supply
    wood_lists = ['Default: Secondary forest supply wood (mega tC)',
                                'Agriland: Secondary forest supply wood (mega tC)',
                                '125% GR: Secondary forest supply wood (mega tC)',
                                '62% SL: Secondary forest supply wood (mega tC)',
                                'WFL50less: Secondary forest supply wood (mega tC)']
    wood_df = pd.read_excel(sumfile, sheet_name='Wood supply (mega tC) DR_{}'.format(discount_filename), index_col=0)[wood_lists]
    # Cumulative carbon required from secondary forest (BAU)
    cum_carbon_BAU = wood_df.loc['BAU_SUBON_{}'.format(vslp_input_control_input)]
    # Cumulative carbon required from secondary forest (constant demand)
    cum_carbon_CST = wood_df.loc['CST_SUBON_{}'.format(vslp_input_control_input)]
    # Additional wood due to BAU
    additional_secondary_carbon = cum_carbon_BAU - cum_carbon_CST

    # The 4-6th scenario have a different wood supply, needs the 125% secondary forest supply wood
    additional_secondary_carbon_scenario = [additional_secondary_carbon[0]] * 3 + additional_secondary_carbon[1:].values.tolist()

    return additional_secondary_carbon_scenario

def get_additional_secondary_land_CHARM(vslp_input_control_input):
    "CHARM model output"
    # Step 2. Read in the output from the results summary file for secondary wood supply

    land_df = pd.read_excel(sumfile, sheet_name='Land (Mha) DR_{}'.format(discount_filename), index_col=0).iloc[:, range(7)]
    # Cumulative carbon required from secondary forest (BAU)
    land_BAU = land_df.loc['BAU_SUBON_{}'.format(vslp_input_control_input)]
    # Cumulative carbon required from secondary forest (constant demand)
    land_CST = land_df.loc['CST_SUBON_{}'.format(vslp_input_control_input)]
    # Additional land due to BAU
    additional_secondary_land_scenario = land_BAU - land_CST

    return additional_secondary_land_scenario


def calculate_additional_secondary_area_for_construction(percentage_order):
    # Use the total wood demand for secondary area and secondary wood
    # vslp_input_control_input = 'ALL' # This is wrong
    # Use the industrial roundwood demand for secondary area and secondary wood
    vslp_input_control_input = 'IND'

    carbon_for_wood_construction = get_wood_demand_for_construction()
    additional_secondary_carbon_scenario = get_additional_secondary_wood_CHARM(vslp_input_control_input)
    additional_secondary_land_scenario = get_additional_secondary_land_CHARM(vslp_input_control_input)
    # Step 3. Scale the area with the carbon ratio
    # Read in the output from the results summary file for land area
    additional_secondary_area = carbon_for_wood_construction[percentage_order] / np.array(additional_secondary_carbon_scenario) * np.array(additional_secondary_land_scenario) #land_df.loc['BAU_SUBON_{}'.format(vslp_input_control_input)].values
    # print(carbon_for_wood_construction[percentage_order], additional_secondary_carbon_scenario, additional_secondary_land_scenario, additional_secondary_area)
    return additional_secondary_area

def export_results_to_excel():
    "Copy the land area tab and add in the two rows"
    land_df = pd.read_excel(sumfile, sheet_name='Land (Mha) DR_{}'.format(discount_filename), index_col=0)
    result_df = land_df.iloc[:, range(7)]
    result_df.loc['Existing plantations'] = land_df.loc['BAU_SUBON_IND', 'Existing plantations']
    result_df.loc['New plantations'] = 0
    result_df.loc['New plantations', 'S4 New tropical plantations'] = land_df.loc[
        'BAU_SUBON_IND', 'New plantations']
    select_df = result_df.loc[['BAU_SUBON_ALL', 'CST_SUBON_ALL', 'BAU_SUBON_IND', 'CST_SUBON_IND', 'Existing plantations', 'New plantations']] # SUBON = NOSUB for land
    wood_percentages = ['10% construction using wood', '50% construction using wood', '90% construction using wood']
    for ipercentage, name in enumerate(wood_percentages):
        select_df.loc[name] = calculate_additional_secondary_area_for_construction(ipercentage)

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

    write_excel(sumfile, 'Land construction (Mha) DR_{}'.format(discount_filename), select_df)

    return

# export_results_to_excel()
# exit()


# Plot the land area results
def barplot_all_scenarios():

    def read_dataframe(tabname):
        # Read in the excel file using the first column as the index
        df = pd.read_excel(sumfile, sheet_name=tabname, index_col=0)
        # Prepare data for the BAU vs CST plot
        df.loc['NewDemand_SUBON_ALL'] = df.loc['BAU_SUBON_ALL'] - df.loc['CST_SUBON_ALL']
        df.loc['NewDemand_SUBON_IND'] = df.loc['BAU_SUBON_IND'] - df.loc['CST_SUBON_IND']
        df.loc['50-10 additional'] = df.loc['50% construction using wood'] - df.loc['10% construction using wood']
        return df

    def setup_axis(ax, ylabel='Carbon costs (Gt CO$_2$e yr$^{-1}$)'):
        # x and y limits
        # plt.xlim(-0.6, 10.5)
        # plt.ylim(-1600, 2000)
        plt.ylabel(ylabel, fontsize=12)
        # remove spines
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['top'].set_visible(False)
        # ax.spines['bottom'].set_visible(False)
        plt.axhline(y=0, color='k', lw=1, linestyle='-', label='_nolegend_')  # skip legend
        # grid
        ax.set_axisbelow(True)
        ax.yaxis.grid(color='gray', linestyle='dashed', alpha=0.7)

        return ax

    def setup_xticks(xticks_loc):
        # x ticks
        xticks_labels = ['(1) Secondary\nforest harvest\nand regrowth', '(2) Secondary\nforest harvest\nand conversion',
                         '(3) Secondary\nforest mixed\nharvest',
                         '(4) New tropical\nplantations', '(5) Higher\nplantation\nproductivity',
                         '(6) Higher\nharvest\nefficiency']
        plt.xticks(xticks_loc, labels=xticks_labels)

        return

    def setup_legend_land():
        legend_label = ['Existing plantations', '2010 supply level', 'Additional BAU demand',
                        'New tropical plantations', '10% construction using wood',
                        'Additional 40% construction using wood', 'Secondary forest area: BAU',
                        'Secondary forest area: 50% construction using wood', 'Total secondary forest area converted to plantations']
        plt.legend(legend_label, ncol=2, bbox_to_anchor=([0.92, -0.14, 0, 0]), handlelength=0.7, frameon=False,
                   fontsize=12)
        # sort both labels and handles by labels
        plt.subplots_adjust(top=0.95, left=0.1, right=0.95, bottom=0.3)
        return

    def barplot_land_IND_WFL(result_df):
        "Plot five scenarios, ignore the last scenario, and only use INDustrial roundwood"
        # Land area requirement from additional demand is the secondary area added upon the CST.
        fig, ax = plt.subplots(1, figsize=(9, 6))
        result_df = result_df.iloc[:,:6]
        plt.bar(result_df.columns, result_df.loc['Existing plantations'], color='#7cc096', edgecolor='w', width=0.5,
                hatch='//')
        plt.bar(result_df.columns, result_df.loc['CST_SUBON_IND'], bottom=result_df.loc['Existing plantations'],
                color='#408107', width=0.5)
        plt.bar(result_df.columns, result_df.loc['NewDemand_SUBON_IND'],
                bottom=result_df.loc['Existing plantations'] + result_df.loc['CST_SUBON_IND'], color='#76aa08',
                width=0.5)
        plt.bar(result_df.columns, result_df.loc['New plantations'],
                bottom=result_df.loc['Existing plantations'] + result_df.loc['CST_SUBON_IND'] + result_df.loc[
                    'NewDemand_SUBON_IND'], edgecolor='w', color='#48f2a8', width=0.5, hatch='//')
        plt.bar(result_df.columns, result_df.loc['10% construction using wood'],
                bottom=result_df.loc['Existing plantations'] + result_df.loc['CST_SUBON_IND'] + result_df.loc[
                    'NewDemand_SUBON_IND'] + result_df.loc['New plantations'], color='#f9af41', width=0.5)
        plt.bar(result_df.columns, result_df.loc['50-10 additional'],
                bottom=result_df.loc['Existing plantations'] + result_df.loc['CST_SUBON_IND'] + result_df.loc[
                    'NewDemand_SUBON_IND'] + result_df.loc['New plantations'] + result_df.loc[
                           '10% construction using wood'], color='#b98653', width=0.5)
        plt.bar(result_df.columns, result_df.loc['BAU_SUBON_IND'], bottom=result_df.loc['Existing plantations'], facecolor="None", edgecolor='k', width=0.5)
        plt.bar(result_df.columns, result_df.loc['50% construction using wood'],
                bottom=result_df.loc['Existing plantations'] + result_df.loc['BAU_SUBON_IND'] + result_df.loc[
                    'New plantations'], ls='dashed', facecolor="None", edgecolor='k', width=0.5)
        # FIXME set the conversion area to converted forests
        plt.bar(result_df.columns[1], result_df.loc['BAU_SUBON_ALL'][1],
                bottom=result_df.loc['Existing plantations'][1], facecolor="None", edgecolor='#96CDCD',
                width=0.5, hatch='//')  # paleturquoise3

        # x and y limits
        setup_axis(ax, ylabel='Land use for wood products (2010-50) (Mha)')
        # x ticks
        setup_xticks(result_df.columns)

        # # bar labels
        area_total = result_df.loc['BAU_SUBON_IND'] + result_df.loc['Existing plantations'] + result_df.loc[
            'New plantations'] + result_df.loc['50% construction using wood']
        for number, rec in enumerate(ax.patches[:18]):
            height = rec.get_height()
            # This is to make sure the turn of the group of scenario
            ax.text(rec.get_x() + rec.get_width() / 2, rec.get_y() + height * 0.44,
                    "{:.0f}".format(height),
                    ha='center', va='center')
        # Add the fourth scenario's new tropical plantations percentage
        ax.text(ax.patches[21].get_x() + ax.patches[21].get_width() / 2,
                ax.patches[21].get_y() + ax.patches[21].get_height() * 0.2,
                "{:.0f}".format(ax.patches[21].get_height()),
                ha='center', va='bottom')
        # other two areas
        for number, rec in enumerate(ax.patches[24:36]):
            height = rec.get_height()
            # This is to make sure the turn of the group of scenario
            ax.text(rec.get_x() + rec.get_width() / 2, rec.get_y() + height * 0.4,
                    "{:.0f}".format(height),
                    ha='center', va='center')
        # Add the final absolute numbers at the top
        for number, rec in enumerate(ax.patches[:6]):
            # This is to make sure the turn of the group of scenario
            ax.text(rec.get_x() + rec.get_width() / 2, rec.get_y() + area_total[number],
                    "{:.0f}".format(area_total[number]),
                    ha='center', va='bottom', fontweight='bold')

        # title and legend
        setup_legend_land()

        return

    land_df = read_dataframe('Land construction (Mha) DR_{}'.format(discount_filename))
    barplot_land_IND_WFL(land_df)
    # plt.savefig('{}/land_requirement_IND_quantity_Churkina_6scenarios.png'.format(figdir))
    # plt.savefig('{}/svg/land_requirement_IND_quantity_Churkina_6scenarios.svg'.format(figdir))
    # plt.show()

    return

# barplot_all_scenarios()








