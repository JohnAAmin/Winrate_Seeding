
"""
                                Winrate Seeder
@authors: J4m
@version: 2.0

This code query's a Smash.gg Tournament corresponding to a given Phase Id.
It takes all the entrants in that phase, grabbing Seed Number, Seeding Id,
Player Id, and Gamer tag.

The code then queries the Smashdata SQLite database to obtain player Win Rates
and Total Set counts.

Finally it then Exports all this data as an Excel Spreadsheet.

USER INPUTS:
    Phase_Id         [int]  - The Phase Id of Players Needed to be seeded
    Event_Name       [str]  - The Name of the event (for file naming purposes)
    Update_Bracket   [bool] - Updates seeds on Smash.GG automatically
"""

###############################################################################
# USER INPUTS

Phase_Id = 883778           # number 88####
Event_Name = 'Peak_66'      # 'Your File Name'
Update_Bracket = False      # True or False
###############################################################################
# IMPORTS

import os,sys,yaml
import time as t
import numpy as np
import pandas as pd
import json as js
import sqlite3
from graphqlclient import GraphQLClient as GQL

###############################################################################
# DEFS

def Smash_Api(*path):
    ''' Opens Auth.yaml and starts GraphQL client '''
    if not path:
        path = os.getcwd() + '/key'
    elif len(path) == 1:
        path = path[0]
    else:
        print('ERROR: Too many arguments')
        sys.exit(0)
    # Finds and reads auth.yaml file
    x = path + '/auth.yaml'
    with open(x) as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
        authToken = data.get('authkey')

    # Starts GraphQL file
    client = GQL('https://api.smash.gg/gql/' + 'alpha')
    client.inject_token('Bearer ' + authToken)

    return client
#-----------------------------------------------------------------------------#

def Tourney_Players(client, phaseId):
    'Collects player seeding information and returns a Dataframe of entrants'

    # Setting Up Dataframe
    cols = ['Seed ID','Player ID','Phase Seed','Player']
    seeding_df = pd.DataFrame(columns=cols)

    # Iterate through API request
    running = True
    page = 1
    player_list = []

    while running:
        standings = client.execute('''
                    query PhaseSeeds($phaseId: ID!, $page: Int!) {
                    phase(id:$phaseId) {seeds(
                    query:{perPage: 256, page:$page})
                    {pageInfo {total} nodes {
                    id seedNum entrant {participants
                    {player{gamerTag id}}}}}}}
                    ''',{"phaseId": phaseId, "page": page})

        standingsData = js.loads(standings)
        players = standingsData['data']['phase']['seeds']['nodes']
        if not players:
            running = False
        else:
            player_list += players
            page += 1
    bracket_size = len(player_list)

    # Fills in the Dataframe
    for i in range(bracket_size):
        Seed_Id = player_list[i]['id']
        Seed_Num = '' #player_list[i]['seedNum']
        Player_Id = player_list[i]['entrant']['participants'][0]['player']['id']
        Gamer_Tag = player_list[i]['entrant']['participants'][0]['player']['gamerTag']
        seeding_df.loc[i] = [Seed_Id, Player_Id, Seed_Num, Gamer_Tag]

    return seeding_df

#-----------------------------------------------------------------------------#

def Win_Rate(con, player_id, tag, zeros, base):
    'Searches Smashdata Database for Player Set Win-Rate'

    # Searches Smashdata SQLite database
    cur = con.cursor()
    A = '''SELECT COUNT(*) FROM 'sets' WHERE (p1_id={} OR p2_id={})
           AND (p1_score>=0 AND p2_score>=0)'''.format(player_id, player_id)
    B = '''SELECT COUNT(*) FROM 'sets' WHERE (winner_id={})
           AND (p1_score>=0 AND p2_score>=0)'''.format(player_id)

    cur.execute(A)
    All = cur.fetchone()[0]
    cur.execute(B)
    Win = cur.fetchone()[0]

    # Calculates Win Rate
    if All == 0:

        Win_Rate = 0
        Link = '-'
        zeros += 1
    else:
        Win_Rate = round((Win/All),3)
        x = tag.replace(' ', '%20') #fixes spaces in names
        Link = base + x + '?id=' + str(player_id)

    return [Win_Rate, All, Link, zeros]
