
"""
                                Winrate Seeder 
@authors: J4m, L4st
@version: 0.5

This code query's a Smash.gg Tournament corresponding to a given Phase Id.
It takes all the entrants in that phase, grabbing Seed Number, Seeding Id,
Player Id, and Gamer tag. 

The code then queries the Smashdata SQLite database to obtain player Win Rates
and Total Set counts. 

Finally it then Exports all this data as an Excel Spreadsheet. 

USER INPUTS:
    API_Key    [str] - This takes your smash.gg API key
    Phase_Id   [int] - The Phase Id of Players Needed to be seeded
    Event_Name [str] - The Name of the event (for file naming purposes)
    EXCEL     [bool] - writes in Excel format (CSV format if false)
"""

###############################################################################
# USER INPUTS

API_Key = '#############################'
Event_Name = 'Output_File_Name'
Phase_Id = 1000
EXCEL = False

###############################################################################
# IMPORTS

import os
import time as t
import pandas as pd
import json as js
import sqlite3
from graphqlclient import GraphQLClient as GQL
from win32com.client import Dispatch

###############################################################################
# DEFS

def Smash_Api(API_Key):
    'Starts the Graphql API Client'
    
    # Starts GraphQL file
    client = GQL('https://api.smash.gg/gql/' + 'alpha')
    client.inject_token('Bearer ' + API_Key)
    return client

#-----------------------------------------------------------------------------#

def Tourney_Players(client, phaseId):
    'Collects player seeding information and returns a Dataframe of entrants'
    
    # Setting Up Dataframe
    cols = ['Phase Seed','Seed ID','Player ID','Player']
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
        Seed_Num = player_list[i]['seedNum']
        Player_Id = player_list[i]['entrant']['participants'][0]['player']['id']
        Gamer_Tag = player_list[i]['entrant']['participants'][0]['player']['gamerTag']
        seeding_df.loc[i] = [Seed_Num, Seed_Id, Player_Id, Gamer_Tag]
        
    return seeding_df

#-----------------------------------------------------------------------------#

def Win_Rate(con, player_id, zeros):
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
        zeros += 1
    else:
        Win_Rate = round((Win/All),3)
    
    return [Win_Rate, All, zeros] 

#-----------------------------------------------------------------------------#
def main(API_Key, Phase_Id, Event_Name, EXCEL):
    'Runs all helper functions to produce seeding excel spreadsheet'
    
    # Closes All Excel Files
    Seeding_File = Event_Name + '_Seeding.xlsx'
    xl = Dispatch('Excel.Application')
    map(lambda book: book.Close(False), xl.Workbooks)
    xl.Quit()    
    
    # Starts API client and collects players from Phase Id
    print("Collecting Entrants in Phase")
    client = Smash_Api(API_Key)
    seeding_df = Tourney_Players(client, Phase_Id)
    
    # Specifies and opens Smashdata SQLite database
    db = 'ultimate_player_database.db'
    con= sqlite3.connect(db)
    
    # Adds Win Rate and Set Count to Dataframe
    print("Collecting Win Rates and Set Counts")
    t0 = t.time()
    count = 0
    zeros = 0
    seeding_df['Win Rate'] = '-'
    seeding_df['Sets'] = '-' 
       
    for i in range(len(seeding_df)):
        player_id = seeding_df.loc[i, 'Player ID']
        wr, sets, zeros = Win_Rate(con, player_id, zeros)
        seeding_df.loc[i, 'Win Rate'] = wr
        seeding_df.loc[i, 'Sets'] = sets
        count += 1
        # Progress Notes
        if (count % 10) == 0:
            print('    Finished Player: {}'.format(count))
        
    con.close()
    print('Win Rates and Set Counts Collected')
    # Calculates Stats
    t1 = t.time()
    tx = round((t1-t0),2)
    rate = round((count/tx),3)
    
    print("""
    - - - - - - - - - - -
     Time: {} s
     Players Count: {}
     Rate: {} Player/s
     Zeroes: {}
    - - - - - - - - - - -
     """.format(tx, count, rate, zeros))

    seeding_df = seeding_df.sort_values(by=['Win Rate', 'Sets'],
                 ascending=[False, False]).reset_index(drop=True)
    
    
    if EXCEL:
        # Exports and Opens Excel Spreadsheet
        try:
            Seeding_File = Event_Name + '_Seeding.xlsx'
            writer = pd.ExcelWriter(Seeding_File, engine='xlsxwriter')    
            seeding_df.to_excel(Seeding_File, index=False)
            writer.save()
            os.startfile(Seeding_File)
        except PermissionError:
            print("Permission Error: -> Printing Temporary Name")
            Seeding_File = Event_Name + '_Seeding.xlsx'
            writer = pd.ExcelWriter(Seeding_File, engine='xlsxwriter')    
            seeding_df.to_excel(Seeding_File, index=False)
            writer.save()
            os.startfile(Seeding_File)
    else:
        # Exports and Opens CSV Spreadsheet
        try:
            Seeding_File = Event_Name + '_Seeding.csv'
            seeding_df.to_csv(Seeding_File, index=False)
            os.startfile(Seeding_File)
        except PermissionError:
            print("Permission Error: -> Printing Temporary Name")
            Seeding_File = 'temp-' + Event_Name + '_Seeding.csv'
            seeding_df.to_csv(Seeding_File, index=False)
            os.startfile(Seeding_File)
    print('Task Complete')
    
###############################################################################    
if __name__ == "__main__":
    main(API_Key, Phase_Id, Event_Name, EXCEL)


