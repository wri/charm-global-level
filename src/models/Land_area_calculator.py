#!/usr/bin/env python
"""
Land area calculator
Scale up one-hectare carbon calculation to national level
Produce the area required from plantation, secondary forest by year
# Parameters:
# VSLP initial and final
# SLP initial and final
# LLP initial and final
# Area of plantation

Update
2021/07/01:
    - change the slash rate array into a 41x41 year-to-year array, so that one can read in the yearly slash rate.
"""
__author__ = "Liqing Peng"
__copyright__ = "Copyright (C) 2023 World Resources Institute, The Carbon Harvest Model (CHARM) Project"
__credits__ = ["Liqing Peng", "Jessica Zionts", "Tim Searchinger", "Richard Waite"]
__license__ = "MIT"
__date__ = "2022.11"
__maintainer__ = "Liqing Peng"
__email__ = "liqing.peng@wri.org"
__version__ = "1.0"

import numpy as np
import pandas as pd
import Secondary_conversion_scenario, Secondary_regrowth_scenario, Secondary_mature_regrowth_scenario, Agricultural_land_tropical_scenario
import Plantation_counterfactual_secondary_plantation_age_scenario


class LandCalculator:

    def __init__(self, Global):
        # set up the country profile
        # this is for 40 years
        self.Global = Global

        # calculate output per ha.
        # Use the first year of PDV (default), as it does not matter which year it starts, all the biomass after full harvest is the same.
        # output per ha for plantation
        self.output_ha_plantation = self.calculate_output_ha(Plantation_counterfactual_secondary_plantation_age_scenario.CarbonTracker(self.Global, year_start_for_PDV=0), self.Global.slash_percentage_plantation)

        # output per ha for secondary
        self.output_ha_secondary_conversion = self.calculate_output_ha(Secondary_conversion_scenario.CarbonTracker(self.Global, year_start_for_PDV=0),
            self.Global.slash_percentage_secondary_conversion)
        self.output_ha_secondary_regrowth = self.calculate_output_ha(Secondary_regrowth_scenario.CarbonTracker(self.Global, year_start_for_PDV=0),
            self.Global.slash_percentage_secondary_regrowth)
        # Add new scenario for mature secondary forest regrowth (>120 years)
        self.output_ha_secondary_mature_regrowth = self.calculate_output_ha(Secondary_mature_regrowth_scenario.CarbonTracker(self.Global, year_start_for_PDV=0),
            self.Global.slash_percentage_secondary_regrowth)

        # Add new scenario for tropical agricultural land converted to plantation
        self.output_ha_agriland = self.calculate_output_ha(Agricultural_land_tropical_scenario.CarbonTracker(self.Global, year_start_for_PDV=0),
            self.Global.slash_percentage_plantation)


        ### For plantation scenario, calculate plantation area
        self.calculate_plantation_area()
        # calculate thinning amount from the plantation
        self.calculate_thinning_amount_plantation()

        ### Area required in secondary conversion scenario
        self.area_harvested_new_secondary_conversion, self.wood_harvest_accumulate_secondary_conversion = self.calculate_new_area_secondary_conversion(self.output_ha_secondary_conversion)
        ### Area required in secondary regrowth scenario
        self.area_harvested_new_secondary_regrowth, self.wood_harvest_accumulate_secondary_regrowth = self.calculate_new_area_secondary_regrowth(self.output_ha_secondary_regrowth)
        ### Area required in secondary mature regrowth scenario
        self.area_harvested_new_secondary_mature_regrowth, self.wood_harvest_accumulate_secondary_mature_regrowth = self.calculate_new_area_secondary_mature_regrowth(self.output_ha_secondary_mature_regrowth)
        # Add secondary regrowth and secondary mature regrowth together
        self.area_harvested_new_secondary_regrowth_combined = self.area_harvested_new_secondary_regrowth + self.area_harvested_new_secondary_mature_regrowth


    ####################################################### OUTPUT per ha ###########################################################

    def calculate_output_ha(self, modelrun_scenario, product_share_slash):
        """
        Calculate the per ha output of using the maximum harvest biomass (after several thinnings) from carbon tracker
        """
        # Obtain the secondary forest aboveground biomass from
        aboveground_biomass = modelrun_scenario.totalC_aboveground_biomass_pool
        # First difference, negative diff = harvest, * (-1), positive diff = harvest
        aboveground_biomass_diff = np.diff(aboveground_biomass) * (-1)
        # Only keep the positives = harvest/thinning records
        aboveground_biomass_diff[aboveground_biomass_diff < 0] = 0

        def exclude_slash_staircase():
            # This is copied from the Global meta file
            # Piecewise array for aboveground biomass actually harvested/thinned during rotation harvest/thinning
            if len(product_share_slash.shape) == 1:
                # Get the output = production by removing the slash share (depending whether it is a harvest/thinning)
                output_ha = aboveground_biomass_diff * (1 - product_share_slash[1:])
                df = pd.DataFrame(output_ha)
                output_ha_outarray = df.replace(to_replace=0, method='ffill').values.reshape(output_ha.shape)
            else: # array.shape = 2
                # FIXME change the slash rate to a 42x41 matrix to store different start year 40 year cycle
                output_ha = aboveground_biomass_diff[None, :] * (1 - product_share_slash[:, 1:])  # [None:, ] means a new axis
                output_ha_outarray = np.zeros(output_ha.shape)
                for row in range(output_ha.shape[0]):
                    df = pd.DataFrame(output_ha[row, :])
                    output_ha_outarray[row, :] = df.replace(to_replace=0, value=None, method='ffill').values.reshape(output_ha.shape[1])
            return output_ha_outarray

        output_ha_staircase = exclude_slash_staircase()

        return output_ha_staircase


    def calculate_output_ha_thinning(self, modelrun_scenario, product_share_slash):
        """
        Calculate the per ha output of several thinnings from carbon tracker
        """
        # Obtain the secondary forest aboveground biomass from
        aboveground_biomass = modelrun_scenario.totalC_aboveground_biomass_pool
        # First difference, negative diff = harvest, * (-1), positive diff = harvest
        aboveground_biomass_diff = np.diff(aboveground_biomass) * (-1)
        # Only keep the positives = harvest/thinning records
        aboveground_biomass_diff[aboveground_biomass_diff < 0] = 0

        ### Remove the harvest amount and maintain thinning amount
        aboveground_biomass_diff_thinning = np.zeros((aboveground_biomass_diff.shape))
        # Get only thinning location
        year_index_thinning = sorted(
            set(self.Global.year_index_thinning_plantation) - set(self.Global.year_index_harvest_plantation))
        # Shift left one index to match with aboveground biomass diff
        year_index_thinning = [x - 1 for x in year_index_thinning]
        aboveground_biomass_diff_thinning[year_index_thinning] = aboveground_biomass_diff[year_index_thinning]

        # Get the output = production by removing the slash share (depending whether it is a harvest/thinning)
        output_ha_thinning = aboveground_biomass_diff_thinning * (1 - product_share_slash[1:])
        # Piecewise array for aboveground biomass actually harvested/thinned during rotation harvest/thinning
        output_ha_thinning = pd.DataFrame(output_ha_thinning)
        output_ha_thinning = output_ha_thinning.replace(to_replace=0, method='ffill').values.reshape(self.Global.nyears)

        return output_ha_thinning


    ####################################################### Land area ###########################################################

    def calculate_plantation_area(self):
        """
        Calculate physical plantation area
        FUTURE FIXME: For plantation scenario, when area_harvest_plantation does not reach the cap/maximum, there is no area_harvest_new_secondary needed. Then in this case, the amount of thinning from the plantation should be used to determine the area_harvest_plantation.
        """
        "Step 1. Calculate the maximum output of plantations (limited by actual physical area)"
        self.product_total_carbon = self.Global.product_total * self.Global.carbon_wood_ratio
        # Annual maximum area harvested: FAO national physical area in the plantation and harvest rotation period
        # Harvest is spread out for all the hectares during the entire rotation period.
        # For example, if it is 100 years, then the ratio of area being harvest in one year is 1/100 = 1%. If it is 10 years, the harvest percentage is 1/10=10%. If there is 1000 ha, then annual area harvested is 1000/10 = 100 ha per year
        area_harvested_plantation_maximum = self.Global.physical_area_plantation / self.Global.rotation_length_harvest
        # Annual total maximum output from the harvest = output per ha at the initial * annual area harvested
        total_output_plantation_maximum = area_harvested_plantation_maximum * self.output_ha_plantation[0]

        "Step 2. Calculate the area harvested required to meet the total supply"
        # Area harvested in the plantation = total production need to supply divided by output per ha
        self.area_harvested_plantation = self.product_total_carbon / self.output_ha_plantation[0]


        # Check if the demand in Year is greater than or less than the maximum plantation output
        # If it’s greater than max output, plantation hectares harvested is equal to the maximum
        # If it’s less than the maximum output, hectares harvested = total wood products / output per hectare
        self.area_harvested_plantation[self.product_total_carbon > total_output_plantation_maximum] = area_harvested_plantation_maximum

        "Step 3. Calculate residue wood supply that deduct from the plantation harvest output"
        self.output_need_secondary = self.product_total_carbon - total_output_plantation_maximum

        # If plantations meet the supply in Year, then zero secondary hectares are harvested
        self.output_need_secondary[self.output_need_secondary < 0] = 0


    def calculate_thinning_amount_plantation(self):
        """
        Calculate the total wood harvest from previous harvest/thinnings
        """

        self.wood_thinning_accumulate_plantation = np.zeros((self.Global.nyears))

        if self.Global.year_index_thinning_plantation:
            # Find the years that only have thinnings
            year_index_thinning = sorted(
                set(self.Global.year_index_thinning_plantation) - set(self.Global.year_index_harvest_plantation))
            # Add the last year to calculate the duration
            year_index_thinning.insert(len(year_index_thinning), self.Global.nyears)
            # Add the first year to calculate the duration of first cycle
            year_index_thinning.insert(0, 1)

            # Get the period lengths for all cycles
            cycle_lengths = np.diff(year_index_thinning)
            ncycles_thinning = len(cycle_lengths)
            # print(year_index_thinning, cycle_lengths)

            # Get the output per ha
            output_ha_plantation_thinning = self.calculate_output_ha_thinning(
                Plantation_counterfactual_secondary_plantation_age_scenario.CarbonTracker(self.Global, year_start_for_PDV=0),
                self.Global.slash_percentage_plantation)

            for current_cycle in range(0, ncycles_thinning):
                ### st year and end year of each period, shift -1 to remove the first initial condition
                st_cycle = year_index_thinning[current_cycle] - 1
                if current_cycle < ncycles_thinning - 1:
                    ed_cycle = year_index_thinning[current_cycle + 1] - 1
                else:
                    ed_cycle = self.Global.nyears

                for year in range(st_cycle, ed_cycle):
                    # calculate wood thinning accumulation for one year except for the first cycle Current cycle = 0, no wood accumulation
                    # Current cycle > 0
                    for previous_cycle in range(0, current_cycle):
                        Nyears_Ncycles_before = 0
                        Nyears_Ncycles_ahead = 0
                        for i in range(previous_cycle, current_cycle):
                            Nyears_Ncycles_before = Nyears_Ncycles_before + cycle_lengths[i]
                        for j in range(0, previous_cycle):
                            Nyears_Ncycles_ahead = Nyears_Ncycles_ahead + cycle_lengths[j]
                        # staggered array only for thinning production output
                        self.wood_thinning_accumulate_plantation[year] = self.wood_thinning_accumulate_plantation[year] + \
                                                                    self.area_harvested_plantation[
                                                                        year - Nyears_Ncycles_before] * \
                                                                    output_ha_plantation_thinning[
                                                                        year - Nyears_Ncycles_ahead]


    def calculate_new_area_secondary_conversion(self, output_ha_secondary):
        """
        Calculate the total new area being harvested from the secondary forest converted to plantation
        use year index both for plantation, ncycles_harvest
        """
        # Initialize two variables
        area_harvested_new_secondary = np.zeros((self.Global.nyears))
        wood_harvest_accumulate_secondary = np.zeros((self.Global.nyears))

        year_index_harvest_thinning = self.Global.year_index_both_plantation.copy()
        # Add the last year to calculate the duration
        year_index_harvest_thinning.insert(self.Global.ncycles_harvest, self.Global.nyears)
        # Get the period lengths for all cycles
        cycle_lengths = np.diff(year_index_harvest_thinning)

        for current_cycle in range(0, self.Global.ncycles_harvest):
            ### st year and end year of each period, shift -1 to remove the first initial condition
            st_cycle = self.Global.year_index_both_plantation[current_cycle] - 1
            if current_cycle < self.Global.ncycles_harvest - 1:
                ed_cycle = self.Global.year_index_both_plantation[current_cycle + 1] - 1
            else:
                ed_cycle = self.Global.nyears

            # calculating the area harvested between year zero and the first thinning, the secondary area harvested (assuming all supply is not met by plantation) is simply:
            # area_harvested_secondary_new = output_need_secondary / output_ha_secondary_first_harvest
            for year in range(st_cycle, ed_cycle):
                # calculating the area harvested AFTER a thinning, account for the wood that you are getting from the secondary thinning and plantation harvest/thinning.
                # Because, in a perfectly managed forest, the thinnings and harvests would be able to supply all the wood required, thus eliminating the need to harvest any ADDITIONAL hectares.
                # Then for each subsequent harvest/thinning, you subtract another (output from thinning * area harvested in year (x-rotation))

                # Current cycle > 0
                for previous_cycle in range(0, current_cycle):
                    Nyears_Ncycles_before = 0
                    Nyears_Ncycles_ahead = 0
                    for i in range(previous_cycle, current_cycle):
                        Nyears_Ncycles_before = Nyears_Ncycles_before + cycle_lengths[i]
                    for j in range(0, previous_cycle):
                        Nyears_Ncycles_ahead = Nyears_Ncycles_ahead + cycle_lengths[j]
                    # This is the wood from the second harvest. output_need_secondary - wood_harvest_accumulate_secondary is the first harvest quantity
                    wood_harvest_accumulate_secondary[year] = wood_harvest_accumulate_secondary[year] + area_harvested_new_secondary[year - Nyears_Ncycles_before] * output_ha_secondary[year, year - Nyears_Ncycles_ahead]   # 2D array output_ha_secondary[year - Nyears_Ncycles_ahead]
                if (self.output_need_secondary[year] - wood_harvest_accumulate_secondary[year] - self.wood_thinning_accumulate_plantation[year]) > 0:
                    # !!!! divide by output from first harvest !!!!
                    # This is to track the secondary area that is first harvested (not the wood reharvesting from the same ha)
                    area_harvested_new_secondary[year] = (self.output_need_secondary[year] - wood_harvest_accumulate_secondary[year] - self.wood_thinning_accumulate_plantation[year]) / output_ha_secondary[year, 0]    # output_ha_secondary[0]
                else:
                    area_harvested_new_secondary[year] = 0

        return area_harvested_new_secondary, wood_harvest_accumulate_secondary


    def calculate_new_area_secondary_regrowth(self, output_ha_secondary):
        """
        Calculate the total new area being harvested from the secondary forest regrowth
        use year index both for regrowth, ncycles_regrowth
        """
        # Add a parameter to mix the percentage of wood from secondary middle aged and secondary mature forest
        secondary_wood_share = 1 - self.Global.secondary_mature_wood_share

        # Initialize two variables
        area_harvested_new_secondary = np.zeros((self.Global.nyears))
        wood_harvest_accumulate_secondary = np.zeros((self.Global.nyears))

        year_index_harvest_thinning = self.Global.year_index_both_regrowth.copy()
        # Add the last year to calculate the duration
        year_index_harvest_thinning.insert(self.Global.ncycles_regrowth, self.Global.nyears)
        # Get the period lengths for all cycles
        cycle_lengths = np.diff(year_index_harvest_thinning)
        # print(year_index_harvest_thinning, cycle_lengths)


        for current_cycle in range(0, self.Global.ncycles_regrowth):
            ### st year and end year of each period, shift -1 to remove the first initial condition
            st_cycle = self.Global.year_index_both_regrowth[current_cycle] - 1
            if current_cycle < self.Global.ncycles_regrowth - 1:
                ed_cycle = self.Global.year_index_both_regrowth[current_cycle + 1] - 1
            else:
                ed_cycle = self.Global.nyears
            for year in range(st_cycle, ed_cycle):
                for previous_cycle in range(0, current_cycle):
                    Nyears_Ncycles_before = 0
                    Nyears_Ncycles_ahead = 0
                    for i in range(previous_cycle, current_cycle):
                        Nyears_Ncycles_before = Nyears_Ncycles_before + cycle_lengths[i]
                    for j in range(0, previous_cycle):
                        Nyears_Ncycles_ahead = Nyears_Ncycles_ahead + cycle_lengths[j]
                    # This is the wood from the second harvest. output_need_secondary - wood_harvest_accumulate_secondary is the first harvest quantity
                    wood_harvest_accumulate_secondary[year] = wood_harvest_accumulate_secondary[year] + area_harvested_new_secondary[year - Nyears_Ncycles_before] * output_ha_secondary[year, year - Nyears_Ncycles_ahead]     # 2D array output_ha_secondary[year - Nyears_Ncycles_ahead]


                if (self.output_need_secondary[year] * secondary_wood_share - wood_harvest_accumulate_secondary[year] - self.wood_thinning_accumulate_plantation[year]) > 0:
                    # !!!! divide by output from first harvest !!!!
                    area_harvested_new_secondary[year] = (self.output_need_secondary[year] * secondary_wood_share - wood_harvest_accumulate_secondary[year] - self.wood_thinning_accumulate_plantation[year]) / output_ha_secondary[year, 0]    # output_ha_secondary[0]
                else:
                    area_harvested_new_secondary[year] = 0

        return area_harvested_new_secondary, wood_harvest_accumulate_secondary


    def calculate_new_area_secondary_mature_regrowth(self, output_ha_secondary):
        """
        Calculate the total new area being harvested from the secondary forest mature regrowth
        use year index both for regrowth, ncycles_regrowth
        """
        # Add a parameter to mix the percentage of wood from secondary middle aged and secondary mature forest
        secondary_wood_share = self.Global.secondary_mature_wood_share

        # Initialize two variables
        area_harvested_new_secondary = np.zeros((self.Global.nyears))
        wood_harvest_accumulate_secondary = np.zeros((self.Global.nyears))

        year_index_harvest_thinning = self.Global.year_index_both_regrowth.copy()
        # Add the last year to calculate the duration
        year_index_harvest_thinning.insert(self.Global.ncycles_regrowth, self.Global.nyears)
        # Get the period lengths for all cycles
        cycle_lengths = np.diff(year_index_harvest_thinning)
        # print(year_index_harvest_thinning, cycle_lengths)

        for current_cycle in range(0, self.Global.ncycles_regrowth):
            ### st year and end year of each period, shift -1 to remove the first initial condition
            st_cycle = self.Global.year_index_both_regrowth[current_cycle] - 1
            if current_cycle < self.Global.ncycles_regrowth - 1:
                ed_cycle = self.Global.year_index_both_regrowth[current_cycle + 1] - 1
            else:
                ed_cycle = self.Global.nyears
            for year in range(st_cycle, ed_cycle):
                for previous_cycle in range(0, current_cycle):
                    Nyears_Ncycles_before = 0
                    Nyears_Ncycles_ahead = 0
                    for i in range(previous_cycle, current_cycle):
                        Nyears_Ncycles_before = Nyears_Ncycles_before + cycle_lengths[i]
                    for j in range(0, previous_cycle):
                        Nyears_Ncycles_ahead = Nyears_Ncycles_ahead + cycle_lengths[j]
                    # This is the wood from the second harvest. output_need_secondary - wood_harvest_accumulate_secondary is the first harvest quantity
                    wood_harvest_accumulate_secondary[year] = wood_harvest_accumulate_secondary[year] +  area_harvested_new_secondary[year - Nyears_Ncycles_before] * output_ha_secondary[year, year - Nyears_Ncycles_ahead]   # 2D array output_ha_secondary[year - Nyears_Ncycles_ahead]


                if (self.output_need_secondary[year] * secondary_wood_share - wood_harvest_accumulate_secondary[year] - self.wood_thinning_accumulate_plantation[year]) > 0:
                    # !!!! divide by output from first harvest !!!!
                    area_harvested_new_secondary[year] = (self.output_need_secondary[year] * secondary_wood_share - wood_harvest_accumulate_secondary[year] - self.wood_thinning_accumulate_plantation[year]) / output_ha_secondary[year, 0]   # output_ha_secondary[0]
                else:
                    area_harvested_new_secondary[year] = 0

        return area_harvested_new_secondary, wood_harvest_accumulate_secondary
