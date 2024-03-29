#!/usr/bin/env python
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
__author__ = "Liqing Peng"
__copyright__ = "Copyright (C) 2023 Liqing Peng, Timothy D. Searchinger, Jessica Zionts, Richard Waite"
__license__ = "MIT"
__date__ = "2023.2"
__maintainer__ = "Liqing Peng"
__email__ = "liqing.peng@wri.org"
__version__ = "1.0"

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class SetupTime:
    """This reads the nyears first and then take input: nyears_run_control to run the individual scenarios"""
    def __init__(self, datafile, country_iso='BRA', nyears_run_control='harvest'):
        """Read in time inputs
        Preparing output of the nyears for Class Parameters
        """
        input_data = pd.read_excel(datafile, sheet_name='Inputs', skiprows=1)
        self.input_country = input_data.loc[input_data['ISO'] == country_iso]  # Country ISO code
        self.country_name = self.input_country['Country'].values[0]
        self.nyears_run_control = nyears_run_control

        self.setup_nyears()

    def setup_nyears(self):
        """Time settings"""
        ### Years
        # Number of future years of harvesting forests beyond 2010. e.g., 40 years means 2011-2050.
        self.nyears_harvest_meet_demand = int(self.input_country['Years of harvests'].values[0])
        self.nyears_growth_PDV = int(self.input_country['Years of growth'].values[0])

        # In case the number of years for PDV calculation input is smaller than the nyears of harvests
        if self.nyears_growth_PDV < self.nyears_harvest_meet_demand:
            self.nyears_growth_PDV = self.nyears_harvest_meet_demand

        # Situation 1: if the scenarios are run using nyears of harvest. This is used in most cases, biomass output and land area calculation
        if self.nyears_run_control is 'harvest':
            self.nyears = self.nyears_harvest_meet_demand + 1  # Number of the total years, including the initial year 2010.
        # Situation 2: if the scenarios are run using nyears of growth. This is used in PDV calculation. It only depends on how long you want to build in the PDv calculation
        elif self.nyears_run_control is 'growth':
            self.nyears = self.nyears_growth_PDV + 1  # Number of the total years, including the initial year 2010.
        else: # default Situation 1.
            self.nyears = self.nyears_harvest_meet_demand + 1  # Number of the total years, including the initial year 2010.

        self.arraylength = self.nyears + 1



