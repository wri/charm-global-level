# CHARM

CHARM (Carbon Harvest Model) is a timber carbon tracker model developed by the World Resources Institute Food and Forest Program. It analyzes future changes in timber demand and their effects on land use and carbon stocks under various policy decision scenarios.

## Copyright and License

Copyright (c) 2023 [World Resources Institute](https://www.wri.org/), The Carbon Harvest Model (CHARM) Project

Author & Maintainer: Liqing Peng (liqing.peng@wri.org)

Contributors: WRI Food Team - Liqing Peng, Jessica Zionts, Tim Searchinger, Richard Waite

This software is made available under the [The MIT License (MIT)](https://mit-license.org/) and under no other licenses.
A copy of the license is available in the `LICENSE` file at the root of this repository.
World Resources Institute believes in the open and transparent exchange of information and strives to embody this value in our analyses and knowledge products.


## Download

Download and prepare the scripts and data files in your computer. Create a new model folder in your computer (default model folder name is **charm-regional-level**, but you can make your own one). Copy all the necessary files to this folder so that it includes:

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
- results_summary_analysis.py

./data/processed/
- CHARM regional - YR_40 - DR_4p - V20230125.xlsx


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
    C:\Users\USERNAME>cd C:\Users\USERNAME\Documents\charm-regional-level\
    C:\Users\USERNAME\Documents\charm-regional-level>pip install -r requirements.txt
    ```

## Usage

1. Check the data file

    Make sure the current sample data file **CHARM regional - YR_40 - DR_4p - V20230125.xlsx** is under the ./data/processed/ directory. The current sample file consists of model outputs; running the model will overwrite the existing outputs.

2. Review the input parameters

    Open the **CHARM regional - YR_40 - DR_4p - V20230125.xlsx** and click on *Inputs* tab. We provide the country name and ISO in columns A and B and input associated parameters in the same row (columns C:AY).

3. Edit the input parameters and the filename

    Everytime you change the parameters for a model experiment, you should change the version name in the filename to avoid overwriting. We currently have the version name in the format of "YYYYMMDD", but you can create other names.
    We change "YR_XX" in the filename based on the years of growth (e.g., YR_40 means 40 years), and "DR_XX" based on different discount rates (e.g., DR_4p means 4% discount rate). 

4. Run the model - Single Run option
    
    If you want to run one single experiment (one data file), uncomment the line of "run_model_all_scnearios()" under the Local run (single run) section:

    ```python
    if __name__ == "__main__":
        ##################### Local run (single run) ########################
        run_model_all_scenarios('40', '4p', '20230125', root)
    ```
    
    Make sure you have changed the location to the model folder, then type the following:

    ```powershell
    C:\Users\USERNAME\Documents\charm-regional-level\src\models>python Driver.py
    ```
    Running one full model run (including all seven scenarios) takes about 1-2 hours depending on the computational power.

5. Run the model - Serial Run option

    We provide a serial run option through command line for advanced users. Here are the argument options available: 

    | Arg Option  | Description                               | Value          |
    |-------------------------------------------|----------------|-----------|
    | --run-main        | Determine if it is a main model run | True/Yes/1     |
    | --run-sensitivity | Determine if it is a sensitivity run | True/Yes/1     |
    | --years-growth    | The number of years of growth  | e.g. 40        |                              |
    | --discount-rate        | The discount rate | e.g. 4p        |
    | --path        | The root path of running the model | user directory |


6. Check the results

    The results are updated in CHARM regional - YR_40 - DR_4p - V20230125.xlsx. The tab name is based on there experiment input parameters. 
    
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
