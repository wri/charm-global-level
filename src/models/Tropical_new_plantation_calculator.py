#!/usr/bin/env python
"""
New Tropical Plantation Module
1. Grab the national results from the result file
2. Calculate the global results
3. Calculate the new tropical plantation scneario based on global results
"""
__author__ = "Liqing Peng"
__copyright__ = "Copyright (C) 2020-2023 World Resources Institute, The Carbon Harvest Model (CHARM) Project"
__credits__ = ["Liqing Peng", "Jessica Zionts", "Tim Searchinger", "Richard Waite"]
__license__ = "Polyform Strict License 1.0.0"
__version__ = "2023.1.1"
__maintainer__ = "Liqing Peng"
__email__ = "liqing.peng@wri.org"
__status__ = "Dev"

import numpy as np
import Global_by_country, Agricultural_land_tropical_scenario


class PlantationCalculator:

    def __init__(self, datafile, results):

        ### Read in model results
        self.datafile = datafile
        self.results = results
        self.nyears_harvest_settings = Global_by_country.SetupTime(datafile, country_iso='BRA', nyears_run_control='harvest')
        self.Global = Global_by_country.Parameters(datafile, self.nyears_harvest_settings, country_iso='BRA')
        self.nyears = self.Global.nyears
        self.rotation_length = self.Global.rotation_length_harvest # this is the rotation length from Brazil, currently set to 7


    def prepare_global_outputs_for_new_tropical_scenario(self):
        """Extract outputs for the new tropical plantation scenario"""
        # 2022 Jan Lists
        carbon_lists = ['Default: Plantation supply wood (mega tC)', 'Default: Secondary forest supply wood (mega tC)',
                        'S1 regrowth: total PDV (mega tC)', 'S1 regrowth: PDV plantation (mega tC)',
                        'S1 regrowth: PDV secondary (mega tC)', 'S2 conversion: total PDV (mega tC)',
                        'S3 mixture: total PDV (mega tC)', 'S4 125% GR: total PDV (mega tC)',
                        'S5 62% SL: total PDV (mega tC)', 'S6 WFL 50% less: total PDV (mega tC)']
        area_lists = ['Plantation area (ha)', 'S1 regrowth: Secondary area (ha)', 'S2 conversion: Secondary area (ha)',
                      'S3 mixture: Secondary area (ha)', 'S3 mixture: Secondary middle aged area (ha)',
                      'S3 mixture: Secondary mature area (ha)', 'S4 125% GR: Secondary area (ha)',
                      'S5 62% SL: Secondary area (ha)', 'S6 WFL 50% less: Secondary area (ha)']
        # Get global carbon and area numbers
        carbon_global = self.results[self.results.select_dtypes(include=['number']).columns][
                            carbon_lists].sum() / 0.8 * 1000000  # mega tC to tC
        area_global = self.results[self.results.select_dtypes(include=['number']).columns][area_lists].sum() / 0.8

        return carbon_global, area_global


    def prepare_new_tropical_plantations_area(self, nyears, rotation_length, area_established_agriland_annual_global):
        """
            This is for the Tropical New Plantation Scenario, 4th scenario's input
            Set up plantation establishment rate per year, time and total area for harvest
        """
        # The first established plantation is in year 0, 2010; the last established plantation is in one rotation ahead of the last year. nyears - 1 + 1 for the range().
        year_new_plantation_st, year_new_plantation_ed = 0, nyears - rotation_length
        # The first harvested year of the established plantation is in one rotation behind of the first established year; the last harvested year is in last year, nyears - 1
        year_harvest_st, year_harvest_ed = year_new_plantation_st + rotation_length, nyears - 1

        area_established_new_agriland = np.zeros(nyears) # This is the area establishing plantation starting from year 0
        area_harvested_new_agriland = np.zeros(nyears)  # This is the new established area starting from the first rotation end
        area_harvested_agriland = np.zeros(nyears)   # This is the total harvested area plantation for each year's established plantation

        # For each year of new established plantations, accumulate the area,
        # and then count the number of rotation for that year's plantation (there may be multiple harvests in the same area over the course)
        for year in range(year_new_plantation_st, year_new_plantation_ed):
            area_established_new_agriland[year] = area_established_agriland_annual_global
            # divide the rotation length and round down
            nrotation = (year_harvest_ed - year) // rotation_length
            area_harvested_agriland[year] = area_established_agriland_annual_global * nrotation

        # after one rotation period
        area_harvested_new_agriland[rotation_length:] = area_established_agriland_annual_global

        # area_established_agriland = np.cumsum(area_established_new_agriland) # This is to show the accumulate agricultural land
        area_established_new_agriland_accumulate = np.sum(area_established_new_agriland)
        area_harvested_agriland_accumulate = np.sum(area_harvested_agriland)
        area_harvested_new_agriland_accumulate = np.sum(area_harvested_new_agriland)

        # CHECK - area_established_new_agriland_accumulate should EQUAL area_harvested_new_agriland_accumulate
        if area_harvested_new_agriland_accumulate != area_established_new_agriland_accumulate:
            raise ValueError('The total new tropical plantation area does not match!')
        return area_established_new_agriland_accumulate, area_harvested_agriland_accumulate, area_harvested_new_agriland


    def run_new_tropical_plantations_scenario(self):
        """
        VERY IMPORTANT FEATURE OF THIS SCRIPT!
        Tropical New Plantation Scenario
        This is the 4th scenario
        require the input from the existing model outputs
        """

        ### New plantation land area assumption
        # We assume the *** 2Mha *** per year of agricultural land are converted to plantation evenly from 2010-2050
        area_established_agriland_annual_global = 2 * 1000000  # Mha per year
        area_established_new_agriland_accumulate, area_harvested_agriland_accumulate, area_harvested_new_agriland = self.prepare_new_tropical_plantations_area(self.nyears, self.rotation_length, area_established_agriland_annual_global)

        ### Read in the country sum parameters
        carbon_global, area_global = self.prepare_global_outputs_for_new_tropical_scenario()
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
        # 2023/Jan: Change the rotation year from exactly 10 years to all countries that are below 10 years
        # only tropical countries that are shorter than 10 years rotation period: Brazil, Congo, Ethiopia, Indonesia, Vietnam (Add Ethiopia)
        ### 3. Calculate average tropical plantation wood harvest
        # weighted average of the output per ha for each harvest
        tropical_countries_iso = ['BRA', 'COD', 'ETH', 'IDN', 'VNM']
        # Get the plantation area
        area_plantation_tropical = [self.results.loc[self.results['ISO']==iso]['Plantation area (ha)'].values[0] for iso in tropical_countries_iso]
        # Get the output per ha at the 2020 year
        output_ha_tropical = [self.results.loc[self.results['ISO']==iso]['Output per ha Agricultural land conversion (tC/ha)'].values[0] for iso in tropical_countries_iso]
        weighted_sum = sum([area_plantation_tropical[i] * output_ha_tropical[i] for i in range(len(output_ha_tropical))])
        # Get the weighted average output per ha for the five countries
        output_ha_tropical_average = weighted_sum / sum(area_plantation_tropical)

        ### 4. Calculate the total wood harvest/production from the new plantation from agricultural land
        # New plantation wood production for 2020-2050, tC, from the 2 Mha per year agricultural land with continuous harvest
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
            # Global = Global_by_country.Parameters(datafile, country_iso=iso)
            nyears_harvest_settings = Global_by_country.SetupTime(self.datafile, country_iso=iso, nyears_run_control='harvest')
            nyears_growth_settings = Global_by_country.SetupTime(self.datafile, country_iso=iso, nyears_run_control='growth')
            ### Default plantation scenarios, (1) secondary harvest regrowth and (2) conversion
            ### Read in global parameters ###
            global_harvest_settings = Global_by_country.Parameters(self.datafile, nyears_harvest_settings, country_iso=iso)
            global_growth_settings = Global_by_country.Parameters(self.datafile, nyears_growth_settings, country_iso=iso)
            annual_discounted_value_nyears_agriland = np.zeros((global_growth_settings.nyears, global_harvest_settings.nyears))
            for year in range(global_harvest_settings.nyears):
                #### This is the only line that requires the CHARM model run ####
                annual_discounted_value_nyears_agriland[:, year] = Agricultural_land_tropical_scenario.CarbonTracker(global_growth_settings, year_start_for_PDV=year).annual_discounted_value[:]
            pdv_yearly_agriland = np.sum(annual_discounted_value_nyears_agriland, axis=0)

            total_pdv_agriland = np.zeros((global_harvest_settings.nyears))
            for year in range(global_harvest_settings.nyears):
                total_pdv_agriland[year] = pdv_yearly_agriland[year] * area_harvested_new_agriland[year]
            total_pdv_agriland_sum_country.append(np.sum(total_pdv_agriland))

        # use plantation area to weighted average from the tropical countries
        pdv_weighted_sum = sum([area_plantation_tropical[i] * total_pdv_agriland_sum_country[i] for i in range(len(total_pdv_agriland_sum_country))])
        # Get the weighted average output per ha for the four countries
        total_pdv_tropical_weighted_average = pdv_weighted_sum / sum(area_plantation_tropical)

        ### 8. Calculate global PDV as Total PDV for existing plantation + Total PDV for new plantation + New total PDV for secondary
        global_pdv = total_pdv_plantation + total_pdv_secondary_after_replace + total_pdv_tropical_weighted_average

        # Convert tC to GtCO2 per year.
        carbon_cost_annual = global_pdv / 1000000000 * 44 / 12 / self.nyears
        # Convert ha to Mha
        updated_secondary_area = (area_harvested_new_secondary_sum - area_reduced_secondary) / 1000000
        new_plantation_area = np.sum(area_harvested_new_agriland) / 1000000

        ### 9. Calculate the total secondary wood supply reduced from the new plantation
        total_wood_secondary_after_replace = total_wood_secondary - wood_supply_agriland
        total_wood_plantation_after_replace = total_wood_plantation + wood_supply_agriland

        return carbon_cost_annual, updated_secondary_area, new_plantation_area, total_wood_secondary_after_replace, total_wood_plantation_after_replace


    # def calculate_existing_tropical_plantations_numbers(self):
    #     """
    #     Tropical Plantation Equivalent
    #     require the input from the CST model outputs
    #     In 2010, pull out the total quantity of wood harvested from NON-plantation forests. Then calculate an average yield for tropical forests in 2010 (tC/ha). Then simply divide the non-plantation quantity by the tropical yield to get the total number of tropical plantation hectares that could replace one year’s worth of global secondary forest harvest.
    #     """
    #     # Read in CST demand 2010 existing level
    #     results = pd.read_excel(self.datafile, sheet_name='CST_NOSUB_IND')
    #
    #     ### Read in the country sum parameters
    #     carbon_global, area_global = self.prepare_global_outputs_for_new_tropical_scenario(results)
    #     total_wood_secondary = carbon_global['Default: Secondary forest supply wood (mega tC)']     # Total wood from secondary, tC
    #     total_wood_plantation = carbon_global['Default: Plantation supply wood (mega tC)']     # Total wood from secondary, tC
    #
    #     ### Calculate average tropical plantation wood harvest
    #     # only tropical countries that are 10 years rotation period: Brazil, Congo, Indonesia, Vietnam
    #     # weighted average of the output per ha for each harvest
    #     tropical_countries_iso = ['BRA', 'COD', 'ETH', 'IDN', 'VNM']
    #     # Get the plantation area
    #     area_plantation_tropical = [results.loc[results['ISO']==iso]['Plantation area (ha)'].values[0] for iso in tropical_countries_iso]
    #     # Get the output per ha at the 2020 year
    #     output_ha_tropical = [results.loc[results['ISO']==iso]['Output per ha Agricultural land conversion (tC/ha)'].values[0] for iso in tropical_countries_iso]
    #     weighted_sum = sum([area_plantation_tropical[i] * output_ha_tropical[i] for i in range(len(output_ha_tropical))])
    #     # Get the weighted average output per ha for the four countries
    #     output_ha_tropical_average = weighted_sum / sum(area_plantation_tropical)
    #
    #     # For cst demand 2010 level
    #     wood_secondary_2010 = total_wood_secondary / self.nyears
    #     area_plantation_tropical_equivalent = wood_secondary_2010 / output_ha_tropical_average
    #     wood_secondary_share = total_wood_secondary / (total_wood_plantation + total_wood_secondary)
    #
    #     return total_wood_secondary, wood_secondary_2010, wood_secondary_share, output_ha_tropical_average, area_plantation_tropical_equivalent

