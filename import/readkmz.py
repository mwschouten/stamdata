import xml.sax, xml.sax.handler
from zipfile import ZipFile
from bs4 import BeautifulSoup
from shapely.geometry import Polygon, Point, MultiPolygon

def gettabledata(s):
    """
    parse the tables that NLOG puts in their KMZ files
    """
    
    def firstitem(x):
        try:
            return x[0]
        except IndexError:
            return '-'

    soup = BeautifulSoup(s.replace('\n',''),"lxml"  )
    data = {}
    for j,r in enumerate(soup.find_all("tr")):
        
        if j<=1:
            pass # First is name, second everything a whole table
    
        if j>1:    
            pv = [i.contents for i in r.find_all("td")]
            prop = firstitem(pv[0]).lower()
            val = firstitem(pv[1])
            if val=='<Null>':
                val='-'
            data[prop]=val
    return data
    
    

class PlacemarkHandler(xml.sax.handler.ContentHandler):
    def __init__(self):
        self.inName = False # handle XML parser events
        self.inPlacemark = False
        self.mapping = {} 
        self.buffer = ""
        self.name_tag = ""
        
    def startElement(self, name, attributes):
        if name == "Placemark": # on start Placemark tag
            self.inPlacemark = True
            self.buffer = "" 
        if self.inPlacemark:
            if name == "name": # on start title tag
                self.inName = True # save name text to follow
            
    def characters(self, data):
        if self.inPlacemark: # on text within tag
            self.buffer += data # save text if in title
            
    def endElement(self, name):
        self.buffer = self.buffer.strip('\n\t')
        
        if name == "Placemark":
            self.inPlacemark = False
            self.name_tag = "" #clear current name
        
        elif name == "name" and self.inPlacemark:
            self.inName = False # on end title tag            
            self.name_tag = self.buffer.strip()
            self.mapping[self.name_tag] = {}
        elif self.inPlacemark:
            if name in self.mapping[self.name_tag]:
                self.mapping[self.name_tag][name] += self.buffer
            else:
                self.mapping[self.name_tag][name] = self.buffer
        self.buffer = ""

def getgeometry(v):

    ccs = v['coordinates'].split()
    if len(v['altitudeMode'].split()) > 1:
        # Multipolygon
        mp = []
        p=[]
        c0 = False
        for c in ccs:
            if not c0:
                c0=c
            x,y,z = list(map(float,c.split(',')))
            p.append((x,y))
            if c==c0 and len(p)>1:
                mp.append(Polygon(p))
                c0 = False
                p=[]
        return MultiPolygon(mp)
            
    if len(ccs)>1: # Polygon
       coords = [ list(map(float,cc.split(',')))[:2] for cc in ccs]
       return Polygon(coords)

    if len(ccs)==1: # Point
        return Point(list(map(float,ccs[0].split(',')))[:2])        
    print('WHAT NOW?')
    print(ccs)
    print('ERROR')
    return ccs

   
def readKMZ(filename, verbose=False, data=True, geometry=True):
    kmz = ZipFile(filename, 'r')
    kml = kmz.open('doc.kml', 'r')
    
    parser = xml.sax.make_parser()
    handler = PlacemarkHandler()
    parser.setContentHandler(handler)
    parser.parse(kml)
    kmz.close()
    
    res=[]
    for item,data in handler.mapping.items():
        if geometry:
            geom = getgeometry(data)
        else:
            geom = None

        if data:
            dd = gettabledata(data['description']) 
        else:
            dd = None
            
        res.append((item,dd,geom))
        if verbose:
            print()
            print (item)
            print ('Geometry : ',geom.wkt)
            print()   
            for k,v in dd.items():
                print("{:>25} : {}".format(k,v))
    return res


