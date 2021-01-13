#!/usr/bin/env python
__author__ = "Liqing Peng, Jessica Zionts, Tim Searchinger"
__copyright__ = "Copyright (C) 2020 WRI, The Carbon Harvest Model (CHarM) Project"
__maintainer__ = "Liqing Peng"
__email__ = "liqing.peng@wri.org"
"""
Global parameters required for carbon tracker for different scenarios
1. INPUT
- set up a country to run
- read in parameters file
2. Time settings
- number of years
- time of harvest/thinning
- harvest percentage
3. Biophysical parameters
- C density
- Growth rate
- Plantation area
- Decay rate
- Slash rate
4. Product parameters
- Product share
5. Other parameters
- LLP parameters
"""

import numpy as np
import pandas as pd

class Parameters:

    def __init__(self, datafile, country_iso='BRA'):
        """Read in inputs"""

        input_data = pd.read_excel(datafile, sheet_name='Inputs', skiprows=1)
        self.input_country = input_data.loc[input_data['ISO']==country_iso] # Country ISO code
        self.country_name = self.input_country['Country'].values[0]
        del input_data

        ### Run the functions
        self.setup_time()
        self.setup_biophysical_parameters()
        self.setup_product_parameters()
        self.setup_LLP_substitution()
        self.setup_misc()
        self.setup_harvest_slash_percentage()


    def setup_time(self):
        """Time settings"""
        ### Years/Periods
        years = int(self.input_country['Years'].values[0])           # Number of future years beyond 2010. e.g., 40 years means 2011-2050.
        self.nyears = years + 1   # Number of the total years, including the initial year 2010.
        self.arraylength = self.nyears + 1  # Length of array (The number of columns of the array) = number of future years + initial condition

        self.rotation_length_harvest = int(self.input_country['Rotation Period (years)'].values[0])    # Rotation length for harvest
        self.rotation_length_thinning = int(self.input_country['Thinning period (years between thinning of managed secondary forest)'].values[0])
        # self.rotation_length_harvest = 10
        # self.rotation_length_thinning = 5

    def setup_biophysical_parameters(self):
        # Growth rates, C density
        self.GR_plantation = self.input_country['Young Plantation GR (MgC/ha/year) (Harris)'].values[0]
        self.GR_old_plantation = self.input_country['Old Plantation GR (MgC/ha/year) (Harris)'].values[0]
        self.GR_young_secondary = self.input_country['Young Secondary GR (MgC/ha/year) (Harris)'].values[0]
        self.GR_old_secondary = self.input_country['Old Secondary GR (MgC/ha/year) (Harris)'].values[0]
        self.C_harvest_density_secondary = self.input_country['Avg Secondary C Density (MgC/ha) (Harris)'].values[0]
        self.physical_area_plantation = self.input_country['Plantation Area (ha) (FAO)'].values[0]
        self.ratio_root_shoot = 0.26
        self.carbon_wood_ratio = 0.5

        # Decay parameters
        self.half_life_LLP = self.input_country['LLP half life'].values[0]
        self.half_life_SLP = self.input_country['SLP half life'].values[0]
        self.half_life_VSLP = self.input_country['VSLP half life'].values[0]
        self.half_life_slash = self.input_country['Slash half life'].values[0]
        self.half_life_root = self.input_country['Roots half life'].values[0]
        self.half_life_landfill = self.input_country['Landfill half life'].values[0]

        # Slash parameters
        self.slash_burn = self.input_country['% of slash burned in the field'].values[0]
        self.slash_left = self.input_country['% of slash left to decay'].values[0]


    def setup_product_parameters(self):
        # Calculate annual wood demand/production and product pool breakdown
        # Product share ratio, depending on country input data
        self.product_share_slash_plantation = self.input_country['% slash plantation'].values[0]
        self.product_share_slash_secondary = self.input_country['% slash natural'].values[0]
        self.product_share_VSLP_thinning = self.input_country['% in VSLP thinning'].values[0]
        self.product_share_SLP_thinning = self.input_country['% in SLP thinning'].values[0]
        self.product_share_LLP_thinning = self.input_country['% in LLP thinning'].values[0]
        self.product_share_slash_thinning = self.input_country['% in slash thinning'].values[0]

        # Dry matter, across 40 years
        VSLP_2010 = self.input_country['VSLP 10'].values[0]
        VSLP_2050 = self.input_country['VSLP 50'].values[0]
        SLP_2010 = self.input_country['SLP 10'].values[0]
        SLP_2050 = self.input_country['SLP 50'].values[0]
        LLP_2010 = self.input_country['LLP 10'].values[0]
        LLP_2050 = self.input_country['LLP 50'].values[0]

        # Create array of VSLP,SLP,LLP ratios AND quantities for every year. This is important because the ratios will change each year.
        product_LLP, product_SLP, product_VSLP = [np.zeros((self.nyears)) for _ in range(3)]
        product_LLP[0], product_LLP[40] = LLP_2010, LLP_2050
        product_SLP[0], product_SLP[40] = SLP_2010, SLP_2050
        product_VSLP[0], product_VSLP[40] = VSLP_2010, VSLP_2050

        # Interpolate the production numbers: take the difference between the last and first year for each product pool, and divide by the number of years
        for year in range(1, len(product_VSLP)):
            product_LLP[year] = product_LLP[0] + (product_LLP[40] - product_LLP[0]) / (2050 - 2010) * year
            product_SLP[year] = product_SLP[0] + (product_SLP[40] - product_SLP[0]) / (2050 - 2010) * year
            product_VSLP[year] = product_VSLP[0] + (product_VSLP[40] - product_VSLP[0]) / (2050 - 2010) * year

        # Create an array of the TOTAL wood products for each year (sum of LLP,SLP,VSLP).
        self.product_total = product_LLP + product_SLP + product_VSLP
        # Product numbers before accounting for slash
        self.product_share_LLP, self.product_share_SLP, self.product_share_VSLP = [product / self.product_total for product in
                                                                    (product_LLP, product_SLP, product_VSLP)]

    def setup_LLP_substitution(self):
        # LLP parameters
        self.llp_construct_ratio = self.input_country['% LLP for construction'].values[0]
        self.llp_displaced_CS_ratio = self.input_country['% LLP displacing concrete and steel'].values[0]
        CF_CO2_C = 44 / 12
        CF_wood_C = 0.5

        # Production emission substitution factor for LLP
        # net tC fossil energy saved per t carbon in wood use
        # Flag to determine calculated SUB factor or default, need to be consistent with the input excel file (w substitution)
        FLAG_CALC_SUB = 1

        if FLAG_CALC_SUB == 0: # Original, set up to the default 1.2 value
            # For example, 1.2 tC/tC means the 1.2 tC being saved if 1 tC is used.
            self.coef_construt_substitution = self.input_country['Emissions substitution factor for LLP (tC saved/tons C in LLP)'].values[0]
        else:
            # Churkina 2020
            # First, replacement ratio.
            # Qconcrete_saved_by_wood (kg concrete/kg wood) = Qconcrete (kg/m2) / Qwood (kg/m2)
            # Calculate the quantity of concrete/steel being saved by wood used.
            # wooduse = 209.4
            # saved_concrete_by_wooduse = 608.4 / wooduse
            # saved_steel_by_wooduse = 82.7 / wooduse

            saved_concrete_by_wooduse = self.input_country['Avoided ton concrete per ton of wood (t concrete/t wood)'].values[0]
            saved_steel_by_wooduse = self.input_country['Avoided ton steel per ton of wood (t steel/t wood)'].values[0]
            # Second, emission factor.
            # EF (tCO2e/t material)
            # Calculate the quantity of C emission by a given quantity of concrete/steel/timber.
            # EF_concrete = 0.145
            # EF_steel = 2.11
            # EF_timber = 0.44
            EF_concrete = self.input_country['Emission factor for concrete (tCO2e/t concrete)'].values[0]
            EF_steel = self.input_country['Emission factor for steel (tCO2e/t steel)'].values[0]
            EF_timber = self.input_country['Emission factor for timber (tCO2e/t wood)'].values[0]

            # Third, substitution value.
            # = (avoided carbon emission from concrete/steel - emission from wood)/(wood quantity in carbon)
            # This number is the quantity of fossil emissions(CO2) from production of a steel or concrete building minus the emissions from alterative construction of wood per kilogram of wood used
            self.coef_construt_substitution = (saved_concrete_by_wooduse * EF_concrete + saved_steel_by_wooduse * EF_steel - 1 * EF_timber) / CF_CO2_C / CF_wood_C
            # Fourth, % reduction of timber system relative to steel/concrete or composite systems.
            self.carbon_reduction_timber_to_cs = 1 * EF_timber / (saved_concrete_by_wooduse * EF_concrete + saved_steel_by_wooduse * EF_steel) - 1


    def setup_misc(self):
        # Others
        self.discount_rate = self.input_country['Discount rate'].values[0]
        self.landfill_methane_ratio = self.input_country['% of carbon in landfill converted to methane'].values[0]

    # This number is the quantity of fossil emissions(CO2) from production of a steel or concrete building minus the emissions from alterative construction of wood per kilogram of wood used

    def setup_harvest_slash_percentage(self):

        ### Combine harvest and thinning together in the time index
        # Create index of years where harvest happened.
        # The first harvest occurs in year 1, index=1. index=0 is the initial condition
        self.year_index_harvest_plantation = np.arange(1, self.arraylength, self.rotation_length_harvest, dtype=int)
        self.year_index_harvest_regrowth = [1]

        # if thinning happened
        if (np.isnan(self.rotation_length_thinning) == False) & (self.rotation_length_thinning > 0):
            # if harvest happened within N years time period
            if len(self.year_index_harvest_plantation) > 1:
                year_index_thinning_plantation = []
                for cycle_harvest in range(len(self.year_index_harvest_plantation)-1):
                    year_index_thinning_plantation.append(np.arange(self.year_index_harvest_plantation[cycle_harvest], self.year_index_harvest_plantation[cycle_harvest+1], self.rotation_length_thinning, dtype=int))
                self.year_index_thinning_plantation = np.array(year_index_thinning_plantation).flatten().tolist()
            # if no second harvest in the time frame
            else:
                self.year_index_thinning_plantation = np.arange(self.year_index_harvest_plantation[0], self.arraylength, self.rotation_length_thinning, dtype=int).tolist()

            self.year_index_both_plantation = sorted(list(set(self.year_index_harvest_plantation) | set(self.year_index_thinning_plantation)))
            self.ncycles_harvest = len(self.year_index_both_plantation)

        # if no thinning happened
        else:
            self.year_index_thinning_plantation = []
            self.year_index_both_plantation = self.year_index_harvest_plantation.tolist()
            self.ncycles_harvest = len(self.year_index_harvest_plantation)


        ### Harvest
        # Tree cover percentage, from 50% to 100% (100% will be zero tree cover area left in the stand pool)
        self.harvest_percentage_default = 1.0

        ### Thinning
        # For plantation or secondary conversion scenario
        self.thinning_percentage_default = self.input_country['% Removed in thinning plantation'].values[0]
        # For secondary regrowth scenario
        self.thinning_percentage_regrowth = 0.1  # self.input_country['% Removed in thinning regrowth'].values[0]

        ### Harvest/slash percentage
        self.harvest_percentage_plantation = np.zeros((self.arraylength))
        self.harvest_percentage_regrowth = np.zeros((self.arraylength))
        slash_percentage_plantation = np.zeros((self.arraylength))  # slash percentage when harvest or thinning
        slash_percentage_secondary_conversion = np.zeros((self.arraylength))  # slash percentage when harvest or thinning
        slash_percentage_secondary_regrowth = np.zeros((self.arraylength))  # slash percentage when harvest or thinning

        ### For plantation/conversion scenario
        if (np.isnan(self.thinning_percentage_default) == False) & (self.thinning_percentage_default != 0) & (np.isnan(self.rotation_length_thinning) == False) & (self.rotation_length_thinning > 0):
            self.harvest_percentage_plantation[self.year_index_thinning_plantation] = self.thinning_percentage_default
            self.harvest_percentage_plantation[self.year_index_harvest_plantation] = self.harvest_percentage_default

            # All harvest is plantation slash
            slash_percentage_plantation[self.year_index_thinning_plantation] = self.product_share_slash_thinning
            slash_percentage_plantation[self.year_index_harvest_plantation] = self.product_share_slash_plantation

            # The first harvest is secondary slash, the others are plantation slash
            slash_percentage_secondary_conversion[self.year_index_thinning_plantation] = self.product_share_slash_thinning
            slash_percentage_secondary_conversion[self.year_index_harvest_plantation] = self.product_share_slash_plantation
            slash_percentage_secondary_conversion[1] = self.product_share_slash_secondary

        else:
            self.harvest_percentage_plantation[self.year_index_harvest_plantation] = self.harvest_percentage_default
            slash_percentage_plantation[self.year_index_harvest_plantation] = self.product_share_slash_plantation
            # The first harvest is secondary slash, the others are plantation slash
            slash_percentage_secondary_conversion[self.year_index_harvest_plantation] = self.product_share_slash_secondary
            slash_percentage_secondary_conversion[1] = self.product_share_slash_secondary


        ### For regrowth scenario
        self.year_index_harvest_regrowth = [1]
        if (np.isnan(self.thinning_percentage_regrowth) == False) & (self.thinning_percentage_regrowth != 0) & (np.isnan(self.rotation_length_thinning) == False) & (self.rotation_length_thinning > 0):
            self.year_index_thinning_regrowth = np.arange(1, self.arraylength, self.rotation_length_thinning, dtype=int)
            # Include the first harvest
            self.year_index_both_regrowth = sorted(list(set(self.year_index_harvest_regrowth) | set(self.year_index_thinning_regrowth)))
            self.ncycles_regrowth = len(self.year_index_both_regrowth)

            self.harvest_percentage_regrowth[self.year_index_thinning_regrowth] = self.thinning_percentage_regrowth
            self.harvest_percentage_regrowth[self.year_index_harvest_regrowth] = self.harvest_percentage_default
            # The first harvest is secondary slash, remove following harvests
            slash_percentage_secondary_regrowth[self.year_index_thinning_regrowth] = self.product_share_slash_thinning
            slash_percentage_secondary_regrowth[1] = self.product_share_slash_secondary
        else:
            self.year_index_both_regrowth = self.year_index_harvest_regrowth
            self.harvest_percentage_regrowth[self.year_index_harvest_regrowth] = self.harvest_percentage_default
            self.ncycles_regrowth = len(self.year_index_both_regrowth)
            slash_percentage_secondary_regrowth[1] = self.product_share_slash_secondary


        ### To get the staggered array for slash percentage
        def staircase(array):
            array = pd.DataFrame(array)
            # Piecewise array for aboveground biomass actually harvested/thinned during rotation harvest/thinning
            array = array.replace(to_replace=0, method='ffill').values.reshape(self.arraylength)
            return array

        self.slash_percentage_plantation, self.slash_percentage_secondary_conversion, self.slash_percentage_secondary_regrowth = [staircase(slash_percentage) for slash_percentage in [slash_percentage_plantation, slash_percentage_secondary_conversion, slash_percentage_secondary_regrowth]]


