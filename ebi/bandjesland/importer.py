
import csv
import datetime
import os.path

from django.core.files import File

from ebi.bandjesland.models import *

dataFile = '/home/alper/bandjesland_import/zaterdag/samplePlaybackRecordings.csv'
sampleDirectory = os.path.join(os.path.dirname(dataFile), 'setRecorded')

f = open(dataFile, 'U')
reader = csv.reader(f)

def parseDate(datestring):
    parts = [int(it) for it in datestring.split('_')]
    return datetime.datetime(parts[0], parts[1], parts[2], parts[3], parts[4], parts[5])

def getAudioFilePath(datecreated):
    filePath = os.path.join(sampleDirectory, datecreated + '.mp3')
    
    return filePath

counter = 0

session = BandjeslandSessie()
# session.start = datetime.datetime(2010, 11, 26, 20, 23, 34)
# session.end = datetime.datetime(2010, 11, 26, 23, 38, 03)
# session.label = 'vrijdag'
session.start = datetime.datetime(2010, 11, 27, 19, 59, 04)
session.end = datetime.datetime(2010, 11, 28, 1, 9, 26)
session.label = 'zaterdag'

session.save()

specialDict = {}

for line in reader:
    
    if not counter == 0:
        dateCreated = line[2]
        dateTimePlayback = line[3]
    
        specialPath = getAudioFilePath(dateCreated)
        
        if not dateCreated in specialDict:
            special = BandjeslandSpecial(created=parseDate(dateCreated))
            if os.path.exists(specialPath):
                special.mp3.save(dateCreated + '.mp3', File(open(specialPath, 'rb')), save=True)
            special.save()

            specialDict[dateCreated] = special
    
        occ = BandjeslandSpecialOccurrence()
        occ.time = parseDate(dateTimePlayback)
        occ.session = session
        occ.special = specialDict[dateCreated]
        occ.save()
    
        print parseDate(dateCreated), parseDate(dateTimePlayback)
    
    counter += 1