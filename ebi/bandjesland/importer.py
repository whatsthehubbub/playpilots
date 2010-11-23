
import csv
import datetime
import os.path

from django.core.files import File

from ebi.bandjesland.models import *

dataFile = '/Users/alper/Downloads/20101118-2344-pretestdata/samplePlaybackRecordings.csv'
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
session.start = datetime.datetime.now()
session.end = datetime.datetime.now()
session.label = 'test'

session.save()

specialDict = {}

for line in reader:
    
    if not counter == 0:
        dateCreated = line[2]
        dateTimePlayback = line[3]
    
        specialPath = getAudioFilePath(dateCreated)
        
        special = BandjeslandSpecial(created=parseDate(dateCreated))
        special.mp3.save(dateCreated + '.mp3', File(open(specialPath, 'rb')), save=True)
        special.save()
    
        if not dateCreated in specialDict:
            specialDict[dateCreated] = special
    
        occ = BandjeslandSpecialOccurrence()
        occ.time = parseDate(dateTimePlayback)
        occ.session = session
        occ.special = specialDict[dateCreated]
        occ.save()
    
        print parseDate(dateCreated), parseDate(dateTimePlayback)
    
    counter += 1