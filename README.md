# Carbon HARvest Model (CHARM)

[//]: # ([![DOI]&#40;https://zenodo.org/badge/DOI/10.1038/s41586-023-06187-1.svg&#41;]&#40;https://doi.org/10.1038/s41586-023-06187-1&#41;)

[//]: # ([![Github downloads]&#40;https://img.shields.io/github/downloads/wri/charm-global-level/total.svg&#41;]&#40;&#41;)

## Contents

- [Overview](#Overview)
- [Download](#Download)
- [Installation](#Installation)
- [Usage](#Usage)
- [Results analysis](#Results-analysis)
- [Copyright and License](#Copyright-and-License)
- [Citation](#Citation)

## Overview

CHARM is a biophysical model that estimates the GHG consequences and land-use requirements to meet wood consumption levels. It is developed by the World Resources Institute Food and Forest Program. 

CHARM starts with existing wood sources and demands as of the year 2010. The model uses estimates of three major wood product categories of consumption by country to estimate harvest levels.
The model tracks the carbon consequences of harvesting these forests under allocation and regrowth management rules specified by the scenario.
It separates wood supplied by existing plantation forests and that supplied by secondary forests, each based on their harvest efficiencies and growth rates. 
Land requirements are the quantity of wood generated per hectare at the estimated efficiencies by country at present levels, assuming all hectares affected are clear-cut 

## Download

Download and prepare the scripts and data files in your computer. Create a new model folder in your computer (default model folder name is **charm-global-level**, but you can make your own one). Copy all the necessary files to this folder so that it includes:

- requirements.txt
- README.md

./src/models/
- Driver.py
- Global_by_country.py
- Secondary_regrowth_scnenario.py
- Secondary_mature_regrowth_scnenario.py
- Secondary_conversion_scenario.py
- Plantation_counterfactual_secondary_plantation_age_scenario.py
- Agricultural_land_tropical_scenario.py
- Land_area_calculator.py
- Carbon_cost_calculator.py
- Tropical_new_plantation_calculator.py

./src/analysis/
- results_summary_analysis.py
- visualize.py

./data/processed/
- CHARM global - YR_40 - DR_4p - V20230125.xlsx


## Installation

1. Check if Python3 is installed on your computer.

    On Windows, open [command prompt](https://www.howtogeek.com/235101/10-ways-to-open-the-command-prompt-in-windows-10/) or [Windows Powershell](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/powershell), type **python** and hit enter. (This documentation uses Windows as an example)

    On Mac OSX or Linux, open [Terminal](https://macpaw.com/how-to/use-terminal-on-mac#:~:text=How%20to%20open%20Terminal%20on,double%2Dclick%20the%20search%20result.), type **python** and hit enter.

    If Python is installed and configured to PATH correctly, it will start up shortly. The first line will tell which version of Python is installed. Python 3.X.X means Python3, and Python 2.X.X means Python2. If Python successfully launched, skip to the next section.

    ```powershell
    C:\Users\USERNAME>python
    Python 3.7.3 (default, Apr 24 2019, 15:29:51) [MSC v.1915 64 bit (AMD64)] on win32
    Type "help", "copyright", "credits" or "license" for more information.
    >>>
    ```

    If the above did not show up successfully or it showed the Python2 version, please install latest Python3 from [here](https://www.python.org/downloads/) and then verify again as above.

2. Check if python package manager [pip](https://pip.pypa.io/en/stable/) is installed on your computer.

    ```powershell
    C:\Users\USERNAME>python -m pip --version
    pip 19.1.1 from C:\Users\USERNAME\AppData\Local\Programs\python\python37\lib\site-packages\pip (python 3.7)
    ```

    If pip is installed, you should see above message, otherwise install pip following the instructions [here](https://pip.pypa.io/en/stable/installing/). After installation, upgrade pip to the latest version:

    ```powershell
    C:\Users\USERNAME>python -m pip install -U pip
    ```

3. Install required Python packages.

    In the command prompt/Powershell (Windows) or Terminal (OSX/Linux), use **cd** to change directory to the model folder location. Use **pip** to install required python packages. This should take a few minutes to install the packages.

    ```powershell
    C:\Users\USERNAME>cd C:\Users\USERNAME\Documents\charm-global-level\
    C:\Users\USERNAME\Documents\charm-global-level>pip install -r requirements.txt
    ```

## Usage

1. Check the data file

    Make sure the current sample data file **CHARM global - YR_40 - DR_4p - V20230125.xlsx** is under the ./data/processed/ directory. The current sample file consists of model outputs; running the model will overwrite the existing outputs.

2. Review the input parameters

    Open the **CHARM global - YR_40 - DR_4p - V20230125.xlsx** and click on *Inputs* tab. We provide the country name and ISO in columns A and B and input associated parameters in the same row (columns C:AY).

3. Edit the input parameters and the filename

    Everytime you change the parameters for a model experiment, you should change the version name in the filename to avoid overwriting. We currently have the version name in the format of "YYYYMMDD", but you can create other names.
    We change "YR_XX" in the filename based on the years of growth (e.g., YR_40 means 40 years of growth), and "DR_XX" based on different discount rates (e.g., DR_4p means 4% discount rate). 

4. Run the model - Single Run option
    
    The main script **./src/models/Driver.py** can run CHARM under different discount rates and years of growth. If you want to run one single experiment (one data file), in the Driver.py, uncomment the line of "run_model_all_scenarios()" under the Local run (single run) section:

    ```python
    if __name__ == "__main__":
        ##################### Local run (single run) ########################
        # Uncomment the line below to run the script without input arguments
        run_model_all_scenarios('40', '4p', '20230125', root)
    ```
    
    Make sure you have changed the location to the model folder, then type the following:

    ```powershell
    C:\Users\USERNAME\Documents\charm-global-level\src\models>python Driver.py
    ```
    Running one full model run (including all seven scenarios) takes about 0.5-1.5 hours depending on the computational power.

5. Run the model - Serial Run option

    We provide a serial run option through command line for advanced users. Here are the argument options available: 

    | Arg Option  | Description                               | Value          |
    |-------------------------------------------|----------------|-----------|
    | --run-main        | Determine if it is a main model run | True/Yes/1     |
    | --run-sensitivity | Determine if it is a sensitivity run | True/Yes/1     |
    | --years-growth    | The number of years of growth  | e.g. 40        |                              |
    | --discount-rate        | The discount rate | e.g. 4p        |
    | --path        | The root path of running the model | user directory |


6. Check the outputs

    The model outputs are updated in CHARM global - YR_40 - DR_4p - V20230125.xlsx. The tab name is based on there experiment input parameters. 
    
    1. future wood demand level
        - BAU (Bussiness-as-usual)
        - CST (Constant demand level as 2010)
    2. substitution benefit mode
        - SUBON (including substitution)
        - NOSUB (excluding substitution)
    3. VSLP input control
        - ALL (total roundwood)
        - IND (industrial roundwood)
        - WFL (wood fuel)
    
    A non-exhaustive list of output variables.
    
    >The present discounted values of carbon benefit per hectare for different policy decisions
   
    | Variable | Harvest scenario                          |
    |-------------------------------------------|-----------|
    | PDV per ha Secondary regrowth (tC/ha) | Secondary forest regrowth                 |
    | PDV per ha Secondary conversion (tC/ha) | Secondary forest conversion to plantation |
    | PDV per ha Plantation secondary plantation age (tC/ha) | Plantation                                |
    
    >Meta statistics 
    
    | Variable | Description |
    |-----------|-----------|
    | Default: Plantation supply wood (mega tC) | wood supply from plantation |
    | Default: Secondary forest supply wood (mega tC) | wood supply from secondary forest |
    | Plantation area (ha) | land area required for plantation |
    
    >Scenarios

    | Variable                           | Description                                                                                                               |
    |---------------------------------------------------------------------------------------------------------------------------|-----------|
    | S1 regrowth: total PDV (mega tC)   | Total carbon consequences of the plantation harvested plus some secondary forest regrowth after a harvest                 |
    | S1 regrowth: Secondary area (ha)   | Secondary forest area required for S1                                                                                     |
    | S2 conversion: total PDV (mega tC) | Total carbon consequences of the plantation harvested plus some secondary forest converted to plantations                 |
    | S2 conversion: Secondary area (ha) | Secondary forest area required for S2                                                                                     |
    | S3 mixture: total PDV (mega tC)   | Total carbon consequences of the plantation harvested plus some young/old mixed secondary forest regrowth after a harvest |
    | S3 mixture: Secondary area (ha)   | Secondary forest area required for S3                                                                                     |
    | S4 125% GR: total PDV (mega tC) | Total carbon consequences of S1, except with higher productivity in existing plantations                                  |
    | S4 125% GR: Secondary area (ha) | Secondary forest area required for S4                                                                                     |
    | S5 62% SL: total PDV (mega tC)   | Total carbon consequences of S1, except with increased harvest efficiency of tropical forests                             |
    | S5 62% SL: Secondary area (ha)   | Secondary forest area required for S5                                                                                     |
    | S6 WFL 50% less: total PDV (mega tC) | Total carbon consequences of S1, except with reduced wood fuel demand in 2050                                             |
    | S6 WFL 50% less: Secondary area (ha) | Secondary forest area required for S6                                                                                     |

## Results analysis

1. Global level summary

   We use ./src/analysis/results_summary_analysis.py to calculate the total carbon costs and land use of global forestry for seven scenarios, as described in our paper and report. The summary file CHARM_global_carbon_land_summary - YR_XX - VYYYYMMDD.xlsx will be generated under the ./data/processed/derivative/ folder.

2. Visualization

   We use ./src/analysis/visualize.py to produce the figures in our paper and report. 


## Copyright and License

Copyright (c) 2023 [World Resources Institute](https://www.wri.org/), The Carbon Harvest Model (CHARM) Project

Author & Maintainer: Liqing Peng (liqing.peng@wri.org)

Contributors: WRI Food & Agriculture Team - Liqing Peng, Tim Searchinger, Jessica Zionts, Richard Waite

This software is made available under the [The MIT License (MIT)](https://mit-license.org/) and under no other licenses.
A copy of the license is available in the `LICENSE` file at the root of this repository.
World Resources Institute believes in the open and transparent exchange of information and strives to embody this value in our analyses and knowledge products.


## Citation
