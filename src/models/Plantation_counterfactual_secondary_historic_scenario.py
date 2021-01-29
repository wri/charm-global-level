#!/usr/bin/env python
__author__ = "Liqing Peng, Jessica Zionts, Tim Searchinger"
__copyright__ = "Copyright (C) 2020 WRI, The Carbon Harvest Model (CHarM) Project"
__maintainer__ = "Liqing Peng"
__email__ = "liqing.peng@wri.org"
"""
Plantation counterfactual secondary historic scenario
1. Aboveground biomass before the first harvest is C density right before the second harvest
2. Counterfactual starts from Nancy’s carbon density and grow back at the old secondary growth rate
3. Harvest with potential thinnings
"""

import numpy as np
import matplotlib.pyplot as plt


class CarbonTracker:

    def __init__(self, Global, year_start_for_PDV=0):
        # To set up when to start calculating total PDV in one year.
        # For example, if it is year 2010 year = 0, then the total PDV in year 0 will be sum of the entire 40 years period until 2050. If it is year 2020, year = 10, the calculator will still be run for the 40 years. But the total PDV in year 10 will be sum of the only first 30 years (40-10), the 31-40 years will be valid for the total PDV in year 2051-2060, which is not relevant.
        # This will be used to select the product share ratio, as well. For example, if it is year 2020 year = 10, then the product share will be obtained from 10 years from the 2010.
        self.Global = Global
        self.year_start_for_PDV = year_start_for_PDV  # the starting year of the carbon calculator
        self.product_share_LLP_plantation, self.product_share_SLP_plantation, self.product_share_VSLP_plantation = [np.zeros((self.Global.nyears)) for _ in range(3)]

        self.product_share_LLP_plantation[:(self.Global.nyears - year_start_for_PDV)] = self.Global.product_share_LLP[year_start_for_PDV:] * (1 - self.Global.slash_percentage_plantation[(year_start_for_PDV+1):])
        self.product_share_SLP_plantation[:(self.Global.nyears - year_start_for_PDV)] = self.Global.product_share_SLP[year_start_for_PDV:] * (1 - self.Global.slash_percentage_plantation[(year_start_for_PDV+1):])
        self.product_share_VSLP_plantation[:(self.Global.nyears - year_start_for_PDV)] = self.Global.product_share_VSLP[year_start_for_PDV:] * (1 - self.Global.slash_percentage_plantation[(year_start_for_PDV+1):])


        ##### Initialize carbon flow variables
        ### Biomass pool: Aboveground biomass leftover + belowground/roots
        self.aboveground_biomass_secondary_maximum = self.Global.C_harvest_density_secondary * 2.0
        self.aboveground_biomass_plantation, self.belowground_biomass_decay_plantation, self.belowground_biomass_live_plantation = [
            np.zeros((self.Global.ncycles_harvest, self.Global.arraylength)) for _ in range(3)]
        ### Product pool: VSLP/SLP/LLP
        self.product_LLP_pool_plantation, self.product_SLP_pool_plantation, self.product_VSLP_pool_plantation = [np.zeros((self.Global.ncycles_harvest, self.Global.arraylength)) for _ in range(3)]
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


    def initialization(self):
        self.aboveground_biomass_plantation[0, 0] = self.calculate_aboveground_biomass_initial_plantation()
        self.belowground_biomass_live_plantation[0, 0] = self.aboveground_biomass_plantation[0, 0] * self.Global.ratio_root_shoot
        # Set to Nancy's secondary initial carbon density
        self.counterfactual_biomass[1] = self.Global.C_harvest_density_secondary


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
            self.belowground_biomass_live_plantation[cycle, year_harvest_thinning] = aboveground_biomass_before_harvest * (1 - self.Global.harvest_percentage_plantation[year_harvest_thinning]) * self.Global.ratio_root_shoot
            self.belowground_biomass_decay_plantation[cycle, year_harvest_thinning] = aboveground_biomass_before_harvest * self.Global.harvest_percentage_plantation[year_harvest_thinning] * self.Global.ratio_root_shoot


            # If this cycle is the harvest or thinning
            # year_harvest_thinning - 1 for product share due to different array length
            if self.Global.year_index_both_plantation[cycle] in self.Global.year_index_harvest_plantation:
                self.product_LLP_pool_plantation[cycle, year_harvest_thinning] = aboveground_biomass_before_harvest * self.Global.harvest_percentage_plantation[year_harvest_thinning] * self.product_share_LLP_plantation[year_harvest_thinning - 1]
                self.product_SLP_pool_plantation[cycle, year_harvest_thinning] = aboveground_biomass_before_harvest * self.Global.harvest_percentage_plantation[year_harvest_thinning] * self.product_share_SLP_plantation[year_harvest_thinning - 1]
                self.product_VSLP_pool_plantation[cycle, year_harvest_thinning] = aboveground_biomass_before_harvest * self.Global.harvest_percentage_plantation[year_harvest_thinning] * self.product_share_VSLP_plantation[year_harvest_thinning - 1]
                self.slash_pool_plantation[cycle, year_harvest_thinning] = aboveground_biomass_before_harvest * self.Global.harvest_percentage_plantation[year_harvest_thinning] * self.Global.slash_percentage_plantation[year_harvest_thinning]

            else:
                self.product_LLP_pool_plantation[cycle, year_harvest_thinning] = aboveground_biomass_before_harvest * self.Global.harvest_percentage_plantation[year_harvest_thinning] * self.Global.product_share_LLP_thinning
                self.product_SLP_pool_plantation[cycle, year_harvest_thinning] = aboveground_biomass_before_harvest * self.Global.harvest_percentage_plantation[year_harvest_thinning] * self.Global.product_share_SLP_thinning
                self.product_VSLP_pool_plantation[cycle, year_harvest_thinning] = aboveground_biomass_before_harvest * self.Global.harvest_percentage_plantation[year_harvest_thinning] * self.Global.product_share_VSLP_thinning
                self.slash_pool_plantation[cycle, year_harvest_thinning] = aboveground_biomass_before_harvest * self.Global.harvest_percentage_plantation[year_harvest_thinning] * self.Global.slash_percentage_plantation[year_harvest_thinning]

            # ### Stand pool grows back within the rotation cycle
            for year in range(st_cycle, ed_cycle):
                # FIXME grows at young growth rate for 20 years after the harvest
                year_after_all_harvests = year - self.Global.year_index_harvest_plantation
                year_after_current_harvest = np.min(year_after_all_harvests[year_after_all_harvests > 0])
                if year_after_current_harvest <= 20:
                    self.aboveground_biomass_plantation[cycle, year] = self.aboveground_biomass_plantation[cycle, year - 1] + self.Global.GR_young_plantation
                else:
                    self.aboveground_biomass_plantation[cycle, year] = self.aboveground_biomass_plantation[cycle, year - 1] + self.Global.GR_old_plantation

                self.belowground_biomass_live_plantation[cycle, year] = self.aboveground_biomass_plantation[cycle, year] * self.Global.ratio_root_shoot

            ### For each product pool, slash pool, roots leftover, landfill, the carbon decay for the entire self.Global.arraylength
            for year in range(st_cycle, self.Global.arraylength):
                ### Product pool
                self.product_LLP_pool_plantation[cycle, year] = self.product_LLP_pool_plantation[cycle, year_harvest_thinning] * np.exp(- np.log(2) / self.Global.half_life_LLP * (year - year_harvest_thinning))
                self.product_SLP_pool_plantation[cycle, year] = self.product_SLP_pool_plantation[cycle, year_harvest_thinning] * np.exp(- np.log(2) / self.Global.half_life_SLP * (year - year_harvest_thinning))
                self.product_VSLP_pool_plantation[cycle, year] = self.product_VSLP_pool_plantation[cycle, year_harvest_thinning] * np.exp(- np.log(2) / self.Global.half_life_VSLP * (year - year_harvest_thinning))
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
        self.totalC_product_VSLP_pool = np.sum(self.product_VSLP_pool_plantation, axis=0)
        self.totalC_product_pool = self.totalC_product_LLP_pool + self.totalC_product_SLP_pool + self.totalC_product_VSLP_pool

        self.totalC_root_decay_pool = np.sum(self.belowground_biomass_decay_plantation, axis=0)
        self.totalC_slash_pool = np.sum(self.slash_pool_plantation, axis=0)
        self.totalC_slash_root = self.totalC_slash_pool + self.totalC_root_decay_pool

        self.totalC_landfill_pool = np.sum(self.landfill_pool_plantation, axis=0)
        self.totalC_methane_emission = np.sum(self.landfill_methane_emission_plantation, axis=0)


        # Account for timber product substitution effect = avoided concrete/steel usage's GHG emission
        self.LLP_substitution_benefit = self.totalC_product_LLP_pool * self.Global.llp_construct_ratio * self.Global.llp_displaced_CS_ratio * self.Global.coef_construt_substitution

        self.total_carbon_benefit = self.totalC_stand_pool + self.totalC_product_pool + self.totalC_root_decay_pool + self.totalC_landfill_pool + self.totalC_slash_pool + self.totalC_methane_emission + self.LLP_substitution_benefit


    def counterfactual(self):
        """
        Counterfactural scenario
        """
        ### Steady growth no-harvest
        self.stand_biomass_secondary_maximum = self.aboveground_biomass_secondary_maximum * (1 + self.Global.ratio_root_shoot)

        # Grows at the old secondary rate
        for year in range(2, self.Global.arraylength):
            self.counterfactual_biomass[year] = self.counterfactual_biomass[year - 1] + self.Global.GR_old_secondary
        self.counterfactual_biomass = self.counterfactual_biomass * (1 + self.Global.ratio_root_shoot)
        self.counterfactual_biomass[self.counterfactual_biomass >= self.stand_biomass_secondary_maximum] = self.stand_biomass_secondary_maximum


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
                ed_cycle = (cycle * self.Global.rotation_length_harvest + self.Global.rotation_length_harvest) * (cycle < len(self.Global.year_index_harvest_plantation) - 1) + self.Global.nyears * (
                                   cycle == len(self.Global.year_index_harvest_plantation) - 1)

                for year in range(st_cycle, ed_cycle):
                    discounted_year[year] = year - st_cycle + 1

        else:
            for year in range(0, self.Global.nyears):
                discounted_year[year] = year

        self.annual_discounted_value = self.benefit_minus_counterfactual_diff / (1 + self.Global.discount_rate) ** discounted_year

        print("year_start_for_PDV:", self.year_start_for_PDV)

    def plot_C_pools_counterfactual_print_PDV(self):

        present_discounted_carbon_fullperiod = np.sum(self.annual_discounted_value)
        print('PDV (tC/ha): ', present_discounted_carbon_fullperiod)

        plt.plot(self.totalC_stand_pool[1:], label='stand')
        plt.plot(self.totalC_product_pool[1:], label='product')
        plt.plot(self.totalC_root_decay_pool[1:], label='decaying root')
        plt.plot(self.totalC_landfill_pool[1:], label='landfill')
        plt.plot(self.totalC_slash_pool[1:], label='slash')
        plt.plot(self.totalC_methane_emission[1:], label='methane emission')
        plt.plot(self.LLP_substitution_benefit[1:], label='substitution')
        plt.plot(self.total_carbon_benefit[1:], label='total carbon benefit')
        plt.plot(self.counterfactual_biomass[1:], label='counterfactual')
        plt.legend(fontsize=20); plt.show(); exit()

        return



