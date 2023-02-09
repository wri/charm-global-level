#!/usr/bin/env python
"""
Plot the barplots for carbon costs and land use
"""
__author__ = "Liqing Peng"
__copyright__ = "Copyright (C) 2020-2021 World Resources Institute, The Carbon Harvest Model (CHARM) Project"
__credits__ = ["Liqing Peng", "Jessica Zionts", "Tim Searchinger", "Richard Waite"]
__license__ = "Polyform Strict License 1.0.0"
__version__ = "2021.11.1"
__maintainer__ = "Liqing Peng"
__email__ = "liqing.peng@wri.org"
__status__ = "Dev"

import pandas as pd
import matplotlib.pyplot as plt


### Directory
root = '../..'
figdir = '{}/../Paper/Figure'.format(root)
discount_filename = '4p'

def barplot_all_scenarios_percentage_old(infile, years_filename):

    def read_dataframe(tabname):
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
        xticks_labels = ['S1 Secondary forest\nHarvest + Regrowth', 'S2 Secondary forest\nHarvest + Conversion',
                         'S3 Secondary forest\nMixed harvest',
                         'S4 New\nTropical plantations', 'S5 Higher\nPlantation productivity',
                         'S6 Higher\nharvest efficiency', 'S7 50% less 2050\nWood fuel demand']

        plt.xticks(result_df.columns, labels=xticks_labels)
        # bar labels
        base = result_df.loc['BAU_NOSUB_ALL']
        for number, rec in enumerate(ax.patches[:21]):
            height = rec.get_height()
            # This is to make sure the turn of the group of scenario
            bar_scenario_group = number%7
            ax.text(rec.get_x() + rec.get_width() / 2, rec.get_y() + height / 2,
                    "{:.0f}%".format(height/base[bar_scenario_group]*100),
                      ha='center', va='bottom')

        for number, rec in enumerate(ax.patches[21:]):
            height = rec.get_height()
            # This is to make sure the turn of the group of scenario
            ax.text(rec.get_x() + rec.get_width() / 2, rec.get_y() + height,
                    "{:.1f}".format(height),
                      ha='center', va='bottom', fontweight='bold')

        # title and legend
        legend_label = ['2010 supply level', 'Additional BAU demand', 'Substitution benefit', 'Net carbon impact']
        plt.legend(legend_label, ncol=4, bbox_to_anchor=([1, 1.05, 0, 0]), frameon=False, fontsize=13)
        plt.title('{}\n'.format(title), loc='left', fontsize=16)
        plt.show()
        # plt.savefig('{}/carbon_cost_annual_percentage_7scenarios_{}.png'.format(figdir, years_filename))

        return

    def stacked_barplot_attribute_demand_substitution_land(result_df, title, ylabel):
        "Plot multiple scenarios"
        # Land area requirement from additional demand is the secondary area added upon the CST.
        result_df_secondary = result_df.iloc[:, range(7)]
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
        xticks_labels = ['S1 Secondary forest\nHarvest + Regrowth', 'S2 Secondary forest\nHarvest + Conversion',
                         'S3 Secondary forest\nMixed harvest',
                         'S4 New\nTropical plantations', 'S5 Higher\nPlantation productivity',
                         'S6 Higher\nharvest efficiency', 'S7 50% less 2050\nWood fuel demand']

        plt.xticks(result_df_secondary.columns, labels=xticks_labels)
        # bar labels
        base = result_df_secondary.loc['BAU_NOSUB_ALL'] + result_df_secondary.loc['Existing plantations'] + result_df_secondary.loc['New plantations']
        for number, rec in enumerate(ax.patches[:21]):
            height = rec.get_height()
            # This is to make sure the turn of the group of scenario
            bar_scenario_group = number%7
            ax.text(rec.get_x() + rec.get_width() / 2, rec.get_y() + height / 2,
                    "{:.0f}%".format(height/base[bar_scenario_group]*100),
                      ha='center', va='bottom')
        # Add the fourth scenario's new tropical plantations percentage
        ax.text(ax.patches[24].get_x() + ax.patches[24].get_width() / 2, ax.patches[24].get_y() + ax.patches[24].get_height()/2,
                "{:.0f}%".format(ax.patches[24].get_height() / base[3] * 100),
                ha='center', va='bottom')
        # Add the final absolute numbers at the top
        area_total = result_df_secondary.loc['Existing plantations'] + result_df_secondary.loc['CST_NOSUB_ALL'] + result_df_secondary.loc['NewDemand_NOSUB_ALL'] + result_df_secondary.loc['New plantations']
        for number, rec in enumerate(ax.patches[:7]):
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
        # plt.savefig('{}/land_requirement_percentage_7scenarios_{}.png'.format(figdir, years_filename))
        plt.show()

        return

    def stacked_barplot_attribute_IND_WFL_carbon(result_df, title, ylabel):
        "Plot multiple scenarios"
        fig, ax = plt.subplots(1, figsize=(14, 8))
        # Convert carbon impact to carbon cost
        result_df[result_df.select_dtypes(include=['number']).columns] *= -1
        # Calculate the area for IND and the area for WFL
        plt.bar(result_df.columns, result_df.loc['BAU_NOSUB_ALL']*result_df.loc['BAU_NOSUB_IND']/(result_df.loc['BAU_NOSUB_IND']+result_df.loc['BAU_NOSUB_WFL']), color='#ab5b1a', width=0.5)
        plt.bar(result_df.columns, result_df.loc['BAU_NOSUB_ALL']*result_df.loc['BAU_NOSUB_WFL']/(result_df.loc['BAU_NOSUB_IND']+result_df.loc['BAU_NOSUB_WFL']), bottom=result_df.loc['BAU_NOSUB_ALL']*result_df.loc['BAU_NOSUB_IND']/(result_df.loc['BAU_NOSUB_IND']+result_df.loc['BAU_NOSUB_WFL']), color='#d48f57', width=0.5)
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
        xticks_labels = ['(1) Secondary forest\nharvest and regrowth', '(2) Secondary forest\nharvest and conversion',
                         '(3) Secondary forest\nmixed harvest',
                         '(4) New\ntropical plantations', '(5) Higher\nplantation productivity',
                         '(6) Higher\nharvest efficiency', '(7) Reduced wood fuel demand']
        plt.xticks(result_df.columns, labels=xticks_labels)
        # bar labels
        base = result_df.loc['BAU_NOSUB_ALL']
        for number, rec in enumerate(ax.patches[:14]):
            height = rec.get_height()
            # This is to make sure the turn of the group of scenario
            bar_scenario_group = number%7
            ax.text(rec.get_x() + rec.get_width() / 2, rec.get_y() + height / 2,
                    "{:.0f}%".format(height/base[bar_scenario_group]*100),
                      ha='center', va='bottom')
        # Add the final absolute numbers at the top
        for number, rec in enumerate(ax.patches[:7]):
            # This is to make sure the turn of the group of scenario
            ax.text(rec.get_x() + rec.get_width() / 2, rec.get_y() + base[number],
                    "{:.1f}".format(base[number]),
                    ha='center', va='bottom', fontweight='bold')
        # title and legend
        legend_label = ['Industrial roundwood', 'Wood fuel', 'Total carbon impact']
        plt.legend(legend_label, ncol=4, bbox_to_anchor=([1, 1.05, 0, 0]), frameon=False, fontsize=13)
        plt.title('{}\n'.format(title), loc='left', fontsize=16)
        # plt.show()
        # plt.savefig('{}/carbon_cost_annual_percentage_IND_WFL_7scenarios_{}.png'.format(figdir, years_filename))
        plt.savefig('{}/svg/carbon_cost_annual_percentage_IND_WFL_7scenarios_{}.svg'.format(figdir, years_filename))

        return

    def stacked_barplot_attribute_IND_WFL_land(result_df, title, ylabel):
        "Plot multiple scenarios"
        result_df_secondary = result_df.iloc[:, range(7)]
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
        xticks_labels = ['S1 Secondary forest\nHarvest + Regrowth', 'S2 Secondary forest\nHarvest + Conversion',
                         'S3 Secondary forest\nMixed harvest',
                         'S4 New\nTropical plantations', 'S5 Higher\nPlantation productivity',
                         'S6 Higher\nharvest efficiency', 'S7 50% less 2050\nWood fuel demand']
        plt.xticks(result_df_secondary.columns, labels=xticks_labels)
        # bar labels
        for number, rec in enumerate(ax.patches[:14]):
            height = rec.get_height()
            # This is to make sure the turn of the group of scenario
            bar_scenario_group = number%7
            ax.text(rec.get_x() + rec.get_width() / 2, rec.get_y() + height / 2,
                    "{:.0f}%".format(height/area_ALL[bar_scenario_group]*100),
                      ha='center', va='bottom')
        # Add the final absolute numbers at the top
        for number, rec in enumerate(ax.patches[:7]):
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
        # plt.savefig('{}/land_requirement_percentage_IND_WFL_7scenarios_{}.png'.format(figdir, years_filename))
        plt.show()

        return


    carbon_df = read_dataframe('CO2 (Gt per yr) DR_{}'.format(discount_filename))
    stacked_barplot_attribute_IND_WFL_carbon(carbon_df, 'Carbon costs', 'GtCO2/year')
    # stacked_barplot_attribute_demand_substitution_carbon(carbon_df, 'Carbon costs', 'GtCO2/year')

    # land_df = read_dataframe('Land (Mha) DR_{}'.format(discount_filename))
    # stacked_barplot_attribute_IND_WFL_land(land_df, 'Land requirements 2010-2050', 'Mha')

    return



