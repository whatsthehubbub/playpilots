#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
from ebi.battleroyale.models import *


styles = {
    'Happy Camper': {
        'actions': ['geeft X een wilde bear hug.',
                    'biedt X een chill pill aan.',
                    'bietst brutaal een sigaretje van X.'],
        'reactions': ['reageert verontwaardigd: "Did you pee on my rug?"',
                    'vindt alles best, behalve dat X in zijn zon staat.',
                    'vindt het gedoe van X wel grappig.'],
        'winphrases': ['wint van X en steekt een dikke sigaar op. "I love it when a plan comes together!"',
                    'wint als een gek van X! Hij heeft vrienden in high places!']
    },
    'Spaceape': {
        'actions': ['doet een onnavolgbare breakdance move.',
                    'daagt X uit voor een MC battle.',
                    'vindt dat X danst als een toondove marionet.'],
        'reactions': ['fluistert in het oor van X: "The revolution will be terrorized."',
                    'kijkt glazig. Van welke planeet komt X?',
                    'blaast wat rook in het gezicht van X.'],
        'winphrases': ['wint van X en verdwijnt in de nacht.',
                    'wint episch van X en krijgt respect van de hele dansvloer!']
    },
    'Mr. DJ': {
        'actions': ['laat X zijn platenkoffer dragen.',
                    'geeft X een demonstratie van zijn turntablist techniek.',
                    'denkt dat X beter tot zijn recht komt op de schuimparty in Grou.'],
        'reactions': ['weigert het verzoeknummertje van X te draaien.',
                    'draait X weg uit de mix.',
                    'heeft geen geduld met gillende groupies zoals X.'],
        'winphrases': ['wint van X en het dak gaat eraf in Tivoli.',
                    'wint totaal van X en gaat cashen op Ibiza!']
    },
    'Nouvelle Vaag': {
        'actions': ['speelt de Samoerai-moord uit Rashomon na.',
                    'knipt naar X als Abel naar een vlieg.',
                    'nodigt X uit voor een Tarkovski marathon.'],
        'reactions': ['tegen X: "Are you looking at me? I said, are you f*#@!n looking at me?"',
                    'tegen X:  "See this?" (wrijft duim en wijsvinger over elkaar) "It\'s the world\'s smallest violin playing just for you."',
                    'fluit dreigend het deuntje uit Once Upon a Time in the West.'],
        'winphrases': ['wint van X en zegt: "I think this could be the beginning of a beautiful friendship."',
                    'wint briljant van X en wordt speciaal bedankt in de Oscar-speech van Cate Blanchett!']
    },
    'VIP Spotter': {
        'actions': ['wil op de foto met X en Gordon.',
                    'is benieuwd naar de claim to fame van X.',
                    'twijfelt of X wel fotogeniek genoeg is.'],
        'reactions': ['negeert X die duidelijk geen VIP is',
                    'heeft X even gegoogled en is niet onder de indruk.',
                    'photoshopt X er gewoon uit.'],
        'winphrases': ['wint van X en komt Anton Corbijn tegen op straat.',
                    'wint exclusief van X! Mis het niet in RTL Boulevard!']
    },
    'Barfly': {
        'actions': ['bestelt een Guillotine voor X.',
                    'bestelt een Sex on the Beach voor X.',
                    'keilt een viltje naar het hoofd van X.'],
        'reactions': ['grijnst: "Zullen we dit anders even buiten oplossen?"',
                    'legt het nog één keer uit: "You mustn\'t kick the bar. You must lean into the bar."',
                    'is vrienden met de uitsmijter. X kan beter even dimmen.'],
        'winphrases': ['wint van X en krijgt een rondje van de zaak.',
                    'wint bruut van X! Hollywoodstudio\'s bieden tegen elkaar op voor de filmrechten van het verhaal.']
    },
    'Avant Terrible': {
        'actions': ['blaast X weg met een lo-fi wall of noise.',
                    'daagt X uit voor een Pixies b-sides quiz.',
                    'verdenkt X van een stiekeme schlager collectie.'],
        'reactions': ['vindt X echt veel te mainstream.',
                    'luistert nog liever naar Kruder & Dorfmeister dan naar X.',
                    'is heel duidelijk tegen X: over smaak valt wel degelijk te twisten.'],
        'winphrases': ['wint van X en speelt een luchtgitaarsolo. ',
                    'wint mythisch van X en is Godspeed You! de Black Emperor!']
    },
    'Scissor Sister': {
        'actions': ['laat X haar oorlogskleuren zien.',
                    'keurt de outfit van X. Het doet pijn aan haar ogen.',
                    'gaat liever met de moeder van X uit.'],
        'reactions': ['legt X over de knie als een stout kind.',
                    'kijkt onschuldig en geeft X een speels knietje. ',
                    'zet haar zonnebril op en keurt X geen blik waardig.'],
        'winphrases': ['wint van X en verft haar haar overwinningsrood.',
                    'wint superieur van X! Own!']
    },
    'Struggling Artist': {
        'actions': ['heeft zin om de hotelkamer van X te verbouwen.',
                    'nodigt X uit om mee op tour te gaan door Polen. Als roadie.',
                    'schrijft een schunnig liedje over X.'],
        'reactions': ['is zulke miskenning wel gewend van mensen als X.',
                    'krijgt bar weinig inspiratie van X.',
                    'laat als een volleerde uitvreter X opdraaien voor de rekening.'],
        'winphrases': ['wint van X en wordt door het publiek op handen gedragen.',
                    'wint geniaal van X! Eindelijk erkenning voor deze grote artiest!']
    },
    'Mens Erger Je Niet': {
        'actions': ['verovert Kamtsjatka op X.',
                    'vermoordt X met de kandelaar in de biljartkamer.',
                    'zet de struikrover in tegen X.'],
        'reactions': ['schuift de zwarte piet terug naar X.',
                    'was al buutvrij. Jammer X.',
                    'ruimt de bom van X op met een mineur.'],
        'winphrases': ['wint van X en int smalend de huur van een hotel op het Neude.',
                    'wint overweldigend van X! Herdersmat!']
    },
    'Super Mario': {
        'actions': ['doet een vuistsprong naar X en breekt de bakstenen.',
                    'doet een monster kill headshot met zijn plasma gun op X.',
                    'verrast X met een Shin Shoryuken. Round 2!'],
        'reactions': ['doet een radslag-sprong opzij en ontwijkt X.',
                    'laat een bananeschil vallen en drukt X van de weg met zijn kart.',
                    'teleporteert weg van X en capturet de vlag.'],
        'winphrases': ['wint van X en redt de prinses.',
                    'wint verpletterend van X! All your mushrooms are belong to us!']
    },
}


for style in styles:
    so = Style.objects.create(name=style)
    
    for action in styles[style]['actions']:
        ActionPhrase.objects.create(style=so, phrase=action)
        
    for reaction in styles[style]['reactions']:
        ActionPhrase.objects.create(style=so, phrase=reaction, action=False)
        
    for winphrase in styles[style]['winphrases']:
        WinPhrase.objects.create(style=so, phrase=winphrase)