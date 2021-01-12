# CHarM

CHarM (Carbon Harvest Model) is a timber carbon tracker model developed by the World Resources Institute Food and Forest Program. It analyzes future changes in timber demand and their effects on land use and carbon stocks under various policy decision scenarios.

## Download

Download and prepare the scripts and data files in your computer. Create a new model folder in your computer (default model folder name is **CHARM_STAND**, but you can make your own one). Copy all the necessary files to this folder so that it includes:

- Driver_stand.py
- Global_stand.py
- Plantation.py
- Secondary_conversion.py
- Secondary_regrowth.py
- Pasture_zero_counterfactual.py
- Pasture_with_counterfactual.py
- CHarM.xlsx
- requirements.txt
- README.md

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
    C:\Users\USERNAME>cd C:\Users\USERNAME\Documents\CHARM_STAND\
    C:\Users\USERNAME\Documents\CHARM_STAND>pip install -r requirements.txt
    ```

## Usage

1. Edit the input parameters

    Open the **CHarM.xlsx** and click on *Inputs* tab. Define scenario name and its abbreviation in columns A and B and input associated parameters in the same row (columns C:AL).

    We provide two country examples Brazil and Austria in this tab. You can modify these examples or simply add the new scenarios below. More country average parameters are also available in the *Samples* tab. You can directly copy a row of parameters from *Samples* to *Inputs*.

    **Note that all the parameters from columns C:AL are required, except for column AI, which is a calculated value.** If you copy the values of an entire row from *Samples* to *Inputs*, and if you modify the parameters within AD:AH, this value in column AI will not update in the excel file. It will not affect the model run, but to make sure it will update and link to your changes in the excel file, you should drag the calculation from AI3 and apply to this copied row.

2. Run the model

    Make sure you have changed the location to the model folder, then type the following:

    ```powershell
    C:\Users\USERNAME\Documents\CHARM_STAND>python Driver_stand.py
    ```

3. Check the results

    The results are updated in CHarM.xlsx *Outputs*. They include the present discounted values of carbon benefit per hectare for five policy decisions:
    - Decision: Plantation, Counterfactual: start from free land and grow back
    - Decision: Secondary forest conversion to plantation, Counterfactual: start from old growth forest and grow
    - Decision: Secondary forest regrowth, Counterfactual: start from old growth forest and grow back
    - Decision: Pasture conversion to plantation, Counterfactual: free land
    - Decision: Pasture conversion to plantation, Counterfactual: start from free land forest and grow back

    The carbon stock dynamics for different pools in the decision and counterfactual groups are printed in the subfolder *Results/*. Each scenario is exported as a png file and named by its abbreviation (column B).

## License

Copyright (C) 2020 [WRI](https://www.wri.org/), The Carbon Harvest Model (CHarM) Project

Contributor: WRI Food Team - Liqing Peng, Jessica Zionts, Tim Searchinger, Richard Waite

Maintainer: Liqing Peng (liqing.peng@wri.org)
