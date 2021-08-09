#!/usr/bin/env python
__author__ = "Liqing Peng, Jessica Zionts, Tim Searchinger"
__copyright__ = "Copyright (C) 2020 WRI, The Carbon Harvest Model (CHarM) Project"
__maintainer__ = "Liqing Peng"
__email__ = "liqing.peng@wri.org"
"""
Plantation counterfactual secondary at the age of plantation scenario
1. Aboveground biomass before the first harvest is C density right before the second harvest
2. Counterfactual:
The initial (starting point) depends on the rotation period, as it is the secondary forest grows for one rotation period. 
Then it continues to grow for another 40 years. 
The growth rate depends on the stand age (0-20, 20-80, 80-120), not related to rotation period. 

3. Harvest with potential thinnings
"""

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
        # FIXME The product share after years beyond 2050 is unknown
        self.product_share_LLP_plantation[:(self.Global.nyears - year_start_for_PDV)] = self.Global.product_share_LLP[year_start_for_PDV:] * (1 - self.Global.slash_percentage_plantation[(year_start_for_PDV+1):])
        self.product_share_SLP_plantation[:(self.Global.nyears - year_start_for_PDV)] = self.Global.product_share_SLP[year_start_for_PDV:] * (1 - self.Global.slash_percentage_plantation[(year_start_for_PDV+1):])
        self.product_share_VSLP_plantation[:(self.Global.nyears - year_start_for_PDV)] = self.Global.product_share_VSLP[year_start_for_PDV:] * (1 - self.Global.slash_percentage_plantation[(year_start_for_PDV+1):])

        def lastyear_padding(product_share_array):
            "This function is to extend the year beyond 2050 using 2050's product share"
            df = pd.DataFrame(product_share_array)
            outarray = df.replace(to_replace=0, method='ffill').values.reshape(product_share_array.shape)
            return outarray

        self.product_share_LLP_plantation, self.product_share_SLP_plantation, self.product_share_VSLP_plantation = [lastyear_padding(product_share) for product_share in (self.product_share_LLP_plantation, self.product_share_SLP_plantation, self.product_share_VSLP_plantation)]

        ##### Set up carbon flow variables
        ### Biomass pool: Aboveground biomass leftover + belowground/roots
        # 2021/06/10: turn off the maximum cap for counterfactual secondary growth
        # self.aboveground_biomass_secondary_maximum = self.Global.C_harvest_density_secondary * 2.0
        self.aboveground_biomass_plantation, self.belowground_biomass_decay_plantation, self.belowground_biomass_live_plantation = [
            np.zeros((self.Global.ncycles_harvest, self.Global.arraylength)) for _ in range(3)]
        ### Product pool: VSLP/SLP/LLP
        # Original, VSLP pool exists.
        # Update: 06/03/21. Now VSLP pool no longer exists, because VSLP disappear when the harvest happens
        self.product_LLP_pool_plantation, self.product_SLP_pool_plantation = [np.zeros((self.Global.ncycles_harvest, self.Global.arraylength)) for _ in range(2)]
        # Update: 06/03/21. Adding LLP harvest and VSLP harvest for substitution benefit calculation.
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

    def calculate_aboveground_biomass_initial_plantation(self):
        "Initial condition for aboveground and belowground live biomass FOR PLANTATION"
        # Initial = end of the first cycle after several thinnings

        ### Define all the harvest, thinning arrays/indices
        # Harvest year index copy
        year_index_harvest_plantation_hypothetical = self.Global.year_index_harvest_plantation.tolist()
        # FIXED: when the rotation length is longer than the time frame, how to calculate the initial value
        if self.Global.nyears < self.Global.rotation_length_harvest:
            year_index_harvest_plantation_hypothetical.append(self.Global.nyears)

        # If thinnings
        if (np.isnan(self.Global.rotation_length_thinning) == False) & (self.Global.rotation_length_thinning > 0):
            # Thinnings year index for the n-1 rotation periods, except for the last not complete one
            year_index_thinning_plantation_hypothetical = []
            for cycle_harvest in range(len(year_index_harvest_plantation_hypothetical) - 1):
                year_index_thinning_plantation_hypothetical.append(np.arange(year_index_harvest_plantation_hypothetical[cycle_harvest], year_index_harvest_plantation_hypothetical[cycle_harvest + 1], self.Global.rotation_length_thinning, dtype=int))
            year_index_thinning_plantation_hypothetical = np.array(year_index_thinning_plantation_hypothetical).flatten().tolist()
            year_index_both_plantation_hypothetical = sorted(list(set(year_index_harvest_plantation_hypothetical) | set(year_index_thinning_plantation_hypothetical)))

        # If no thinnings
        else:
            year_index_thinning_plantation_hypothetical = []
            year_index_both_plantation_hypothetical = year_index_harvest_plantation_hypothetical

        # harvest percentage
        harvest_percentage_plantation = np.zeros((self.Global.arraylength))
        if (np.isnan(self.Global.thinning_percentage_default) == False) & (self.Global.thinning_percentage_default != 0) & (np.isnan(self.Global.rotation_length_thinning) == False) & (self.Global.rotation_length_thinning > 0):
            harvest_percentage_plantation[year_index_thinning_plantation_hypothetical] = self.Global.thinning_percentage_default
            harvest_percentage_plantation[year_index_harvest_plantation_hypothetical] = self.Global.harvest_percentage_default
        else:
            harvest_percentage_plantation[year_index_harvest_plantation_hypothetical] = self.Global.harvest_percentage_default
        # Only look at the first rotation cycle, get the first harvest all the thinnings before the second harvest
        ncycles_first = year_index_both_plantation_hypothetical.index(year_index_harvest_plantation_hypothetical[1])

        ### Initialize and grow the aboveground biomass array
        aboveground_biomass_plantation_pilot = np.zeros((ncycles_first, self.Global.arraylength))

        for cycle in range(0, ncycles_first):
            year_harvest_thinning = year_index_both_plantation_hypothetical[cycle]
            st_cycle = year_index_both_plantation_hypothetical[cycle] + 1
            ed_cycle = year_index_both_plantation_hypothetical[cycle + 1]
            if cycle == 0: # For the first rotation cycle
                aboveground_biomass_before_harvest = 0
            else: # The following cycles
                aboveground_biomass_before_harvest = aboveground_biomass_plantation_pilot[cycle - 1, year_harvest_thinning - 1]

            ### Carbon intensity at the year of harvest
            aboveground_biomass_plantation_pilot[cycle, year_harvest_thinning] = aboveground_biomass_before_harvest * (1 - harvest_percentage_plantation[year_harvest_thinning])
            ### Stand pool grows back within the rotation cycle
            for year in range(st_cycle, ed_cycle):
                # FIXED: grows at young growth rate for 20 years after the harvest
                year_after_all_harvests = year - self.Global.year_index_harvest_plantation
                year_after_current_harvest = np.min(year_after_all_harvests[year_after_all_harvests > 0])
                if year_after_current_harvest <= 20:
                    aboveground_biomass_plantation_pilot[cycle, year] = aboveground_biomass_plantation_pilot[cycle, year - 1] + self.Global.GR_young_plantation
                else:
                    aboveground_biomass_plantation_pilot[cycle, year] = aboveground_biomass_plantation_pilot[cycle, year - 1] + self.Global.GR_old_plantation

        totalC_aboveground_biomass_pool_pilot = np.sum(aboveground_biomass_plantation_pilot, axis=0)

        return totalC_aboveground_biomass_pool_pilot[year_index_harvest_plantation_hypothetical[1]-1]

    def calculate_belowground_biomass(self, aboveground_biomass):
        belowground_biomass = self.Global.root_shoot_coef * aboveground_biomass ** self.Global.root_shoot_power
        return belowground_biomass

    def initialization(self):
        self.aboveground_biomass_plantation[0, 0] = self.calculate_aboveground_biomass_initial_plantation()
        self.belowground_biomass_live_plantation[0, 0] = self.calculate_belowground_biomass(self.aboveground_biomass_plantation[0, 0])  #self.Global.ratio_root_shoot
        # Remove the initialization of counterfactual


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
            self.belowground_biomass_live_plantation[cycle, year_harvest_thinning] = self.calculate_belowground_biomass(aboveground_biomass_before_harvest * (1 - self.Global.harvest_percentage_plantation[year_harvest_thinning]))  #* self.Global.ratio_root_shoot
            self.belowground_biomass_decay_plantation[cycle, year_harvest_thinning] = self.calculate_belowground_biomass(aboveground_biomass_before_harvest * self.Global.harvest_percentage_plantation[year_harvest_thinning])     #* self.Global.ratio_root_shoot


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

            # ### Stand pool grows back within the rotation cycle
            for year in range(st_cycle, ed_cycle):
                # FIXME grows at young growth rate for 20 years after the harvest
                year_after_all_harvests = year - self.Global.year_index_harvest_plantation
                year_after_current_harvest = np.min(year_after_all_harvests[year_after_all_harvests > 0])
                if year_after_current_harvest <= 20:
                    self.aboveground_biomass_plantation[cycle, year] = self.aboveground_biomass_plantation[cycle, year - 1] + self.Global.GR_young_plantation
                else:
                    self.aboveground_biomass_plantation[cycle, year] = self.aboveground_biomass_plantation[cycle, year - 1] + self.Global.GR_old_plantation

                self.belowground_biomass_live_plantation[cycle, year] = self.calculate_belowground_biomass(self.aboveground_biomass_plantation[cycle, year])    # * self.Global.ratio_root_shoot

            ### For each product pool, slash pool, roots leftover, landfill, the carbon decay for the entire self.Global.arraylength
            for year in range(st_cycle, self.Global.arraylength):
                ### Product pool
                self.product_LLP_pool_plantation[cycle, year] = self.product_LLP_pool_plantation[cycle, year_harvest_thinning] * np.exp(- np.log(2) / self.Global.half_life_LLP * (year - year_harvest_thinning))
                self.product_SLP_pool_plantation[cycle, year] = self.product_SLP_pool_plantation[cycle, year_harvest_thinning] * np.exp(- np.log(2) / self.Global.half_life_SLP * (year - year_harvest_thinning))
                # Original version of VSLP product pool uses the exponential decay. Now we need to change it to immediate loss. Just remove the exponential decay
                # Current version 06/02/21: the VSLP product pool does not mean the leftover of VSLP, it means the burnt emission (it should be considered emission pool, not the product pool)
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
        self.totalC_product_LLP_harvest = np.sum(self.product_LLP_harvest_plantation, axis=0)
        self.totalC_product_VSLP_harvest = np.sum(self.product_VSLP_harvest_plantation, axis=0)
        # Exclude VSLP product pool from total product pool
        self.totalC_product_pool = self.totalC_product_LLP_pool + self.totalC_product_SLP_pool  # + self.totalC_product_VSLP_pool

        self.totalC_root_decay_pool = np.sum(self.belowground_biomass_decay_plantation, axis=0)
        self.totalC_slash_pool = np.sum(self.slash_pool_plantation, axis=0)
        self.totalC_slash_root = self.totalC_slash_pool + self.totalC_root_decay_pool

        self.totalC_landfill_pool = np.sum(self.landfill_pool_plantation, axis=0)
        self.totalC_methane_emission = np.sum(self.landfill_methane_emission_plantation, axis=0)

        # Account for timber product substitution effect = avoided concrete/steel usage's GHG emission
        # Correction:
        # llp_construct_ratio is used in two places. One is here for LLP substitution benefit. The other is used for the LLP halflife parameter, prepared externally.
        self.LLP_substitution_benefit = self.totalC_product_LLP_harvest * self.Global.llp_construct_ratio * self.Global.llp_displaced_CS_ratio * self.Global.coef_construt_substitution
        self.VSLP_substitution_benefit = self.totalC_product_VSLP_harvest * self.Global.coef_bioenergy_substitution
        self.total_carbon_benefit = self.totalC_stand_pool + self.totalC_product_pool + self.totalC_root_decay_pool + self.totalC_landfill_pool + self.totalC_slash_pool + self.totalC_methane_emission + self.LLP_substitution_benefit + self.VSLP_substitution_benefit


    def counterfactual(self):
        """
        Counterfactural scenario
        """
        ### Steady growth no-harvest
        ## Remove the old capping system. Old version: before 06/09 2021 Depending on rotation length
        # The time series must have a length longer than 120 to store the full three growing stage, but it can have longer optional > 120 years.
        tstep_max = max(self.Global.rotation_length_harvest + self.Global.nyears, 120+1)
        counterfactual_biomass_start_zero = np.zeros((tstep_max))
        # For three period
        for tstep in range(1, 20):
            counterfactual_biomass_start_zero[tstep] = counterfactual_biomass_start_zero[tstep-1] + self.Global.GR_young_secondary
        for tstep in range(20, 80):
            counterfactual_biomass_start_zero[tstep] = counterfactual_biomass_start_zero[tstep-1] + self.Global.GR_middle_secondary
        for tstep in range(80, tstep_max):
            counterfactual_biomass_start_zero[tstep] = counterfactual_biomass_start_zero[tstep-1] + self.Global.GR_mature_secondary

        counterfactual_biomass_start_zero = counterfactual_biomass_start_zero + self.calculate_belowground_biomass(counterfactual_biomass_start_zero)
        # Update: year 0 = 0, year 1 onwards are cropped from the counterfactual_biomass_start_zero
        self.counterfactual_biomass[1:] = counterfactual_biomass_start_zero[self.Global.rotation_length_harvest:self.Global.rotation_length_harvest+self.Global.nyears]


