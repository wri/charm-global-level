# CHarM

CHarM (Carbon Harvest Model) is a timber carbon tracker model developed by the World Resources Institute Food and Forest Program. It analyzes future changes in timber demand and their effects on land use and carbon stocks under various policy decision scenarios.

## Copyright and License

Copyright (c) 2020-2021 [World Resources Institute](https://www.wri.org/), The Carbon Harvest Model (CHarM) Project

Author & Maintainer: Liqing Peng (liqing.peng@wri.org)

Contributors: WRI Food Team - Liqing Peng, Jessica Zionts, Tim Searchinger, Richard Waite

This software is made available under the [Polyform Strict License 1.0.0](https://polyformproject.org/licenses/strict/1.0.0/) and under no other licenses.
A copy of the license is available in the `LICENSE` file at the root of this repository.

In the future, it is possible the software will be made available under different terms at the author's discretion.
World Resources Institute believes in the open and transparent exchange of information and strives to embody this value in our analyses and knowledge products.


## Download

Download and prepare the scripts and data files in your computer. Create a new model folder in your computer (default model folder name is **charm-regional-level-clean**, but you can make your own one). Copy all the necessary files to this folder so that it includes:

- requirements.txt
- README.md

./src/models/
- Driver_regional.py
- Global_by_country.py
- Secondary_regrowth_scnenario.py
- Secondary_mature_regrowth_scnenario.py
- Secondary_conversion_scenario.py
- Plantation_counterfactual_secondary_plantation_age_scenario.py
- Land_area_calculator.py

./data/processed/
- CHARM_global.xlsx


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

    In the command prompt/Powershell (Windows) or Terminal (OSX/Linux), use **cd** to change directory to the model folder location. Use **pip** to install required python packages.

    ```powershell
    C:\Users\USERNAME>cd C:\Users\USERNAME\Documents\charm-regional-level-clean\
    C:\Users\USERNAME\Documents\charm-regional-level-clean>pip install -r requirements.txt
    ```

## Usage

1. Check the data file

    Make sure the current data file **CHARM_global.xlsx** is under the ./data/processed/ directory. You can save the previous model results by changing their names, for example, **CHARM_global_11012021.xlsx**, to avoid overwriting.

2. Review or edit the input parameters

    Open the **CHARM_global.xlsx** and click on *Inputs* tab. We provide the country name and ISO in columns A and B and input associated parameters in the same row (columns C:AY).

3. Run the model

    Make sure you have changed the location to the model folder, then type the following:

    ```powershell
    C:\Users\USERNAME\Documents\charm-regional-level-clean\src\models>python Driver_regional.py
    ```

3.  Check the results

    The results are updated in CHARM_global.xlsx. The tab name is based on there experiment input parameters. 
    
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
   
    | Variable | Decison|
    |-----------|-----------|
    | PDV per ha Secondary regrowth (tC/ha) | Secondary forest regrowth|
    | PDV per ha Secondary conversion (tC/ha) | Secondary forest conversion to plantation|
    | PDV per ha Plantation secondary plantation age (tC/ha) | Plantation|
    
    >Meta statistics 
    
    | Variable | Description |
    |-----------|-----------|
    | Default: Plantation supply wood (mega tC) | wood supply from plantation |
    | Default: Secondary forest supply wood (mega tC) | wood supply from secondary forest |
    | Plantation area (ha) | land area required for plantation |
    
    >Scenarios

    | Variable | Description |
    |-----------|-----------|
    |S1 regrowth: total PDV (mega tC)|Total carbon consequences of the plantation harvested plus some secondary forest regrowth after a harvest|
    |S1 regrowth: Secondary area (ha)|Secondary forest area required for S1|
    |S2 conversion: total PDV (mega tC)|Total carbon consequences of the plantation harvested plus some secondary forest converted to plantations|
    |S2 conversion: Secondary area (ha)|Secondary forest area required for S2|

