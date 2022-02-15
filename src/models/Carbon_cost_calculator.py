#!/usr/bin/env python
"""
Carbon cost calculator
Separate the PDV module from the original Land_area_calculator

2022/02/14:
Major update: change the slash rate array into a 41x41 year-to-year array, so that one can read in the yearly slash rate.
"""
__author__ = "Liqing Peng"
__copyright__ = "Copyright (C) 2020-2021 World Resources Institute, The Carbon Harvest Model (CHARM) Project"
__credits__ = ["Liqing Peng", "Jessica Zionts", "Tim Searchinger", "Richard Waite"]
__license__ = "Polyform Strict License 1.0.0"
__version__ = "2022.02.1"
__maintainer__ = "Liqing Peng"
__email__ = "liqing.peng@wri.org"
__status__ = "Dev"

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import Secondary_conversion_scenario, Secondary_regrowth_scenario, Secondary_mature_regrowth_scenario, Agricultural_land_tropical_scenario
import Plantation_counterfactual_secondary_plantation_age_scenario


class CarbonCalculator:

    def __init__(self, Global_harvest, Global_growth, Land_area):
        # set up the country profile
        self.Global_harvest = Global_harvest # this is for 100 years of length
        self.Global_growth = Global_growth # this is for 100 years of length
        self.Land_area = Land_area
        ### total PDV
        self.calculate_total_present_discounted_value()

    def calculate_total_present_discounted_value(self):
            """
            - Number of plantation hectares harvested each year: area_harvested_plantation
            - Number of natural hectares harvested each year for BOTH the conversion and regrowth scenarios
            - PDV of harvesting a hectare of plantation in year x
                - This is done by running the plantation calculator over every year, changing the product share %s each time, and only doing the sum of the annual PDVs from 0 : duration-year (i.e. in year 5, you would do the sum from year 0 to year 40-5 (35))
            - PDV of harvesting a hectare of secondary (regrow AND conversion) in year x
                - This is done in the same way- by running the regrow and conversion calculators over every year, changing the product shares each time, and only including the annual PDVs from 0 : duration-year
            """
            ### 2021 05 12
            # In a natural secondary forest that regrows as a secondary forest, for example, the PDV should be the same per hectare every year

            # Initialize
            # nyears rows, nyears of columns
            # array dimension nyears_growth. Only place with nyears_growth
            annual_discounted_value_nyears_plantation, annual_discounted_value_nyears_secondary_conversion, annual_discounted_value_nyears_secondary_regrowth, annual_discounted_value_nyears_secondary_mature_regrowth = [
                    np.zeros((self.Global_growth.nyears, self.Global_growth.nyears)) for _ in range(4)]

            # Get PDV values for the large matrix nyears+40 x nyears
            # This is number of years for product demand, only 2010-2050. As long as it is 100 years' PDV.

            for year in range(self.Global_harvest.nyears):
                # Run the carbon tracker
                stand_result_year_secondary_regrowth = Secondary_regrowth_scenario.CarbonTracker(self.Global_growth, year_start_for_PDV=year)
                stand_result_year_secondary_conversion = Secondary_conversion_scenario.CarbonTracker(self.Global_growth, year_start_for_PDV=year)
                stand_result_year_plantation = Plantation_counterfactual_secondary_plantation_age_scenario.CarbonTracker(self.Global_growth, year_start_for_PDV=year)
                stand_result_year_secondary_mature_regrowth = Secondary_mature_regrowth_scenario.CarbonTracker(self.Global_growth, year_start_for_PDV=year)
                # Update the PDV per ha
                # Every year, the annual discounted value are saved for each column
                annual_discounted_value_nyears_secondary_regrowth[:, year] = stand_result_year_secondary_regrowth.annual_discounted_value[:]
                annual_discounted_value_nyears_secondary_conversion[:, year] = stand_result_year_secondary_conversion.annual_discounted_value[:]
                annual_discounted_value_nyears_plantation[:, year] = stand_result_year_plantation.annual_discounted_value[:]
                annual_discounted_value_nyears_secondary_mature_regrowth[:, year] = stand_result_year_secondary_mature_regrowth.annual_discounted_value[:]

            # plt.plot(np.sum(annual_discounted_value_nyears_secondary_conversion, axis=0))
            # plt.show()
            # exit()

            # Sum up the yearly values
            self.pdv_yearly_plantation = np.sum(annual_discounted_value_nyears_plantation, axis=0)
            self.pdv_yearly_secondary_conversion = np.sum(annual_discounted_value_nyears_secondary_conversion, axis=0)
            self.pdv_yearly_secondary_regrowth = np.sum(annual_discounted_value_nyears_secondary_regrowth, axis=0)
            self.pdv_yearly_secondary_mature_regrowth = np.sum(annual_discounted_value_nyears_secondary_mature_regrowth, axis=0)

            # First, let’s do the secondary PDV (regrowth; conversion) since that’s easier.
            # The total secondary PDV is simply equal to the number of secondary hectares harvested in year x multiplied by the PDV of harvesting one hectare in year x. We have to do this separately for the conversion and regrowth scenarios.
            # array dimension nyears_harvest
            self.total_pdv_secondary_conversion = self.Land_area.area_harvested_new_secondary_conversion * self.pdv_yearly_secondary_conversion
            self.total_pdv_secondary_regrowth = self.Land_area.area_harvested_new_secondary_regrowth * self.pdv_yearly_secondary_regrowth
            self.total_pdv_secondary_mature_regrowth = self.Land_area.area_harvested_new_secondary_mature_regrowth * self.pdv_yearly_secondary_mature_regrowth

            self.total_pdv_plantation = np.zeros((self.Global_harvest.nyears))
            self.area_harvested_new_plantation = np.zeros((self.Global_harvest.nyears))

            if self.Global_harvest.rotation_length_harvest < self.Global_harvest.nyears:
                # From year 0 until the next harvest, the total PDV is equal to the number of plantation hectares harvested multiplied by the PDV of harvesting one hectare in year x.
                for year in range(0, self.Global_harvest.rotation_length_harvest):
                    self.total_pdv_plantation[year] = self.Land_area.area_harvested_plantation[year] * self.pdv_yearly_plantation[year]
                    self.area_harvested_new_plantation[year] = self.Land_area.area_harvested_plantation[year]
                # Beyond the next harvest, the total PDV is equal to
                # (#plantation hectares harvested(x) - # plantation hectares harvested (x – harvest rotation)) * PDV of harvesting one hectare in year x.
                # We have to do this extra step to avoid double counting.
                # There are some cases where a country might be able to supply all of its wood from plantations only, so we have to separate out the re-harvests from the new harvests.
                for year in range(self.Global_harvest.rotation_length_harvest, self.Global_harvest.nyears):
                    self.total_pdv_plantation[year] = (self.Land_area.area_harvested_plantation[year] - self.Land_area.area_harvested_plantation[year - self.Global_harvest.rotation_length_harvest]) * self.pdv_yearly_plantation[year]
                    self.area_harvested_new_plantation[year] = self.Land_area.area_harvested_plantation[year] - self.Land_area.area_harvested_plantation[year - self.Global_harvest.rotation_length_harvest]

            else:
                for year in range(0, self.Global_harvest.nyears):
                    self.total_pdv_plantation[year] = self.Land_area.area_harvested_plantation[year] * self.pdv_yearly_plantation[year]
                    self.area_harvested_new_plantation[year] = self.Land_area.area_harvested_plantation[year]

            def get_total_PDV(total_pdv):
                # Convert to megatonnes.
                total_pdv_sum = np.sum(total_pdv) / 1000000
                ### 2021 May 12 Remove the second discounting
                return total_pdv_sum

            # Unit: megat tonnes C
            self.total_pdv_plantation_sum = get_total_PDV(self.total_pdv_plantation)
            # For secondary regrowth (full middle-aged to 0 middle-aged)
            self.total_pdv_secondary_regrowth_combined = self.total_pdv_secondary_regrowth + self.total_pdv_secondary_mature_regrowth
            self.total_pdv_secondary_regrowth_sum = get_total_PDV(self.total_pdv_secondary_regrowth_combined)
            # For secondary conversion
            self.total_pdv_secondary_conversion_sum = get_total_PDV(self.total_pdv_secondary_conversion)

            # For scenario add up
            self.total_pdv_plantation_secondary_regrowth = self.total_pdv_plantation_sum + self.total_pdv_secondary_regrowth_sum
            self.total_pdv_plantation_secondary_conversion = self.total_pdv_plantation_sum + self.total_pdv_secondary_conversion_sum


    def calculate_annual_carbon_stock(self):

        # 2022/01/25 FIXME For stand carbon stock accumulation
        # 2022/02/02 wrong formula turn off
        # FIXME add the accumulate carbon, the end of 40 years of growth 2050 tC/ha for 40-years
        self.total_C_stand_pool_cum_secondary_conversion = self.Land_area.area_harvested_new_secondary_conversion * Secondary_conversion_scenario.CarbonTracker(self.Global_harvest, year_start_for_PDV=0).totalC_stand_pool[-1]
        self.total_C_stand_pool_cum_secondary_regrowth = self.Land_area.area_harvested_new_secondary_regrowth * Secondary_regrowth_scenario.CarbonTracker(self.Global_harvest,year_start_for_PDV=0).totalC_stand_pool[-1]
        self.total_C_stand_pool_cum_secondary_mature_regrowth = self.Land_area.area_harvested_new_secondary_mature_regrowth * Secondary_mature_regrowth_scenario.CarbonTracker(self.Global_harvest, year_start_for_PDV=0).totalC_stand_pool[-1]
        # add up regrowth and mature regrowth = tC yearly 2010-2050, each year the total accumulate carbon after 40 years of regrowth
        self.total_C_stand_pool_cum_secondary_regrowth_combined = self.total_C_stand_pool_cum_secondary_regrowth + self.total_C_stand_pool_cum_secondary_mature_regrowth