def barplot_all_scenarios_quantity_old(infile, years_filename):
    "Use quantity in the report"
    def read_dataframe(tabname):
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
                         'S4 New\nTropical plantations', 'S5 Higher\nPlantation productivity', 'S6 Higher\nharvest efficiency', 'S7 50% less 2050\nWood fuel demand']
        plt.xticks(result_df.columns, labels=xticks_labels)
        # bar labels
        # base = result_df.loc['BAU_NOSUB_ALL']
        for number, rec in enumerate(ax.patches[:21]):
            height = rec.get_height()
            # This is to make sure the turn of the group of scenario
            ax.text(rec.get_x() + rec.get_width() / 2, rec.get_y() + height / 2,
                    "{:.1f}".format(height),
                      ha='center', va='bottom')

        for number, rec in enumerate(ax.patches[21:]):
            height = rec.get_height()
            # This is to make sure the turn of the group of scenario
            ax.text(rec.get_x() + rec.get_width() / 2, rec.get_y() + height,
                    "{:.1f}".format(height),
                      ha='center', va='bottom', fontweight='bold')

        # title and legend
        legend_label = ['2010 supply level', 'Additional BAU demand', 'Substitution benefit', 'Net carbon impact']
        plt.legend(legend_label, ncol=4, bbox_to_anchor=([1, 1.05, 0, 0]), frameon=False, fontsize=13)
        plt.title('{}\n'.format(title), loc='left', fontsize=16)
        # plt.savefig('{}/annual_carbon_cost_7scenarios_{}.png'.format(figdir, years_filename))
        # plt.savefig('{}/svg/annual_carbon_cost_7scenarios_{}.svg'.format(figdir, years_filename))
        plt.show()

        return

    def stacked_barplot_attribute_demand_substitution_land(result_df, title, ylabel):
        "Plot multiple scenarios"
        # Land area requirement from additional demand is the secondary area added upon the CST.
        result_df_secondary = result_df.iloc[:, range(7)]
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
     'S4 New\nTropical plantations', 'S5 Higher\nPlantation productivity', 'S6 Higher\nharvest efficiency', 'S7 50% less 2050\nWood fuel demand']
        plt.xticks(result_df_secondary.columns, labels=xticks_labels)
        # bar labels
        base = result_df_secondary.loc['BAU_NOSUB_ALL'] + result_df_secondary.loc['Existing plantations'] + result_df_secondary.loc['New plantations']
        for number, rec in enumerate(ax.patches[:21]):
            height = rec.get_height()
            # This is to make sure the turn of the group of scenario
            ax.text(rec.get_x() + rec.get_width() / 2, rec.get_y() + height / 2,
                    "{:.0f}".format(height),
                      ha='center', va='bottom')
        # Add the fourth scenario's new tropical plantations percentage
        ax.text(ax.patches[24].get_x() + ax.patches[24].get_width() / 2, ax.patches[24].get_y() + ax.patches[24].get_height()/2,
                "{:.0f}".format(ax.patches[24].get_height()),
                ha='center', va='bottom')
        # Add the final absolute numbers at the top
        area_total = result_df_secondary.loc['Existing plantations'] + result_df_secondary.loc['CST_NOSUB_ALL'] + result_df_secondary.loc['NewDemand_NOSUB_ALL'] + result_df_secondary.loc['New plantations']
        for number, rec in enumerate(ax.patches[:7]):
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
        # plt.savefig('{}/land_requirement_7scenarios_{}.png'.format(figdir, years_filename))
        plt.savefig('{}/svg/land_requirement_7scenarios_{}.svg'.format(figdir, years_filename))
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
    # land_df = read_dataframe('Land (Mha) DR_{}'.format(discount_filename))
    # stacked_barplot_attribute_demand_substitution_land(land_df, 'Land requirements 2010-2050', 'Mha')

    return