class Parameters:

    def __init__(self, datafile, nyears_setup, country_iso='BRA', discount_rate_input=None, future_demand_level='BAU', substitution_mode='SUB', vslp_input_control='ALL', vslp_future_demand='default', secondary_mature_wood_share=0, plantation_growth_increase_ratio=1.0, slash_rate_mode='natural'):
        """Read in inputs"""

        input_data = pd.read_excel(datafile, sheet_name='Inputs', skiprows=1)
        self.input_country = input_data.loc[input_data['ISO']==country_iso] # Country ISO code
        self.country_name = self.input_country['Country'].values[0]
        self.nyears = nyears_setup.nyears
        self.arraylength = nyears_setup.arraylength
        # Meta Parameters for scenarios
        self.discount_rate_input = discount_rate_input
        self.future_demand_level = future_demand_level
        self.substitution_mode = substitution_mode
        self.vslp_input_control = vslp_input_control   # for VSLP product pool selection
        self.vslp_future_demand = vslp_future_demand    # for VSLP future demand control (5th scenario)
        self.secondary_mature_wood_share = secondary_mature_wood_share  # for secondary wood supply distribution among the secondary forest
        self.plantation_growth_increase_ratio = plantation_growth_increase_ratio  # for productivity increase ratio
        self.slash_rate_mode = slash_rate_mode
        del input_data

        ### Run the functions
        self.setup_time_period()
        self.setup_biophysical_parameters()
        self.setup_product_parameters()
        self.setup_LLP_substitution()
        self.setup_VSLP_substitution()
        self.setup_misc()
        self.setup_harvest_thinning_events()
        self.setup_harvest_slash_percentage()


    def setup_biophysical_parameters(self):
        """Growth rates, C density"""
        ### Plantation
        self.GR_young_plantation = self.input_country['Young Plantation GR'].values[0] * self.plantation_growth_increase_ratio
        self.GR_old_plantation = self.input_country['Middle Plantation GR'].values[0] * self.plantation_growth_increase_ratio
        # Add the converted plantation GR for secondary conversion scenario
        self.GR_converted_plantation = self.input_country['Converted Plantation GR'].values[0]
        self.physical_area_plantation = self.input_country['Plantation Area'].values[0]

        ### Secondary forest
        # Growth rates GR1 and GR2 inputs
        self.GR_young_secondary = self.input_country['Young Secondary GR'].values[0]     # Stand age 0-20
        self.GR_middle_secondary = self.input_country['Middle Secondary GR'].values[0]   # Stand age 20-100
        # Read the ratio between mature secondary forest (stand age 80-120) growth rate and middle aged secondary forest (20-100)
        # 2022/1/20: turn off the ratio
        # self.GR_mature_secondary = self.GR_middle_secondary * self.input_country['Mature to middle secondary GR ratio'].values[0]

        # Growth rate curve
        # Monod function: C = agb_max * AGE / (AGE + age_50perc)
        age_first = 20      # This is relatively established
        age_second = 100    # This is relatively not established
        C_first = age_first * self.GR_young_secondary  # This is the carbon density at the age_first
        C_second = C_first + (age_second - age_first) * self.GR_middle_secondary  # This is the carbon density at the age_second
        self.age_50perc = age_first * age_second * (C_second - C_first) / (age_second * C_first - age_first * C_second)
        self.agb_max = C_first / age_first * (age_first + self.age_50perc)

        # C density
        self.C_harvest_density_secondary = self.input_country['Avg Secondary C Density'].values[0]
        # Calculate the equivalent age of the C density based on the Monod function
        age_eq_C_secondary = self.age_50perc * self.C_harvest_density_secondary / (self.agb_max - self.C_harvest_density_secondary)
        # The harvesting year is 20 years after the equivalent age, but at least to be 40 years (lower bound in case some C density too low)
        if age_eq_C_secondary + 20 > 40:
            self.age_for_harvest = age_eq_C_secondary + 20
        else:
            self.age_for_harvest = 40

        ### Underground - aboveground biomass relationship
        # This constant approach is depreciated, used only in the Plantation scenario as a reference
        # Mokany 2006
        self.root_shoot_coef = 0.489

        # Experiment 1: root_shoot_coef increases 25 %, Experiment 2: root_shoot_coef decreases 25%
        # self.root_shoot_coef = 0.489 * self.input_country['Root to Shoot ratio scaling factor'].values[0]
        # FIXME in the future, build the parameter into the parameter file

        self.root_shoot_power = 0.89
        self.carbon_wood_ratio = 0.5

        # Set up the under bark to over bark conversion factor: M. O'Brien 2018: FAO, 2010. Global Forest Resources Assessment 2010. FAO Forestry Paper 163, Rome, Italy
        self.overbark_underbark_ratio = 1.15

        ### Decay parameters
        self.half_life_LLP = self.input_country['LLP half life'].values[0]
        self.half_life_SLP = self.input_country['SLP half life'].values[0]
        self.half_life_VSLP = self.input_country['VSLP half life'].values[0]
        self.half_life_slash = self.input_country['Slash half life'].values[0]
        self.half_life_root = self.input_country['Roots half life'].values[0]
        self.half_life_landfill = self.input_country['Landfill half life'].values[0]

        ### Slash parameters
        self.slash_burn = self.input_country['% of slash burned in the field'].values[0]
        self.slash_left = self.input_country['% of slash left to decay'].values[0]

    def setup_product_parameters(self):
        # Calculate annual wood demand/production and product pool breakdown
        # Product share ratio, depending on country input data
        self.product_share_slash_plantation = self.input_country['% slash plantation'].values[0]
        # Update 06/17/2021: split the slash rate into LLP, SLP, and VSLP.
        # Update 01/24/2022: determine which slash rate to use by using input parameter
        if self.slash_rate_mode == 'optimal':
            self.product_share_slash_secondary_llp = self.input_country['% slash optimal for LLP'].values[0]
            self.product_share_slash_secondary_slp = self.input_country['% slash optimal for SLP'].values[0]
            self.product_share_slash_secondary_vslp = self.input_country['% slash optimal for VSLP'].values[0]
        else: # secondary
            self.product_share_slash_secondary_llp = self.input_country['% slash secondary for LLP'].values[0]
            self.product_share_slash_secondary_slp = self.input_country['% slash secondary for SLP'].values[0]
            self.product_share_slash_secondary_vslp = self.input_country['% slash secondary for VSLP'].values[0]

        self.product_share_VSLP_thinning = self.input_country['% in VSLP thinning'].values[0]
        self.product_share_SLP_thinning = self.input_country['% in SLP thinning'].values[0]
        self.product_share_LLP_thinning = self.input_country['% in LLP thinning'].values[0]
        self.product_share_slash_thinning = self.input_country['% in slash thinning'].values[0]

        # Dry matter
        # This is to control whether the 2050 uses BAU demand level or 2010 level
        if self.future_demand_level == 'BAU':
            product_year = '2050'
        else:  # CST constant demand, 2010 level remain
            product_year = '2010'
        if self.vslp_input_control == 'WFL':
            SLP_2010 = 0
            SLP_2050 = 0
            LLP_2010 = 0
            LLP_2050 = 0
        else:
            SLP_2010 = self.input_country['SLP 2010'].values[0] * self.overbark_underbark_ratio
            SLP_2050 = self.input_country['SLP {}'.format(product_year)].values[0] * self.overbark_underbark_ratio
            LLP_2010 = self.input_country['LLP 2010'].values[0] * self.overbark_underbark_ratio
            LLP_2050 = self.input_country['LLP {}'.format(product_year)].values[0] * self.overbark_underbark_ratio

        ### Fifth scenario: "vslp_future_demand" is to control whether the 2050 uses 50% less WFL VSLP input scenario.
        # For fifth scenario, when fifth scenario is active.
        if self.vslp_future_demand == 'WFL50less':
            # BAU and including WFL. The 2010 uses current level, but 2050 has 50% reduction of the WFL compared to the BAU.
            if (self.vslp_input_control == 'ALL') & (self.future_demand_level == 'BAU'):
                # This is a default mode that only works with BAU and ALL wood: VSLP includes WFL. AND WFL is included as well
                VSLP_2010 = self.input_country['VSLP 2010'].values[0] * self.overbark_underbark_ratio
                VSLP_2050 = (self.input_country['VSLP-IND {}'.format(product_year)].values[0] + self.input_country['VSLP-WFL {}'.format(product_year)].values[0] * 0.5) * self.overbark_underbark_ratio
            # CST and including WFL. The 2010 and 2050 uses current level.
            elif (self.vslp_input_control == 'ALL') & (self.future_demand_level == 'CST'):
                # CST. The 2010 uses current level, and 2050 uses the same 2010 level. nothing changed. 50% less will not work.
                VSLP_2010 = self.input_country['VSLP 2010'].values[0] * self.overbark_underbark_ratio
                VSLP_2050 = self.input_country['VSLP {}'.format(product_year)].values[0] * self.overbark_underbark_ratio
            # Excluding WFL. When VSLP does not include WFL, then the 50% reduction does not work on the WFL at all
            elif self.vslp_input_control == 'IND':
                VSLP_2010 = self.input_country['VSLP-IND 2010'].values[0] * self.overbark_underbark_ratio
                VSLP_2050 = self.input_country['VSLP-IND {}'.format(product_year)].values[0] * self.overbark_underbark_ratio
            elif (self.vslp_input_control == 'WFL') & (self.future_demand_level == 'BAU'):
                VSLP_2010 = self.input_country['VSLP-WFL 2010'].values[0] * self.overbark_underbark_ratio
                VSLP_2050 = self.input_country['VSLP-WFL {}'.format(product_year)].values[0] * 0.5 * self.overbark_underbark_ratio
            elif (self.vslp_input_control == 'WFL') & (self.future_demand_level == 'CST'):
                VSLP_2010 = self.input_country['VSLP-WFL 2010'].values[0] * self.overbark_underbark_ratio
                VSLP_2050 = self.input_country['VSLP-WFL {}'.format(product_year)].values[0] * self.overbark_underbark_ratio
            else:
                VSLP_2010 = self.input_country['VSLP 2010'].values[0] * self.overbark_underbark_ratio
                VSLP_2050 = (self.input_country['VSLP-IND {}'.format(product_year)].values[0] + self.input_country['VSLP-WFL {}'.format(product_year)].values[0] * 0.5) * self.overbark_underbark_ratio

        # self.vslp_future_demand == 'default':  # For 1-4th scenario, not active.
        else:
            ## This is to control whether the VSLP includes WFL or not
            if self.vslp_input_control == 'ALL':  # This is a default mode: VSLP includes WFL.
                VSLP_2010 = self.input_country['VSLP 2010'].values[0] * self.overbark_underbark_ratio
                VSLP_2050 = self.input_country['VSLP {}'.format(product_year)].values[0] * self.overbark_underbark_ratio
            elif self.vslp_input_control == 'IND':  # This is industrial roundwood only for comparison purpose: VSLP excludes WFL.
                VSLP_2010 = self.input_country['VSLP-IND 2010'].values[0] * self.overbark_underbark_ratio
                VSLP_2050 = self.input_country['VSLP-IND {}'.format(product_year)].values[0] * self.overbark_underbark_ratio
            elif self.vslp_input_control == 'WFL':  # This is wood fuel only for comparison purpose: VSLP excludes WFL.
                VSLP_2010 = self.input_country['VSLP-WFL 2010'].values[0] * self.overbark_underbark_ratio
                VSLP_2050 = self.input_country['VSLP-WFL {}'.format(product_year)].values[0] * self.overbark_underbark_ratio
            else:
                VSLP_2010 = self.input_country['VSLP 2010'].values[0] * self.overbark_underbark_ratio
                VSLP_2050 = self.input_country['VSLP {}'.format(product_year)].values[0] * self.overbark_underbark_ratio

        # Create array of VSLP,SLP,LLP ratios AND quantities for every year. This is important because the ratios will change each year.
        # FIXME nyears how to define
        product_LLP, product_SLP, product_VSLP = [np.zeros((self.nyears)) for _ in range(3)]
        product_LLP[0], product_LLP[40] = LLP_2010, LLP_2050
        product_SLP[0], product_SLP[40] = SLP_2010, SLP_2050
        product_VSLP[0], product_VSLP[40] = VSLP_2010, VSLP_2050

        # Interpolate the production numbers: take the difference between the last and first year for each product pool, and divide by the number of years
        for year in range(1, len(product_VSLP)):
            # FIXME here this uses the nyears_product_demand = 40, which is quite obvious..., return to 40.
            # FIXME if one want to extend the demand or keep the latest demand.
            product_LLP[year] = product_LLP[0] + (product_LLP[40] - product_LLP[0]) / 40 * year
            product_SLP[year] = product_SLP[0] + (product_SLP[40] - product_SLP[0]) / 40 * year
            product_VSLP[year] = product_VSLP[0] + (product_VSLP[40] - product_VSLP[0]) / 40 * year


        # Create an array of the TOTAL wood products for each year (sum of LLP,SLP,VSLP).
        self.product_total = product_LLP + product_SLP + product_VSLP
        # Product numbers before accounting for slash
        self.product_share_LLP, self.product_share_SLP, self.product_share_VSLP = [product / self.product_total for product in
                                                                    (product_LLP, product_SLP, product_VSLP)]
        ### 06/17/2021: calculate weighted average slash rate in time series, based on the product quantity
        slash_LLP = product_LLP * self.product_share_slash_secondary_llp / (1 - self.product_share_slash_secondary_llp)
        slash_SLP = product_SLP * self.product_share_slash_secondary_slp / (1 - self.product_share_slash_secondary_slp)
        slash_VSLP = product_VSLP * self.product_share_slash_secondary_vslp / (1 - self.product_share_slash_secondary_vslp)
        slash_total = slash_LLP + slash_SLP + slash_VSLP
        self.product_share_slash_secondary_yearly = (slash_total / (self.product_total + slash_total))

    def setup_LLP_substitution(self):
        # LLP parameters
        self.llp_construct_ratio = self.input_country['% LLP for construction'].values[0]
        self.llp_displaced_CS_ratio = self.input_country['% LLP displacing concrete and steel'].values[0]
        CF_CO2_C = 44 / 12

        # Production emission substitution factor for LLP
        # net tC fossil energy saved per t carbon in wood use
        # Flag to determine calculated SUB factor or default, need to be consistent with the input excel file (w substitution)
        if self.substitution_mode == 'NOSUB':
            self.coef_construt_substitution = 0
        elif self.substitution_mode == 'constant': # Original, set up to the default 1.2 value
            # For example, 1.2 tC/tC means the 1.2 tC being saved if 1 tC is used.
            self.coef_construt_substitution = self.input_country['Emissions substitution factor for LLP (tC saved/tons C in LLP)'].values[0]
        else: # calculate SF from the excel file
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
            self.coef_construt_substitution = (saved_concrete_by_wooduse * EF_concrete + saved_steel_by_wooduse * EF_steel - 1 * EF_timber) / CF_CO2_C / self.carbon_wood_ratio

    def setup_VSLP_substitution(self):
        if self.substitution_mode == 'NOSUB':
            self.coef_bioenergy_substitution = 0
        else:
            self.coef_bioenergy_substitution = self.input_country['Emissions substitution factor for VSLP (tC saved/tons C in VSLP)'].values[0]

    def setup_misc(self):
        # Others
        # If user input exists, the highest level input. Set a physical limit
        if self.discount_rate_input is None:
            self.discount_rate = self.input_country['Discount rate'].values[0]
        elif (self.discount_rate_input>=0) & (self.discount_rate_input<=0.1):
            self.discount_rate = self.discount_rate_input
        # If it is out of physical limits:
        else:
            self.discount_rate = self.input_country['Discount rate'].values[0]
        self.landfill_methane_ratio = self.input_country['% of carbon in landfill converted to methane'].values[0]
        # This number is the quantity of fossil emissions(CO2) from production of a steel or concrete building minus the emissions from alterative construction of wood per kilogram of wood used

    def setup_time_period(self):
        """Time settings"""
        # Periods
        self.rotation_length_harvest = int(self.input_country['Rotation Period'].values[0])    # Rotation length for harvest
        self.rotation_length_thinning = int(self.input_country['Thinning period'].values[0])

    def setup_harvest_thinning_events(self):
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
                # include the end year to fix the issue that the thinning does not occur in the second rotation period
                year_index_harvest_end_year = self.year_index_harvest_plantation.tolist().copy()
                year_index_harvest_end_year.append(self.nyears)
                for cycle_harvest in range(len(year_index_harvest_end_year)-1):
                    year_index_thinning_in_cycle = np.arange(year_index_harvest_end_year[cycle_harvest], year_index_harvest_end_year[cycle_harvest + 1], self.rotation_length_thinning, dtype=int)
                    year_index_thinning_plantation.append(year_index_thinning_in_cycle.tolist())
                self.year_index_thinning_plantation = [item for sublist in year_index_thinning_plantation for item in sublist]

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


    def setup_harvest_slash_percentage(self):
        ### Step.0 Read in the harvest and thinning parameters.
        ## Harvest
        # Tree cover percentage, from 50% to 100% (100% will be zero tree cover area left in the stand pool)
        self.harvest_percentage_default = 1.0
        ## Thinning
        # For plantation or secondary conversion scenario
        self.thinning_percentage_default = self.input_country['% Removed in thinning plantation'].values[0]
        # For secondary regrowth scenario
        self.thinning_percentage_regrowth = self.input_country['% Removed in thinning regrowth'].values[0]

        ### Step.1 Harvest/slash percentage time series
        ## Initialization of time series array.
        # 1.1 Harvest percentage array. For plantation/conversion and regrowth, have the same length of year of growth.
        self.harvest_percentage_plantation = np.zeros((self.arraylength))
        self.harvest_percentage_regrowth = np.zeros((self.arraylength))

        # 1.2 Slash percentage when harvest or thinning
        slash_percentage_plantation = np.zeros((self.arraylength))
        # 06/17/2021 New slash rate for secondary forest, due to the varying product share from the annual product demand data inputs (different from stand level)
        # There are 2010-2050 41 rows for different wood demand data, and then column: nyears for years of growth.
        slash_percentage_secondary_conversion = np.zeros((self.nyears, self.arraylength))
        slash_percentage_secondary_regrowth = np.zeros((self.nyears, self.arraylength))

        ### Step.2 Assign the percentage to the event occurence year.
        ## 2.1 For plantation/conversion scenarios. They all have multiple harvests across the period of growth.
        # If there is thinning
        if (np.isnan(self.thinning_percentage_default) == False) & (self.thinning_percentage_default != 0) & (np.isnan(self.rotation_length_thinning) == False) & (self.rotation_length_thinning > 0):
            self.harvest_percentage_plantation[self.year_index_thinning_plantation] = self.thinning_percentage_default
            self.harvest_percentage_plantation[self.year_index_harvest_plantation] = self.harvest_percentage_default

            # Plantation slash does not change over years. All harvest is plantation slash.
            slash_percentage_plantation[self.year_index_thinning_plantation] = self.product_share_slash_thinning
            slash_percentage_plantation[self.year_index_harvest_plantation] = self.product_share_slash_plantation

            # The first harvest is secondary slash, the others are plantation slash
            # the weighted average slash rate change depending on the first harvest year
            # 07/01/2021 New array with different starting year of harvest: 41 row x 42 column. Use new axis to index two dimensions.
            slash_percentage_secondary_conversion[np.arange(self.nyears)[:, None], self.year_index_thinning_plantation] = self.product_share_slash_thinning
            slash_percentage_secondary_conversion[np.arange(self.nyears)[:, None], self.year_index_harvest_plantation] = self.product_share_slash_plantation
            slash_percentage_secondary_conversion[np.arange(self.nyears), 1] = self.product_share_slash_secondary_yearly

        else:  # Default: if there is no thinning
            self.harvest_percentage_plantation[self.year_index_harvest_plantation] = self.harvest_percentage_default
            slash_percentage_plantation[self.year_index_harvest_plantation] = self.product_share_slash_plantation
            # The first harvest is secondary slash, the others are plantation slash.
            # 07/01/2021 BUG FIXED: conversion slash rate is plantation slash rate
            # 07/01/2021 New array with different starting year of harvest: 41 row x 42 column. Use new axis to index two dimensions.
            slash_percentage_secondary_conversion[np.arange(self.nyears)[:, None], self.year_index_harvest_plantation] = self.product_share_slash_plantation
            slash_percentage_secondary_conversion[np.arange(self.nyears), 1] = self.product_share_slash_secondary_yearly

        ## 2.2 For regrowth scenario, only one harvest at the beginning of the year start for PDV.
        self.year_index_harvest_regrowth = [1]
        # If there is a thinning
        if (np.isnan(self.thinning_percentage_regrowth) == False) & (self.thinning_percentage_regrowth != 0) & (np.isnan(self.rotation_length_thinning) == False) & (self.rotation_length_thinning > 0):
            self.year_index_thinning_regrowth = np.arange(1, self.arraylength, self.rotation_length_thinning, dtype=int)
            # Include the first harvest
            self.year_index_both_regrowth = sorted(list(set(self.year_index_harvest_regrowth) | set(self.year_index_thinning_regrowth)))
            self.ncycles_regrowth = len(self.year_index_both_regrowth)

            self.harvest_percentage_regrowth[self.year_index_thinning_regrowth] = self.thinning_percentage_regrowth
            self.harvest_percentage_regrowth[self.year_index_harvest_regrowth] = self.harvest_percentage_default

            # The first harvest is secondary slash, remove following harvests
            # 07/01/2021 New array with different starting year of harvest: 41 row x 42 column. Use new axis to index two dimensions.
            slash_percentage_secondary_regrowth[np.arange(self.nyears)[:, None], self.year_index_thinning_regrowth] = self.product_share_slash_thinning
            slash_percentage_secondary_regrowth[np.arange(self.nyears), 1] = self.product_share_slash_secondary_yearly

        else:  # Default: if there is no thinning
            self.year_index_both_regrowth = self.year_index_harvest_regrowth
            self.harvest_percentage_regrowth[self.year_index_harvest_regrowth] = self.harvest_percentage_default
            self.ncycles_regrowth = len(self.year_index_both_regrowth)
            # The first harvest is secondary slash, remove following harvests
            # 07/01/2021 New array with different starting year of harvest: 41 row x 42 column. Use new axis to index two dimensions.
            slash_percentage_secondary_regrowth[np.arange(self.nyears), 1] = self.product_share_slash_secondary_yearly

        ### Step.3 To get the staggered array for slash percentage
        def staircase(array):
            # Piecewise array for aboveground biomass actually harvested/thinned during rotation harvest/thinning
            outarray = np.zeros(array.shape)
            if len(array.shape) == 1:
                df = pd.DataFrame(array)
                outarray = df.replace(to_replace=0, method='ffill').values.reshape(array.shape)
            else: # array.shape = 2
                for row in range(array.shape[0]):
                    df = pd.DataFrame(array[row, :])
                    outarray[row, :] = df.replace(to_replace=0, value=None, method='ffill').values.reshape(array.shape[1])
            return outarray

        self.slash_percentage_plantation, self.slash_percentage_secondary_conversion, self.slash_percentage_secondary_regrowth = [staircase(slash_percentage) for slash_percentage in [slash_percentage_plantation, slash_percentage_secondary_conversion, slash_percentage_secondary_regrowth]]


