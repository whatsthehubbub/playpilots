from kipwip.models import *

import csv


race_filename = 'kipwip/races.csv'

racereader = csv.reader(open(race_filename), delimiter=';')

first = True
for racerow in racereader:
    if first:
        first = False
        continue

    print racerow
    
    raceid = int(racerow[1])
    movie = racerow[2]
    
    Kippenrace.objects.create(raceid=raceid, movie_filename=movie)


players_filename = 'kipwip/players.csv'

playerreader = csv.reader(open(players_filename), delimiter=';')

first = True

for playerrow in playerreader:
    if first:
        first = False
        continue
        
    print playerrow
    
    name = playerrow[0]
    kipid = int(playerrow[1])
    raceid = int(playerrow[2])
    position = int(playerrow[3])
    code = playerrow[4]
    
    try:
        time = int(playerrow[5])
    except ValueError:
        time = None
    
    try:
        race = Kippenrace.objects.get(raceid=raceid)
    except Kippenrace.DoesNotExist:
        race = None
    
    rider = Kippenrijder.objects.create(race=race, name=name, kipid=kipid, raceid=raceid, position=position, code=code, time=time)