######################## STEP 5: Present discounted value ##############################

    def calculate_PDV(self):
        # Gap between current scenario and baseline
        benefit_minus_counterfactual = self.total_carbon_benefit[1:] - self.counterfactual_biomass[1:]
        # Keep the initial benefit, and calculate the first-difference in the gap
        benefit_minus_counterfactual = np.insert(benefit_minus_counterfactual, 0, 0)
        self.benefit_minus_counterfactual_diff = np.diff(benefit_minus_counterfactual)

        discounted_year = np.zeros((self.Global.nyears))
        # when the rotation length is short, set to 40 years
        # The emissions for each hectare of harvest in each year need to be the PDV of that harvest in that year.
        # In other words, it should incorporate all the changes in carbon pools, including regrowth, for 40 years and then discount TO THE YEAR OF HARVEST.
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

        # for cycle in range(0, len(self.Global.year_index_harvest_plantation)):
        #     st_cycle = cycle * self.Global.rotation_length_harvest + 1
        #     ed_cycle = (cycle * self.Global.rotation_length_harvest + self.Global.rotation_length_harvest) * (
        #                 cycle < len(self.Global.year_index_harvest_plantation) - 1) + self.Global.nyears * (
        #                            cycle == len(self.Global.year_index_harvest_plantation) - 1)
        #
        #     for year in range(st_cycle, ed_cycle):
        #         discounted_year[year] = year - st_cycle + 1

        self.annual_discounted_value = self.benefit_minus_counterfactual_diff / (1 + self.Global.discount_rate) ** discounted_year

        print("year_start_for_PDV:", self.year_start_for_PDV)

    def plot_C_pools_counterfactual_print_PDV(self):

        present_discounted_carbon_fullperiod = np.sum(self.annual_discounted_value)
        print('PDV (tC/ha): ', present_discounted_carbon_fullperiod)

        plt.plot(self.totalC_stand_pool[1:], label='stand', color='yellowgreen')
        plt.plot(self.totalC_product_pool[1:], label='product', color='b')
        plt.plot(self.totalC_slash_pool[1:], label='slash', color='r')
        plt.plot(self.total_carbon_benefit[1:], label='total carbon benefit', color='k', lw=2)
        plt.plot(self.counterfactual_biomass[1:], label='Non-harvest', color='g', lw=2)
        plt.plot(self.totalC_product_LLP_pool[1:], label='LLP')
        plt.plot(self.totalC_product_SLP_pool[1:], label='SLP')
        plt.plot(self.totalC_root_decay_pool[1:], label='decaying root')
        plt.plot(self.totalC_landfill_pool[1:], label='landfill')
        plt.plot(self.totalC_methane_emission[1:], label='methane emission')
        plt.plot(self.LLP_substitution_benefit[1:], label='LLP substitution', marker='o')
        plt.plot(self.VSLP_substitution_benefit[1:], label='VSLP substitution', marker='^')
        plt.plot(self.annual_discounted_value, label='annual_discounted_value')
        # plt.annotate('PDV: {:.0f} (tC/ha)'.format(present_discounted_carbon_fullperiod), xy=(0.8, 0.88), xycoords='axes fraction', fontsize=14)
        plt.legend(fontsize=16); plt.show(); exit()

        return