if __name__=="__main__":
    
    
#    M1 = readKMZ('data/NLOG_Geothermie_GCS_WGS_1984_20180126.kmz',
#                 data=False)
#      
#    M2 = readKMZ('data/NLOG_Geothermie_aangevraagd_GCS_WGS_1984_20171017.kmz',
#                 data=False)
#          
#    for (n1,d1,G1) in M2:
#
#        print(n1)
#        for n2,G2 in M2:
#            if G1.overlaps(G2):
#                print ('   ... conflicteert met ',n2, '(bestaande vergunning)')
#        
#        for (n2,d2,G2) in M2:
#            if G1.overlaps(G2):
#                print ('   ... conflicteert met  ',n2, '(aanvraag)')

    M1 = readKMZ('data/NLOG_Boorgaten_GCS_WGS_1984_20170112.kmz')        
    M2 = readKMZ('data/NLOG_Mijnbouwwerken_GCS_WGS_1984_20170113.kmz')        
    M3 = readKMZ('data/NLOG_Velden_GCS_WGS_1984_20170829.kmz')        

    from collections import Counter
    M = M1[:100]

    for fld in ['boorgatvorm','boorgatstatus']:
        cnt = Counter()
        for m in M1:
            cnt[m[1][fld]]+=1    
        print('\n',fld,'\n=========')
        print(cnt)
    
    """
     Producerende putten, die staan vermeld als gedevieerd
     Maar waarvan geen deviatie bekend is!
    """
    md = []
    for m in M1:
        status = m[1]['boorgatstatus']
        vorm = m[1]['boorgatvorm']
        onoff = m[1]['on offshore']
        if onoff=='ON':
            if status in ['Injecting', 'Producing', 'Water injecting','-']:
                if vorm in ['Horizontaal','Gedevieerd']:
                    deviatie = [m[1]['x deviatie utm31 ed50'],
                                m[1]['y deviatie utm31 ed50']]
                    eindpunt = [m[1]['x_end utm31_ed50'],
                                m[1]['y_end utm31_ed50']]
    
                    if sum(map(lambda x: float(x)**2,deviatie)) < 1.0**2:
                        print(m[0],deviatie,eindpunt,vorm)
                        
                        md.append(m[0])
    print('Gedevieerde put zonder deviatie:')
    print(md)

    #datafor:
    vries  = {i:j for i,j,k in M1 if 'VRS' in i}    
    me = 'AME-107-S1'
    me = 'VRS-10'
    [j for i,j,k in M1 if i==me]
    
    
    mbws = {m[1]['facility code']:m[0] for m in M2}
    from collections import defaultdict
    onbekend = defaultdict(list)
    
    for m in M1:
        status = m[1]['boorgatstatus']
        onoff = m[1]['on offshore']
        if onoff=='ON':
            if status in ['Injecting', 'Producing', 'Water injecting','-']:
                mbw = m[1]['mijnbouwwerk code']
                werk = mbws.get(mbw,'ONBEKEND '+mbw)
                if 'ONBEKEND' in werk or 'verwijderd' in werk:
                    onbekend[werk].append((m[0]))
                    print ("{} ({}) : {}".format(m[0],status,werk))
    
    print('Putcodes zonder mijnbouwwerk:')
    x = [i.split('-')[0] for i in onbekend['ONBEKEND -']]
    print(Counter(x))
    
    len(set([i.split('-')[0] for i in onbekend['ONBEKEND -']]))