def read_dataframe(infile, tabname):
    # Read in the excel file using the first column as the index
    df = pd.read_excel(infile, sheet_name=tabname, index_col=0)
    # Prepare data for the BAU vs CST plot
    df.loc['NewDemand_NOSUB_ALL'] = df.loc['BAU_NOSUB_ALL'] - df.loc['CST_NOSUB_ALL']
    df.loc['BAU_SubEffect_ALL'] = df.loc['BAU_SUBON_ALL'] - df.loc['BAU_NOSUB_ALL']
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
                     '(6) Higher\nharvest\nefficiency', '(7) Reduced\nwood fuel\ndemand']
    plt.xticks(xticks_loc, labels=xticks_labels)
    return

def setup_bar_label(ax):
    for number, rec in enumerate(ax.patches[:21]): # fixme update the hardcoded 21
        height = rec.get_height()
        # This is to make sure the turn of the group of scenario
        ax.text(rec.get_x() + rec.get_width() / 2, rec.get_y() + height / 2,
                "{:.1f}".format(height),
                ha='center', va='bottom')

    for number, rec in enumerate(ax.patches[21:]):
        height = rec.get_height()
        # This is to make sure the turn of the group of scenario
        ax.text(rec.get_x() + rec.get_width() / 2, rec.get_y() + height,
                "{:.1f}".format(height),
                ha='center', va='bottom', fontweight='bold')
    return ax

