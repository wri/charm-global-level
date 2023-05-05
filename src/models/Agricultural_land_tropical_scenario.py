#!/usr/bin/env python
"""
This is an updated Pasture with counterfactual scenario for the 4th scenario
1. Aboveground biomass in year 0 is 0
2. Counterfactual starting from 0 and grows back
3. First harvest occurs at the end of first rotation, no harvest in year 0.
"""
__author__ = "Liqing Peng"
__copyright__ = "Copyright (C) 2023 World Resources Institute, The Carbon Harvest Model (CHARM) Project"
__credits__ = ["Liqing Peng", "Jessica Zionts", "Tim Searchinger", "Richard Waite"]
__license__ = "MIT"
__date__ = "2022.2"
__maintainer__ = "Liqing Peng"
__email__ = "liqing.peng@wri.org"
__version__ = "1.0"

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class CarbonTracker:

    def __init__(self, Global, year_start_for_PDV=0):
        # To set up when to start calculating total PDV in one year.
        # For example, if it is year 2010 year = 0, then the total PDV in year 0 will be sum of the entire 40 years period until 2050. If it is year 2020, year = 10, the calculator will still be run for the 40 years. But the total PDV in year 10 will be sum of the only first 30 years (40-10), the 31-40 years will be valid for the total PDV in year 2051-2060, which is not relevant.
        # This will be used to select the product share ratio, as well. For example, if it is year 2020 year = 10, then the product share will be obtained from 10 years from the 2010.
        self.Global = Global
        self.year_start_for_PDV = year_start_for_PDV  # the starting year of the carbon calculator

        self.product_share_LLP_plantation, self.product_share_SLP_plantation, self.product_share_VSLP_plantation = [np.zeros((self.Global.nyears)) for _ in range(3)]

        # Very important assumption: assume the years of product share over the years of growth will be the same as 2050
        # The product share after years beyond 2050 is unknown, extend the year beyond 2050 using 2050's product share
        # 2022/02/08 Separate the nyears_product_demand from the years of growth
        # Get the product share by shifting the initial year, depending on the year_start_for_PDV
        self.product_share_LLP_plantation[:(self.Global.nyears - year_start_for_PDV)] = self.Global.product_share_LLP[year_start_for_PDV:]
        self.product_share_SLP_plantation[:(self.Global.nyears - year_start_for_PDV)] = self.Global.product_share_SLP[year_start_for_PDV:]
        self.product_share_VSLP_plantation[:(self.Global.nyears - year_start_for_PDV)] = self.Global.product_share_VSLP[year_start_for_PDV:]
        self.product_share_LLP_plantation, self.product_share_SLP_plantation, self.product_share_VSLP_plantation = [self.staircase(product_share) * (1 - self.Global.slash_percentage_plantation[1:]) for product_share in
            (self.product_share_LLP_plantation, self.product_share_SLP_plantation, self.product_share_VSLP_plantation)]

        ##### Set up carbon flow variables
        ### Biomass pool: Aboveground biomass leftover + belowground/roots
        # self.aboveground_biomass_secondary_maximum = self.Global.C_harvest_density_secondary * 2.0
        self.aboveground_biomass_plantation, self.belowground_biomass_decay_plantation, self.belowground_biomass_live_plantation = [
            np.zeros((self.Global.ncycles_harvest, self.Global.arraylength)) for _ in range(3)]
        ### Product pool: VSLP/SLP/LLP
        self.product_LLP_pool_plantation, self.product_SLP_pool_plantation = [np.zeros((self.Global.ncycles_harvest, self.Global.arraylength)) for _ in range(2)]
        self.product_LLP_harvest_plantation, self.product_VSLP_harvest_plantation = [np.zeros((self.Global.ncycles_harvest, self.Global.arraylength)) for _ in range(2)]

        ### Slash pool
        self.slash_pool_plantation = np.zeros((self.Global.ncycles_harvest, self.Global.arraylength))
        ### Landfill pool
        # End-use of LLP -> landfill cumulative
        self.landfill_cumulative_plantation = np.zeros((self.Global.ncycles_harvest, self.Global.arraylength))
        # Emissions from landfill
        self.landfill_emission_plantation, self.landfill_methane_emission_plantation = [
            np.zeros((self.Global.ncycles_harvest, self.Global.arraylength)) for _ in range(2)]
        # Landfill pool = LLP cumulative after emission (decay)
        self.landfill_pool_plantation = np.zeros((self.Global.ncycles_harvest, self.Global.arraylength))

        ### The counterfactual scenario: biomass growth as a secondary forest
        self.counterfactual_biomass = np.zeros((self.Global.arraylength))

        #################################### Main functions #####################
        self.initialization()
        self.carbon_pool_simulator_per_cycle()
        self.total_carbon_benefit()
        self.counterfactual()
        self.calculate_PDV()

    def staircase(self, array):
        # Piecewise array for aboveground biomass actually harvested/thinned during rotation harvest/thinning
        outarray = np.zeros(array.shape)
        if len(array.shape) == 1:
            df = pd.DataFrame(array)
            outarray = df.replace(to_replace=0, method='ffill').values.reshape(array.shape)
        else:  # array.shape = 2
            for row in range(array.shape[0]):
                df = pd.DataFrame(array[row, :])
                outarray[row, :] = df.replace(to_replace=0, value=None, method='ffill').values.reshape(array.shape[1])
        return outarray

    def calculate_belowground_biomass(self, aboveground_biomass):
        belowground_biomass = self.Global.root_shoot_coef * aboveground_biomass ** self.Global.root_shoot_power
        return belowground_biomass


    def initialization(self):
        self.aboveground_biomass_plantation[0, 0] = 0
        self.belowground_biomass_live_plantation[0, 0] = self.calculate_belowground_biomass(self.aboveground_biomass_plantation[0, 0])
        # Set to zero at the year of harvest, grow from zero if not continue used as plantation
        self.counterfactual_biomass[1] = 0


    def carbon_pool_simulator_per_cycle(self):
        ######################## STEP 2: Carbon tracker ##############################
        """
        SIMULATE CARBON POOLS
        Every harvest cycle: decay
        Later to edd: add SOC, deadwood
        """
        for cycle in range(0, self.Global.ncycles_harvest):
            ### year of harvest / thinning
            year_harvest_thinning = self.Global.year_index_both_plantation[cycle]   # year_harvest = cycle * self.Global.rotation_length_harvest + 1
            ### Start and end year of the cycle. If it is the last cycle, it is cut off to the length of the array.
            st_cycle = year_harvest_thinning + 1
            if cycle < self.Global.ncycles_harvest - 1:
                ed_cycle = self.Global.year_index_both_plantation[cycle + 1]
            else:
                ed_cycle = self.Global.arraylength

            ### The leftover of the aboveground biomass before the year of harvest
            # For the first rotation cycle
            if cycle == 0:
                aboveground_biomass_before_harvest = self.aboveground_biomass_plantation[0, 0]
            # The following cycles
            else:
                aboveground_biomass_before_harvest = self.aboveground_biomass_plantation[cycle - 1, year_harvest_thinning - 1]

            ### Carbon intensity at the year of harvest
            self.aboveground_biomass_plantation[cycle, year_harvest_thinning] = aboveground_biomass_before_harvest * (1 - self.Global.harvest_percentage_plantation[year_harvest_thinning])
            self.belowground_biomass_live_plantation[cycle, year_harvest_thinning] = self.calculate_belowground_biomass(aboveground_biomass_before_harvest * (1 - self.Global.harvest_percentage_plantation[year_harvest_thinning]))
            self.belowground_biomass_decay_plantation[cycle, year_harvest_thinning] = self.calculate_belowground_biomass(aboveground_biomass_before_harvest * self.Global.harvest_percentage_plantation[year_harvest_thinning])


            # If this cycle is the harvest or thinning
            # year_harvest_thinning - 1 for product share due to different array length
            if self.Global.year_index_both_plantation[cycle] in self.Global.year_index_harvest_plantation:
                self.product_LLP_pool_plantation[cycle, year_harvest_thinning] = aboveground_biomass_before_harvest * self.Global.harvest_percentage_plantation[year_harvest_thinning] * self.product_share_LLP_plantation[year_harvest_thinning - 1]
                self.product_SLP_pool_plantation[cycle, year_harvest_thinning] = aboveground_biomass_before_harvest * self.Global.harvest_percentage_plantation[year_harvest_thinning] * self.product_share_SLP_plantation[year_harvest_thinning - 1]
                self.slash_pool_plantation[cycle, year_harvest_thinning] = aboveground_biomass_before_harvest * self.Global.harvest_percentage_plantation[year_harvest_thinning] * self.Global.slash_percentage_plantation[year_harvest_thinning]
                self.product_LLP_harvest_plantation[cycle, year_harvest_thinning] = aboveground_biomass_before_harvest * self.Global.harvest_percentage_plantation[year_harvest_thinning] * self.product_share_LLP_plantation[year_harvest_thinning - 1]
                self.product_VSLP_harvest_plantation[cycle, year_harvest_thinning] = aboveground_biomass_before_harvest * self.Global.harvest_percentage_plantation[year_harvest_thinning] * self.product_share_VSLP_plantation[year_harvest_thinning - 1]

            else:
                self.product_LLP_pool_plantation[cycle, year_harvest_thinning] = aboveground_biomass_before_harvest * self.Global.harvest_percentage_plantation[year_harvest_thinning] * self.Global.product_share_LLP_thinning
                self.product_SLP_pool_plantation[cycle, year_harvest_thinning] = aboveground_biomass_before_harvest * self.Global.harvest_percentage_plantation[year_harvest_thinning] * self.Global.product_share_SLP_thinning
                self.slash_pool_plantation[cycle, year_harvest_thinning] = aboveground_biomass_before_harvest * self.Global.harvest_percentage_plantation[year_harvest_thinning] * self.Global.slash_percentage_plantation[year_harvest_thinning]
                self.product_LLP_harvest_plantation[cycle, year_harvest_thinning] = aboveground_biomass_before_harvest * self.Global.harvest_percentage_plantation[year_harvest_thinning] * self.Global.product_share_LLP_thinning
                self.product_VSLP_harvest_plantation[cycle, year_harvest_thinning] = aboveground_biomass_before_harvest * self.Global.harvest_percentage_plantation[year_harvest_thinning] * self.Global.product_share_VSLP_thinning

            ### Stand pool grows back within the rotation cycle
            for year in range(st_cycle, ed_cycle):
                # FIXME grows at young growth rate for 20 years after the harvest
                year_after_all_harvests = year - self.Global.year_index_harvest_plantation
                year_after_current_harvest = np.min(year_after_all_harvests[year_after_all_harvests > 0])
                if year_after_current_harvest <= 20:
                    self.aboveground_biomass_plantation[cycle, year] = self.aboveground_biomass_plantation[cycle, year - 1] + self.Global.GR_young_plantation
                else:
                    self.aboveground_biomass_plantation[cycle, year] = self.aboveground_biomass_plantation[cycle, year - 1] + self.Global.GR_old_plantation

                self.belowground_biomass_live_plantation[cycle, year] = self.calculate_belowground_biomass(self.aboveground_biomass_plantation[cycle, year])

            ### For each product pool, slash pool, roots leftover, landfill, the carbon decay for the entire self.Global.arraylength
            for year in range(st_cycle, self.Global.arraylength):
                ### Product pool
                self.product_LLP_pool_plantation[cycle, year] = self.product_LLP_pool_plantation[cycle, year_harvest_thinning] * np.exp(- np.log(2) / self.Global.half_life_LLP * (year - year_harvest_thinning))
                self.product_SLP_pool_plantation[cycle, year] = self.product_SLP_pool_plantation[cycle, year_harvest_thinning] * np.exp(- np.log(2) / self.Global.half_life_SLP * (year - year_harvest_thinning))
                # self.product_VSLP_pool_plantation[cycle, year] = self.product_VSLP_pool_plantation[cycle, year_harvest_thinning] * np.exp(- np.log(2) / self.Global.half_life_VSLP * (year - year_harvest_thinning))
                self.slash_pool_plantation[cycle, year] = self.slash_pool_plantation[cycle, year_harvest_thinning] * (1 - self.Global.slash_burn) * np.exp(- np.log(2) / self.Global.half_life_slash * (year - year_harvest_thinning))
                self.belowground_biomass_decay_plantation[cycle, year] = self.belowground_biomass_decay_plantation[cycle, year_harvest_thinning] * np.exp(- np.log(2) / self.Global.half_life_root * (year - year_harvest_thinning))

                ### Landfill pool
                # Landfill cumulative = sum of the LLP product pool yearly difference deltaC: C(yr-1) - C(yr)
                # Landfill pool = cumulative amount in landfill – emissions
                self.landfill_cumulative_plantation[cycle, year] = self.landfill_pool_plantation[cycle, year - 1] + self.product_LLP_pool_plantation[cycle, year - 1] - self.product_LLP_pool_plantation[cycle, year]
                self.landfill_pool_plantation[cycle, year] = self.landfill_cumulative_plantation[cycle, year] * np.exp(-np.log(2) / self.Global.half_life_landfill)
                # Landfill carbon and methane emission, Methane is a stronger GHG, 34 times over CO2
                self.landfill_emission_plantation[cycle, year] = self.landfill_cumulative_plantation[cycle, year] * (1 - np.exp(-np.log(2) / self.Global.half_life_landfill))
                self.landfill_methane_emission_plantation[cycle, year] = - self.landfill_emission_plantation[cycle, year] * self.Global.landfill_methane_ratio * 34 * 12 / 44


    def total_carbon_benefit(self):
        """
        - Carbon pool total
            - Sum up multiple cycles to get the total carbon stock
        - Substitution effect
        """
        self.totalC_aboveground_biomass_pool = np.sum(self.aboveground_biomass_plantation, axis=0)
        self.totalC_root_live_pool = np.sum(self.belowground_biomass_live_plantation, axis=0)
        self.totalC_stand_pool = self.totalC_aboveground_biomass_pool + self.totalC_root_live_pool

        self.totalC_product_LLP_pool = np.sum(self.product_LLP_pool_plantation, axis=0)
        self.totalC_product_SLP_pool = np.sum(self.product_SLP_pool_plantation, axis=0)
        # Change totalC_product_LLP_harvest to totalC_product_LLP_harvest_stock to show the accumulate harvest stock for LLP substitution benefit
        # For purposes of showing the cumulative impact on carbon, the substitution value represents a permanent increased quantity of carbon that stays in the ground – a permanent increase in fossil fuels.
        # We can think of it as transferring some carbon from the original tree permanently into the ground. This is a one time “stock” gain, but it persists. It just does not grow.
        self.product_LLP_harvest_stock_plantation = self.staircase(self.product_LLP_harvest_plantation)
        self.totalC_product_LLP_harvest_stock = np.sum(self.product_LLP_harvest_stock_plantation, axis=0)

        self.product_VSLP_harvest_stock_plantation = self.staircase(self.product_VSLP_harvest_plantation)
        self.totalC_product_VSLP_harvest_stock = np.sum(self.product_VSLP_harvest_stock_plantation, axis=0)
        # Exclude VSLP product pool from total product pool)
        self.totalC_product_pool = self.totalC_product_LLP_pool + self.totalC_product_SLP_pool #+ self.totalC_product_VSLP_pool

        self.totalC_root_decay_pool = np.sum(self.belowground_biomass_decay_plantation, axis=0)
        self.totalC_slash_pool = np.sum(self.slash_pool_plantation, axis=0)
        self.totalC_slash_root = self.totalC_slash_pool + self.totalC_root_decay_pool

        self.totalC_landfill_pool = np.sum(self.landfill_pool_plantation, axis=0)
        self.totalC_methane_emission = np.sum(self.landfill_methane_emission_plantation, axis=0)

        # Account for timber product substitution effect = avoided concrete/steel usage's GHG emission
        self.LLP_substitution_benefit = self.totalC_product_LLP_harvest_stock * self.Global.llp_construct_ratio * self.Global.llp_displaced_CS_ratio * self.Global.coef_construt_substitution
        self.VSLP_substitution_benefit = self.totalC_product_VSLP_harvest_stock * self.Global.coef_bioenergy_substitution
        self.total_carbon_benefit = self.totalC_stand_pool + self.totalC_product_pool + self.totalC_root_decay_pool + self.totalC_landfill_pool + self.totalC_slash_pool + self.totalC_methane_emission + self.LLP_substitution_benefit + self.VSLP_substitution_benefit


    def counterfactual(self):
        """
        Counterfactural scenario
        """
        ### Steady growth no-harvest
        # start zero, grow at growth rate
        # If there is no harvest, the forest restoration becomes secondary forest
        # 2022/01/20 change the secondary counterfactual
        for year in range(2, self.Global.arraylength):
            self.counterfactual_biomass[year] = self.Global.agb_max * (year - 1) / (year - 1 + self.Global.age_50perc)
        self.counterfactual_biomass = self.counterfactual_biomass + self.calculate_belowground_biomass(self.counterfactual_biomass)