#-----------------------------------------------------------------------------#
def Update_GG(update_bracket, client, phaseId, seeds):
        # Updates the Smash.gg player seeds
    if update_bracket:
        print('Seeds Assigned')
        print('Updating Smash.gg:')

        seeds['Phase Seed'] = np.arange(1, len(seeds)+1)
        seedMapping = []
        for i in range(len(seeds)):
            seedId = str(seeds.loc[i,'Seed ID'])
            phaseSeed = str(seeds.loc[i,'Phase Seed'])
            seedMapping.append({'seedId': seedId, 'seedNum': phaseSeed})

        result = client.execute('''
                 mutation UpdatePhaseSeeding
                 ($phaseId: ID!, $seedMapping: [UpdatePhaseSeedInfo]!) {
                 updatePhaseSeeding (phaseId: $phaseId, seedMapping: $seedMapping) {
                     id}}''',{"phaseId": phaseId, "seedMapping": seedMapping})

        resData = js.loads(result)
        if 'errors' in resData:
            print('Error:')
            print(resData['errors'])
            print(phaseId)
        else:
            print('Success!')
    else:
        print('Seeds Assigned')
        print('NOT updating smash.gg')

#-----------------------------------------------------------------------------#

def Check_Type(client, phaseId):
    'Checks if event is for Ultimate, Melee, or Smash4'
    try:
        game = client.execute('''
                        query PhaseSeeds($phaseId: ID!) {
                        phase(id:$phaseId){event{name type 
                        videogame {id}}}}''',{"phaseId": phaseId})
        gameData = js.loads(game)
    except:
        return (False, 'Bad API Key: Check Auth.yaml') 
    
    try:
        gameName = gameData['data']['phase']['event']['name']
        gameType = gameData['data']['phase']['event']['type']
        gameNumber = gameData['data']['phase']['event']['videogame']['id']
        
        if gameNumber == 1 and gameType == 1:
            db = 'database/melee_player_database.db'
            base = 'https://smashdata.gg/smash/melee/player/'
        elif gameNumber == 3 and gameType == 1:
            db = 'database/smash4_player_database.db'
            base = 'https://smashdata.gg/smash/4/player/'
        elif gameNumber == 1386 and gameType == 1:
            db = 'database/ultimate_player_database.db'
            base = 'https://smashdata.gg/smash/ultimate/player/'
        else:
            return (False, 'Bad Phase: Must be Singles')   
        
        return(True, gameName, db, base)
    
    except:
        return (False, 'Bad Phase: Check Number')   
    
#-----------------------------------------------------------------------------#

def main(Phase_Id, Event_Name):
    'Runs all helper functions to produce seeding csv spreadsheet'


# Starts API client and collects players from Phase Id
    print("Checking API Key")
    client = Smash_Api()
    
    gameData = Check_Type(client, Phase_Id)
    
    if not gameData[0]:
        print(gameData[1])
        print('Exiting Seeder')
        sys.exit(0)
    
    print("Collecting players in event: {}".format(gameData[1]))
    seeding_df = Tourney_Players(client, Phase_Id)

# Specifies and opens Smashdata SQLite database
    db = gameData[2]
    base = gameData[3]
    
    con= sqlite3.connect(db)
# Adds Win Rate and Set Count to Dataframe
    print("Collecting Win Rates and Set Counts")
    t0 = t.time()
    count = 0
    zeros = 0
    seeding_df['Win Rate'] = '-'
    seeding_df['Sets'] = '-'
    seeding_df['Link'] = '-'

    for i in range(len(seeding_df)):
        gamer_tag = seeding_df.loc[i, 'Player']
        player_id = seeding_df.loc[i, 'Player ID']
        wr, sets, link, zeros = Win_Rate(con, player_id, gamer_tag, zeros, base)
        seeding_df.loc[i, 'Win Rate'] = wr
        seeding_df.loc[i, 'Sets'] = sets
        seeding_df.loc[i, 'Link'] = link
        count += 1
        # Progress Notes
        if (count % 10) == 0:
            print('    Finished Player: {}'.format(count))

    con.close()
    print('Win Rates and Set Counts Collected')

# Calculates Stats
    t1 = t.time()
    tx = round((t1-t0),2)
    rate = round((tx/count),3)

    print("""
    - - - - - - - - - - -
     Time: {} s
     Rate: {} S/player
     Player Count: {}
     No Data: {}
    - - - - - - - - - - -
     """.format(tx, rate, count, zeros))

    seeding_df = seeding_df.sort_values(by=['Win Rate', 'Sets'],
                 ascending=[False, False]).reset_index(drop=True)

    Update_GG(Update_Bracket, client, Phase_Id, seeding_df)

# Exports and Opens CSV Spreadsheet
    folder = os.getcwd() + '\\seeding\\'
    try:
        Seeding_File =  folder + Event_Name + '_Seeding.csv'
        seeding_df.to_csv(Seeding_File, index=False)
        os.startfile(Seeding_File)
    except PermissionError:
        print("Permission Error: -> Printing Temporary Name")
        Seeding_File = folder + 'temp-' + Event_Name + '_Seeding.csv'
        seeding_df.to_csv(Seeding_File, index=False)
        os.startfile(Seeding_File)
    print('Task Complete')

###############################################################################
if __name__ == "__main__":
    main(Phase_Id, Event_Name)
