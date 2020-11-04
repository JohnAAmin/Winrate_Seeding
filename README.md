# Super Smash Bros Ultimate Player Seeding
### Automated Player Seeding by Win-rate:

This repo contains a script to seed players in SSBU based on average win rates.
These average win rates are calculated based on results in [Smashdata.gg](https://smashdata.gg/smash/ultimate/player/MkLeo).

There is a web based version of code created by L4st found [here](http://smashseeder.telic.us/). This makes initial seeding much easier for larger
tournaments.

### Requirements
#### Software
- Python 3.7
  - Pandas >= 1.1.1
  - sqlite >= 3.33.0
  - graphqlclient >= 0.2.4
  - yaml >= 0.2.5
  - json >= 2.0.9

#### Smash.gg Info
- [Smashdata.gg](https://github.com/smashdata/ThePlayerDatabase) Database
- [Smash.gg Token](https://developer.smash.gg/docs/authentication)
- Tournament Phase Id Number

### Setup:

1. Clone or download this repository.
1. Download and install Python 3.7 or greater and the required libraries
1. Download the Smashdata.gg Player Database (updated ~biweekly) and place in repository root folder
1. Request and generate a smash.gg Token (Do not lose your key)
1. Add your key to the **auth.yaml** file in the **key** folder
1. Open **Winrate_Seeder.py** and enter a tourney *Phase_Id* and *Event_Name* in the *User Inputs* section
1. Run the code. This will generate a .csv file in the **seeding** folder
1. Upload the seeds [here](https://gg-seed-upload.herokuapp.com/)
