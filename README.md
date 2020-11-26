# Super Smash Bros Ultimate Player Seeding
### Automated Player Seeding by Win-rate:

This repo contains a script to seed players in SSBU based on average win rates.
These average win rates are calculated based on results in [Smashdata.gg](https://smashdata.gg/smash/ultimate/player/MkLeo).

There is a web based version of code created by L4st found [here](http://smashseeder.telic.us/). This makes initial seeding much easier for larger
tournaments.

### Requirements
#### Software
- Python 3.7+

 **Key packages**
  - Numpy == 1.19.1
  - Pandas >= 1.1.1
  - graphqlclient >= 0.2.4
  - yaml >= 0.2.5

 **Other packages**    
  - sqlite >= 3.33.0
  - json >= 2.0.9

#### Smash.gg Info
- [Smashdata.gg](https://github.com/smashdata/ThePlayerDatabase) Database
- [Smash.gg Token](https://developer.smash.gg/docs/authentication)
- Tournament Phase Id Number

### Winrate Seeder Setup:

1. Clone or download this repository.
2. Download and install Python 3.7 or greater and the required libraries. For help, see ***Python Setup Guide*** below
3. Download the Smashdata.gg Player Database (updated ~biweekly) and place in repository root folder
4. Request and generate a smash.gg Token (Do not lose your key)
5. Add your key to the **auth.yaml** file in the **key** folder and remove the "#" in front of the key
6. Open **Winrate_Seeder.py** and enter a tourney *Phase_Id* and *Event_Name* in the *User Inputs* section
7. Run the code. This will generate a .csv file in the **seeding** folder
8. Use [Seed Uploader](https://gg-seed-upload.herokuapp.com/) to upload seeds

***

### Python Setup Guide
In order to run the Winrate Seeder, you need a version of python as well as a text editor.

I recommend [Sublime Text 3](https://www.sublimetext.com/3) for the text editor. [Atom](https://atom.io/) is another good editor

#### Python Setup
1. Install python:
  - Open Command Prompt and type "python".
    - **If you don't have python:** This should open the Microsoft Windows Store to the python app. Download it.
    - **If you have python:** A python terminal should open in the Command Prompt.
2. Install Packages:
  - Open a new command prompt or type "quit()" to exit python terminal
  - Type "pip help" to verify you have pip. This should open a command list
  - Install packages by typing:
      - "pip install **numpy==1.19.1**"
      - "pip install **pandas**"
      - "pip install **graphqlclient**"
      - "pip install **pyyaml**"
3. Install Sublime Text 3
  - Install Sublime 3
  - Go to Tools > Build System and select Python
  - Test python runs through Sublime Text
    - Create a file called "test.py"
    - In the file type "print('hello world')"
    - Press "Ctrl+B" to run test.py
    - A popup at the bottom should show "hello world"

Once these steps are complete you have a working installation of python and text editor on your computer. You can continue to follow the steps for Winrate_Seeder.
