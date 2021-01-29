#!/usr/bin/env python
__author__ = "Liqing Peng, Jessica Zionts, Tim Searchinger"
__copyright__ = "Copyright (C) 2020 WRI, The Carbon Harvest Model (CHarM) Project"
__maintainer__ = "Liqing Peng"
__email__ = "liqing.peng@wri.org"
"""
Secondary forest regrowth scenario
1. Aboveground biomass before the first harvest is (20*young secondary GR)+(20*old secondary GR)
2. Counterfactual starting from (20*young secondary GR)+(20*old secondary GR) and growing at the old secondary growth rate
3. Only has the first harvest 
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
        self.product_share_LLP_secondary, self.product_share_SLP_secondary, self.product_share_VSLP_secondary = [np.zeros((self.Global.nyears)) for _ in range(3)]

        self.product_share_LLP_secondary[:(self.Global.nyears - year_start_for_PDV)] = self.Global.product_share_LLP[year_start_for_PDV:] * (1 - self.Global.slash_percentage_secondary_regrowth[(year_start_for_PDV + 1):])
        self.product_share_SLP_secondary[:(self.Global.nyears - year_start_for_PDV)] = self.Global.product_share_SLP[year_start_for_PDV:] * (1 - self.Global.slash_percentage_secondary_regrowth[(year_start_for_PDV + 1):])
        self.product_share_VSLP_secondary[:(self.Global.nyears - year_start_for_PDV)] = self.Global.product_share_VSLP[year_start_for_PDV:] * (1 - self.Global.slash_percentage_secondary_regrowth[(year_start_for_PDV + 1):])

        ##### Initialize carbon flow variables
        ### Biomass pool: Aboveground biomass leftover + belowground/roots
        self.aboveground_biomass_secondary_maximum = self.Global.C_harvest_density_secondary * 2.0 #1.50
        # The reason to have a thinning is to increase the fast growth of the secondary forest
        # 20 years is the IPCC threshold for young forest growth period
        self.aboveground_biomass_oldgrowth_threshold = self.Global.GR_young_secondary * 20
        self.aboveground_biomass_secondary, self.belowground_biomass_decay_secondary, self.belowground_biomass_live_secondary = [
            np.zeros((self.Global.ncycles_regrowth, self.Global.arraylength)) for _ in range(3)]
        ### Product pool: VSLP/SLP/LLP
        self.product_LLP_pool_secondary, self.product_SLP_pool_secondary, self.product_VSLP_pool_secondary = [np.zeros((self.Global.ncycles_regrowth, self.Global.arraylength)) for _ in range(3)]
        ### Slash pool
        self.slash_pool_secondary = np.zeros((self.Global.ncycles_regrowth, self.Global.arraylength))
        ### Landfill pool
        # End-use of LLP -> landfill cumulative
        self.landfill_cumulative_secondary = np.zeros((self.Global.ncycles_regrowth, self.Global.arraylength))
        # Emissions from landfill
        self.landfill_emission_secondary, self.landfill_methane_emission_secondary = [
            np.zeros((self.Global.ncycles_regrowth, self.Global.arraylength)) for _ in range(2)]
        # Landfill pool = LLP cumulative after emission (decay)
        self.landfill_pool_secondary = np.zeros((self.Global.ncycles_regrowth, self.Global.arraylength))

        ### The counterfactual scenario: biomass growth as a secondary forest
        self.counterfactual_biomass = np.zeros((self.Global.arraylength))

        #################################### Main functions #####################
        self.initialization()
        self.carbon_pool_simulator_per_cycle()
        self.total_carbon_benefit()
        self.counterfactual()
        self.calculate_PDV()


    def initialization(self):
        # # Secondary regrowth scenario, initial aboveground biomass is the C density from secondary
        # self.aboveground_biomass_secondary[0, 0] = self.Global.C_harvest_density_secondary
        # 2021/01/28 change the decision initial also to the (20*young secondary GR)+(20*old secondary GR)
        self.aboveground_biomass_secondary[0, 0] = self.Global.GR_young_secondary * 20 + self.Global.GR_old_secondary * 20
        self.belowground_biomass_live_secondary[0, 0] = self.aboveground_biomass_secondary[0, 0] * self.Global.ratio_root_shoot
        # set to the Nancy's average carbon density
        # self.counterfactual_biomass[0] = self.aboveground_biomass_secondary[0, 0]
        # self.counterfactual_biomass[1] = self.aboveground_biomass_secondary[0, 0]
        # 2021/01/26 change the initial to (20*young secondary GR)+(20*old secondary GR)
        self.counterfactual_biomass[1] = self.Global.GR_young_secondary * 20 + self.Global.GR_old_secondary * 20

    def carbon_pool_simulator_per_cycle(self):
        ######################## STEP 2: Carbon tracker ##############################
        """
        SIMULATE CARBON POOLS
        Every harvest cycle: decay
        Later to edd: add SOC, deadwood
        """
        for cycle in range(0, self.Global.ncycles_regrowth):
            ### year of harvest / thinning
            year_harvest_thinning = self.Global.year_index_both_regrowth[cycle]
            ### Start and end year of the cycle. If it is the last cycle, it is cut off to the length of the array.
            st_cycle = year_harvest_thinning + 1
            if cycle < self.Global.ncycles_regrowth - 1:
                ed_cycle = self.Global.year_index_both_regrowth[cycle + 1]
            else:
                ed_cycle = self.Global.arraylength

            ### The leftover of the aboveground biomass before the year of harvest
            # For the first rotation cycle
            if cycle == 0:
                aboveground_biomass_before_harvest = self.aboveground_biomass_secondary[0, 0]
            # The following cycles
            else:
                aboveground_biomass_before_harvest = self.aboveground_biomass_secondary[cycle - 1, year_harvest_thinning - 1]

            ### Carbon intensity at the year of harvest
            self.aboveground_biomass_secondary[cycle, year_harvest_thinning] = aboveground_biomass_before_harvest * (1 - self.Global.harvest_percentage_regrowth[year_harvest_thinning])
            self.belowground_biomass_live_secondary[cycle, year_harvest_thinning] = aboveground_biomass_before_harvest * (1 - self.Global.harvest_percentage_regrowth[year_harvest_thinning]) * self.Global.ratio_root_shoot
            self.belowground_biomass_decay_secondary[cycle, year_harvest_thinning] = aboveground_biomass_before_harvest * self.Global.harvest_percentage_regrowth[year_harvest_thinning] * self.Global.ratio_root_shoot


            # If this cycle is the harvest or thinning
            # year_harvest_thinning - 1 for product share due to different array length
            if self.Global.year_index_both_regrowth[cycle] in self.Global.year_index_harvest_regrowth:
                self.product_LLP_pool_secondary[cycle, year_harvest_thinning] = aboveground_biomass_before_harvest * self.Global.harvest_percentage_regrowth[year_harvest_thinning] * self.product_share_LLP_secondary[year_harvest_thinning - 1]
                self.product_SLP_pool_secondary[cycle, year_harvest_thinning] = aboveground_biomass_before_harvest * self.Global.harvest_percentage_regrowth[year_harvest_thinning] * self.product_share_SLP_secondary[year_harvest_thinning - 1]
                self.product_VSLP_pool_secondary[cycle, year_harvest_thinning] = aboveground_biomass_before_harvest * self.Global.harvest_percentage_regrowth[year_harvest_thinning] * self.product_share_VSLP_secondary[year_harvest_thinning - 1]
                self.slash_pool_secondary[cycle, year_harvest_thinning] = aboveground_biomass_before_harvest * self.Global.harvest_percentage_regrowth[year_harvest_thinning] * self.Global.slash_percentage_secondary_regrowth[year_harvest_thinning]

            else:
                self.product_LLP_pool_secondary[cycle, year_harvest_thinning] = aboveground_biomass_before_harvest * self.Global.harvest_percentage_regrowth[year_harvest_thinning] * self.Global.product_share_LLP_thinning
                self.product_SLP_pool_secondary[cycle, year_harvest_thinning] = aboveground_biomass_before_harvest * self.Global.harvest_percentage_regrowth[year_harvest_thinning] * self.Global.product_share_SLP_thinning
                self.product_VSLP_pool_secondary[cycle, year_harvest_thinning] = aboveground_biomass_before_harvest * self.Global.harvest_percentage_regrowth[year_harvest_thinning] * self.Global.product_share_VSLP_thinning
                self.slash_pool_secondary[cycle, year_harvest_thinning] = aboveground_biomass_before_harvest * self.Global.harvest_percentage_regrowth[year_harvest_thinning] * self.Global.slash_percentage_secondary_regrowth[year_harvest_thinning]


            # ### Stand pool grows back within the rotation cycle
            for year in range(st_cycle, ed_cycle):
                if self.aboveground_biomass_secondary[cycle, year - 1] < self.aboveground_biomass_oldgrowth_threshold:
                    self.aboveground_biomass_secondary[cycle, year] = self.aboveground_biomass_secondary[cycle, year - 1] + self.Global.GR_young_secondary
                else:
                    self.aboveground_biomass_secondary[cycle, year] = self.aboveground_biomass_secondary[cycle, year - 1] + self.Global.GR_old_secondary
                # This creates a same cap as counterfactual for the maximum
                self.aboveground_biomass_secondary[self.aboveground_biomass_secondary > self.aboveground_biomass_secondary_maximum] = self.aboveground_biomass_secondary_maximum
                self.belowground_biomass_live_secondary[cycle, year] = self.aboveground_biomass_secondary[cycle, year] * self.Global.ratio_root_shoot

            ### For each product pool, slash pool, roots leftover, landfill, the carbon decay for the entire self.Global.arraylength
            for year in range(st_cycle, self.Global.arraylength):
                ### Product pool
                self.product_LLP_pool_secondary[cycle, year] = self.product_LLP_pool_secondary[cycle, year_harvest_thinning] * np.exp(- np.log(2) / self.Global.half_life_LLP * (year - year_harvest_thinning))
                self.product_SLP_pool_secondary[cycle, year] = self.product_SLP_pool_secondary[cycle, year_harvest_thinning] * np.exp(- np.log(2) / self.Global.half_life_SLP * (year - year_harvest_thinning))
                self.product_VSLP_pool_secondary[cycle, year] = self.product_VSLP_pool_secondary[cycle, year_harvest_thinning] * np.exp(- np.log(2) / self.Global.half_life_VSLP * (year - year_harvest_thinning))
                self.slash_pool_secondary[cycle, year] = self.slash_pool_secondary[cycle, year_harvest_thinning] * (1 - self.Global.slash_burn) * np.exp(- np.log(2) / self.Global.half_life_slash * (year - year_harvest_thinning))
                self.belowground_biomass_decay_secondary[cycle, year] = self.belowground_biomass_decay_secondary[cycle, year_harvest_thinning] * np.exp(- np.log(2) / self.Global.half_life_root * (year - year_harvest_thinning))

                ### Landfill pool
                # Landfill cumulative = sum of the LLP product pool yearly difference deltaC: C(yr-1) - C(yr)
                # Landfill pool = cumulative amount in landfill – emissions
                self.landfill_cumulative_secondary[cycle, year] = self.landfill_pool_secondary[cycle, year - 1] + self.product_LLP_pool_secondary[cycle, year - 1] - self.product_LLP_pool_secondary[cycle, year]
                self.landfill_pool_secondary[cycle, year] = self.landfill_cumulative_secondary[cycle, year] * np.exp(-np.log(2) / self.Global.half_life_landfill)
                # Landfill carbon and methane emission, Methane is a stronger GHG, 34 times over CO2
                self.landfill_emission_secondary[cycle, year] = self.landfill_cumulative_secondary[cycle, year] * (1 - np.exp(-np.log(2) / self.Global.half_life_landfill))
                self.landfill_methane_emission_secondary[cycle, year] = - self.landfill_emission_secondary[cycle, year] * self.Global.landfill_methane_ratio * 34 * 12 / 44


    def total_carbon_benefit(self):
        """
        - Carbon pool total
            - Sum up multiple cycles to get the total carbon stock
        - Substitution effect
        """
        self.totalC_aboveground_biomass_pool = np.sum(self.aboveground_biomass_secondary, axis=0)
        self.totalC_root_live_pool = np.sum(self.belowground_biomass_live_secondary, axis=0)
        self.totalC_stand_pool = self.totalC_aboveground_biomass_pool + self.totalC_root_live_pool

        self.totalC_product_LLP_pool = np.sum(self.product_LLP_pool_secondary, axis=0)
        self.totalC_product_SLP_pool = np.sum(self.product_SLP_pool_secondary, axis=0)
        self.totalC_product_VSLP_pool = np.sum(self.product_VSLP_pool_secondary, axis=0)
        self.totalC_product_pool = self.totalC_product_LLP_pool + self.totalC_product_SLP_pool + self.totalC_product_VSLP_pool

        self.totalC_root_decay_pool = np.sum(self.belowground_biomass_decay_secondary, axis=0)
        self.totalC_slash_pool = np.sum(self.slash_pool_secondary, axis=0)
        self.totalC_slash_root = self.totalC_slash_pool + self.totalC_root_decay_pool

        self.totalC_landfill_pool = np.sum(self.landfill_pool_secondary, axis=0)
        self.totalC_methane_emission = np.sum(self.landfill_methane_emission_secondary, axis=0)

        # Account for timber product substitution effect = avoided concrete/steel usage's GHG emission
        self.LLP_substitution_benefit = self.totalC_product_LLP_pool * self.Global.llp_construct_ratio * self.Global.llp_displaced_CS_ratio * self.Global.coef_construt_substitution

        self.total_carbon_benefit = self.totalC_stand_pool + self.totalC_product_pool + self.totalC_root_decay_pool + self.totalC_landfill_pool + self.totalC_slash_pool + self.totalC_methane_emission + self.LLP_substitution_benefit


    def counterfactual(self):
        """
        Counterfactural scenario
        """
        ### Steady growth no-harvest
        self.stand_biomass_secondary_maximum = self.aboveground_biomass_secondary_maximum * (1 + self.Global.ratio_root_shoot)
        # start zero, grow at growth rate
        # If there is no harvest, the forest restoration becomes secondary forest
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
                ed_cycle = (cycle * self.Global.rotation_length_harvest + self.Global.rotation_length_harvest) * (cycle < len(self.Global.year_index_harvest_plantation) - 1) + self.Global.nyears * (cycle == len(self.Global.year_index_harvest_plantation) - 1)

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