def setup_legend_carbon():
    # title and legend
    legend_label = ['2010 supply level', 'Additional BAU demand', 'Substitution benefit', 'Net carbon impact']
    plt.legend(legend_label, ncol=2, bbox_to_anchor=([0.8, -0.18, 0, 0]), handlelength=0.7, frameon=False, fontsize=12)
    plt.subplots_adjust(top=0.95, left=0.1, right=0.95, bottom=0.25)

    return

def setup_legend_land():
    # title and legend
    legend_label = ['Existing plantations', '2010 supply level', 'Additional BAU demand', 'New tropical plantations',
                    'Total secondary forest area']
    plt.legend(legend_label, ncol=2, bbox_to_anchor=([1, -0.05, 0, 0]), frameon=False, fontsize=14)
    # sort both labels and handles by labels
    plt.subplots_adjust(bottom=0.20)

    return


def barplot_all_scenarios_quantity():
    "Use quantity in the report"

    def plot_carbon_BAU_CST_SUB(result_df):
        "Plot the total carbon costs"
        fig, ax = plt.subplots(1, figsize=(9, 6))
        result_df[result_df.select_dtypes(include=['number']).columns] *= -1
        plt.bar(result_df.columns, result_df.loc['CST_NOSUB_ALL'], color='#DB4444', width=0.5)
        plt.bar(result_df.columns, result_df.loc['NewDemand_NOSUB_ALL'], bottom=result_df.loc['CST_NOSUB_ALL'], color='#E17979', width=0.5)
        plt.bar(result_df.columns, result_df.loc['BAU_SubEffect_ALL'], color='#337AE3', width=0.5)
        plt.bar(result_df.columns, result_df.loc['BAU_SUBON_ALL'], ls='dashed', facecolor="None", edgecolor='k', width=0.5)

        # set up the axis and grid lines
        ax = setup_axis(ax, 'Carbon costs (Gt CO$_2$e yr$^{-1}$)')
        # set up the xtick labels
        setup_xticks(result_df.columns)
        # set up the bar labels # base = result_df.loc['BAU_NOSUB_ALL']
        ax = setup_bar_label(ax)
        # set up the legend
        setup_legend_carbon()

        return ax

    def stacked_barplot_attribute_demand_substitution_land(result_df, ylabel):
        "Plot multiple scenarios"
        # Land area requirement from additional demand is the secondary area added upon the CST.
        result_df_secondary = result_df.iloc[:, range(7)]
        result_df_secondary.loc['Existing plantations'] = result_df.loc['BAU_SUBON_ALL', 'Existing plantations']
        result_df_secondary.loc['New plantations'] = 0
        result_df_secondary.loc['New plantations', 'S4 New tropical plantations'] = result_df.loc['BAU_SUBON_ALL', 'New plantations']

        fig, ax = plt.subplots(1, figsize=(14, 8))
        plt.bar(result_df_secondary.columns, result_df_secondary.loc['Existing plantations'], color='#7cc096', edgecolor='w', width=0.5, hatch='//')
        plt.bar(result_df_secondary.columns, result_df_secondary.loc['CST_NOSUB_ALL'], bottom=result_df_secondary.loc['Existing plantations'], color='#408107', width=0.5)
        plt.bar(result_df_secondary.columns, result_df_secondary.loc['NewDemand_NOSUB_ALL'], bottom=result_df_secondary.loc['Existing plantations']+result_df_secondary.loc['CST_NOSUB_ALL'], color='#76aa08', width=0.5)
        plt.bar(result_df_secondary.columns, result_df_secondary.loc['New plantations'], bottom=result_df_secondary.loc['Existing plantations']+result_df_secondary.loc['CST_NOSUB_ALL']+result_df_secondary.loc['NewDemand_NOSUB_ALL'], edgecolor='w', color='#48f2a8', width=0.5, hatch='//')
        plt.bar(result_df_secondary.columns, result_df_secondary.loc['BAU_SUBON_ALL'], bottom=result_df_secondary.loc['Existing plantations'], facecolor="None", edgecolor='k', width=0.5)

        setup_axis(ax, ylabel)
        setup_xticks(result_df_secondary.columns)

        # bar labels
        base = result_df_secondary.loc['BAU_NOSUB_ALL'] + result_df_secondary.loc['Existing plantations'] + result_df_secondary.loc['New plantations']
        for number, rec in enumerate(ax.patches[:21]):
            height = rec.get_height()
            # This is to make sure the turn of the group of scenario
            ax.text(rec.get_x() + rec.get_width() / 2, rec.get_y() + height / 2,
                    "{:.0f}".format(height),
                      ha='center', va='bottom')
        # Add the fourth scenario's new tropical plantations percentage
        ax.text(ax.patches[24].get_x() + ax.patches[24].get_width() / 2, ax.patches[24].get_y() + ax.patches[24].get_height()/2,
                "{:.0f}".format(ax.patches[24].get_height()),
                ha='center', va='bottom')
        # Add the final absolute numbers at the top
        area_total = result_df_secondary.loc['Existing plantations'] + result_df_secondary.loc['CST_NOSUB_ALL'] + result_df_secondary.loc['NewDemand_NOSUB_ALL'] + result_df_secondary.loc['New plantations']
        for number, rec in enumerate(ax.patches[:7]):
            # This is to make sure the turn of the group of scenario
            ax.text(rec.get_x() + rec.get_width() / 2, rec.get_y() + area_total[number],
                    "{:.0f}".format(area_total[number]),
                      ha='center', va='bottom', fontweight='bold')


        setup_legend_land()

        # plt.savefig('{}/land_requirement_7scenarios_{}.png'.format(figdir, years_filename))
        plt.savefig('{}/svg/land_requirement_7scenarios_{}.svg'.format(figdir, years_filename))
        # plt.show()

        return


    carbon_df = read_dataframe(infile, 'CO2 (Gt per yr) DR_{}'.format(discount_filename))
    ax = plot_carbon_BAU_CST_SUB(carbon_df)
    plt.show()
    # plt.savefig('{}/annual_carbon_cost_7scenarios_{}.png'.format(figdir, years_filename))
    # plt.savefig('{}/svg/annual_carbon_cost_7scenarios_{}.svg'.format(figdir, years_filename))

    # land_df = read_dataframe('Land (Mha) DR_{}'.format(discount_filename))
    # stacked_barplot_attribute_demand_substitution_land(land_df, 'Land requirements 2010-2050', 'Mha')

    return


years, years_filename = 40, '40yr'
# years, years_filename = 100, '100yr'
version = '20230125'
infile = '{}/data/processed/derivative/CHARM_global_carbon_land_summary - YR_{} - V{}.xlsx'.format(root, years, version)

barplot_all_scenarios_quantity()
# barplot_all_scenarios_percentage(infile, years_filename)