"""
NOTES


Relaties:
    {       'PCC' : 'Plan concerns',
            'ILA' : 'In Licence area',
            'PMH' : 'Permit holder',
            'OPR' : 'Operator',
            'WSH' : 'Well starts here',
            'WTF' : 'Well to field',
            'OWN' : 'Current owner'}
      
Items to keep from boorgat:    
    
    ['on offshore', 'bloknummer', 'provincie code', 'provincie naam', 'gemeente naam', 'postcode', 'mijnbouwwerk code', 'mijnbouwwerk naam', 'startdatum', 'einddatum', 'boorgat / sidetrack', 'nitg nummer', 'uwi', 'boorgatcode', 'boorgatnaam', 'boorgatdoel code', 'boorgatdoel', 'boorgatresultaat code', 'boorgatresultaat', 'boorgatstatus', 'boorgatvorm', 'kickoff diepte ah', 'boorgatdiepte ah', 'boorgatdiepte tvd', 'referentievlak', 'hoogte referentievlak', 't.o.v.', 'boorgatdiepte ah t.o.v. nap / msl', 'boorgatdiepte tvd t.o.v. nap / msl', 'huidige eigenaar', 'opdrachtgever', 'boortoren/-platform', 'boorfirma', 'lithostratigrafie code', 'chronostratigrafie code', 'put naam', 'veld code', 'veld naam', 'openbaar vanaf']


Mijnbouwinstallaties zijn er in de volgende types:
    
        {'Geothermie installatie',
         'Off-load Terminal',
         'Plant',
         'Productielocatie',
         'Productieplatform',
         'Productiesatelliet',
         'Raffinaderij',
         'Sidetap',
         'Subsea',
         'Tanker mooring and loading system'}

Putten:
    
boorgatstatus 
=========
         {'-': 581,
         'Borehole ready': 15,
         'Closed-in': 624,
         'Completed to well': 53,
         'FAILED': 1,
         'Injecting': 7,
         'Observing': 22,
         'Planned': 1,
         'Plugged': 2,
         'Plugged and abandoned': 2610,
         'Plugged back': 112,
         'Plugged back and sidetracked': 384,
         'Producing': 1270,
         'Suspended': 50,
         'Technisch mislukt en sidetracked': 579,
         'Temporarily abandoned': 2,
         'Unknown': 58,
         'Water injecting': 30})
    
boorgatvorm 
=========
Counter({'Gedevieerd': 3301, 'Vertikaal': 2582, 
         'Horizontaal': 339, '-': 179})
    

Gedevieerde put zonder deviatie:
['AND-06-S1', 'ANJ-06', 'ANV-04', 'BAS-03-S1', 'BDM-05', 'BGM-03-S2', 'BGM-03-S3', 'BGM-03-S4', 'BGM-10', 'BGM-10-S1', 'BGM-10-S2', 'BGM-11', 'BGM-14', 'BGM-15', 'BGM-16', 'BGM-17', 'BGM-17-S1', 'BGM-18', 'BGM-19', 'BGM-23', 'BGM-24', 'BGM-25', 'BGM-27', 'BGM-28', 'BGM-29', 'BHM-07', 'BHM-07-S1', 'BRI-GT-01', 'BRI-GT-02', 'BRW-05', 'CAL-GT-01', 'CAL-GT-01-S1', 'CAL-GT-02', 'CAL-GT-03', 'CAL-GT-04', 'CAL-GT-05', 'COV-59', 'DIV-02', 'DKK-04', 'DVD-04', 'ERW-02', 'EWM-01-S1', 'EWM-03', 'FAN-02', 'GRO-01-S1', 'HEK-GT-01', 'HEK-GT-01-S1', 'HEK-GT-01-S2', 'HEK-GT-02', 'HON-GT-01', 'HON-GT-01-S1', 'HON-GT-01-S2', 'HON-GT-02', 'HRK-01-S2', 'HVE-01', 'KBB-04', 'KBB-05', 'KHL-GT-01', 'KHL-GT-02', 'KMP-04', 'KWR-02', 'LEW-102-S2', 'LIR-GT-01', 'LIR-GT-02', 'LMB-02', 'LNB-01-S1', 'LZG-02', 'LZG-03', 'MDM-GT-01', 'MDM-GT-02', 'MDM-GT-02-S1', 'MDM-GT-02-S2', 'MDM-GT-03', 'MDM-GT-03-S1', 'MDM-GT-04', 'MGT-03', 'MGT-04', 'MGT-05', 'MID-303', 'MKZ-07', 'MNZ-01', 'MON-04', 'NMD-02', 'NMD-03', 'NOR-41', 'NOR-416', 'NOR-43', 'PLD-GT-01', 'PLD-GT-02', 'SCH-1552', 'SCH-2952', 'SCH-2952-S1', 'SLD-06', 'SLD-06-S1', 'SLD-07', 'SLD-07-S1', 'SOW-02', 'SPKO-01-S2', 'TBN-01', 'TBN-02', 'TBN-03', 'TCI-09', 'TWI-01-S1', 'VDM-04-S1', 'VDM-04-S2', 'VKG-02', 'VRS-09', 'VRS-10', 'WAH-02', 'WAH-02-S1', 'WFM-02', 'WFM-03', 'WIT-04', 'WIT-05', 'WYK-201', 'WYK-202', 'WYK-35', 'WYK-36', 'WYK-37', 'WYK-39', 'WYK-41', 'WYK-42', 'WYK-43', 'WYK-44', 'ZRP-02', 'ZRP-03', 'ZRP-03-S1', 'ZWK-01']


"""