######################## STEP 5: Present discounted value ##############################

    def calculate_PDV(self):
        # Gap between current scenario and baseline
        benefit_minus_counterfactual = self.total_carbon_benefit[1:] - self.counterfactual_biomass[1:]
        # Keep the initial benefit, and calculate the first-difference in the gap
        benefit_minus_counterfactual = np.insert(benefit_minus_counterfactual, 0, 0)
        self.benefit_minus_counterfactual_diff = np.diff(benefit_minus_counterfactual)

        discounted_year = np.zeros((self.Global.nyears))
        # when the rotation length is short, set to 40 years
        # The PDV per ha reflect the decision of harvest. For longer rotation, like managed timber land, reset to zero because we treat it as a separate decision.
        if self.Global.rotation_length_harvest > 40:
            for cycle in range(0, len(self.Global.year_index_harvest_plantation)):
                st_cycle = cycle * self.Global.rotation_length_harvest + 1
                ed_cycle = (cycle * self.Global.rotation_length_harvest + self.Global.rotation_length_harvest) * (cycle < len(self.Global.year_index_harvest_plantation) - 1) + self.Global.nyears * (cycle == len(self.Global.year_index_harvest_plantation) - 1)

                for year in range(st_cycle, ed_cycle):
                    discounted_year[year] = year - st_cycle + 1

        else:
            for year in range(0, self.Global.nyears):
                discounted_year[year] = year

        self.annual_discounted_value = self.benefit_minus_counterfactual_diff / (1 + self.Global.discount_rate) ** discounted_year

        print("year_start_for_PDV:", self.year_start_for_PDV)

        return


    def plot_C_pools_counterfactual_print_PDV(self):
        present_discounted_carbon_fullperiod = np.sum(self.annual_discounted_value)
        print('PDV (tC/ha): ', present_discounted_carbon_fullperiod)

        nyears = self.Global.nyears
        df_stack = pd.DataFrame({'Displaced VSLP emissions': self.VSLP_substitution_benefit[1:],
                                 'Displaced concrete & steel emissions': self.LLP_substitution_benefit[1:],
                                 'Live tree stand & root storage': self.totalC_stand_pool[1:],
                                 'Slash & decaying root storage': self.totalC_slash_root[1:],
                                 'Wood products storage': self.totalC_product_pool[1:],
                                 'Landfill storage': self.totalC_landfill_pool[1:],
                                 'Methane emission': self.totalC_methane_emission[1:]
                                 }, index=np.arange(2010, 2010 + nyears))
        df_line = pd.DataFrame({'Non-harvest scenario': self.counterfactual_biomass[1:],
                                'Harvest scenario - total carbon (all pools)': self.total_carbon_benefit[1:]},
                               index=np.arange(2010, 2010 + nyears))

        colornames = ['Brown', 'Darkgrey', 'DarkGreen', 'Sienna', 'Goldenrod', 'Darkorange', 'Steelblue']

        # Positive carbon flux
        fig, ax = plt.subplots(figsize=(11, 5))
        plt.stackplot(df_stack.index, df_stack['Displaced VSLP emissions'],df_stack['Displaced concrete & steel emissions'],
                      df_stack['Live tree stand & root storage'], df_stack['Slash & decaying root storage'],
                      df_stack['Wood products storage'], df_stack['Landfill storage'], labels=df_stack.columns,
                      colors=colornames[:-1])
        # Negative carbon flux
        # plt.stackplot(df_stack.index, df_stack['Methane emission'], labels=['Methane emission'], color=colornames[-1])
        plt.stackplot(df_stack.index, df_stack['Methane emission'], labels=[''], color=colornames[-1])

        # Two lines
        df_line.plot(ax=ax, style=['--', '-'], color=["limegreen", "k"], lw=2.5, legend=False)
        ax.set_ylabel('Carbon storage (tCeq/ha)', fontsize=18)
        ax.set_xlabel('Year', fontsize=18)
        ax.tick_params(axis='both', which='major', labelsize=16)
        ax.annotate('PDV including substitution: {:.1f} tCeq/ha'.format(present_discounted_carbon_fullperiod), xy=(0.05, 0.84),
                    xycoords='axes fraction', fontsize=11, fontweight='bold')

        ax.set_title(self.Global.country_name, fontsize=16)

        handles, labels = ax.get_legend_handles_labels()
        # fig.legend(handles, labels, loc=(0.68, 0.04), fontsize=12)
        fig.legend(handles[:2], labels[:2], loc=(0.62, 0.6), fontsize=11, frameon=False)
        fig.legend(handles[2:], labels[2:], loc=(0.62, 0.2), fontsize=11, title='Subpools in harvest scenario',
                   title_fontsize=11, frameon=False)

        fig.tight_layout()
        fig.subplots_adjust(top=0.82, right=0.6, left=0.1)
        plt.show(); exit()

        return
