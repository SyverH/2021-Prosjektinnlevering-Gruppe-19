# -*- coding: utf-8 -*-
"""
Created on Thu Apr 29 17:35:25 2021

@author: syver
"""

import requests
import pandas as pd
from datetime import datetime as dt
import time
import json

###############################################################################
#Verdier som kan endres

VaerAvlesning_minuttDelay = 10 # i minutter
MainLoopintervall = 60 # i sekunder
ArealSolPanel = 30 # m^2
EffektSolpanel = 200 # Typisk 200W/m2
OvnEffekt = 1200 # effekt i Watt
LysEffekt = 30 # effekt i Watt

Strompris_sone = 'NO3' 

###############################################################################

SolcellepanelMaxEffekt = ArealSolPanel * EffektSolpanel #Teoretisk max effekt fra solcellepanel
prislisteTotal = [] 
prislisteSyver = []
prislisteChris = []
prislisteFossum = []
prislisteTorMartin = []
prislisteTobias = []

client_id = 'b762baee-f291-4057-8b61-cb1b7acb3779' # Bruker ID for Frost API
endpoint = 'https://frost.met.no/observations/v0.jsonld' # Endpoint for Frost API

parameters = { 
    'sources': 'SN68860',
    'elements': 'air_temperature',
    'referencetime': 'latest',
} # Parametre for Frost API

EndpointSky = 'http://api.openweathermap.org/data/2.5/onecall?' # Endpoint for OpenWeather API
ParametersSky = {
    'lat': '63.418827',
    'lon': '10.402732',
    'appid':'d5096354ca109ffda086dba72e7735b9',
    'exclude': 'hourly,minutely,daily,alerts',
    'units': 'metric'} # Parametre for OpenWeather API

Chris_token = 'eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI1NTIzIn0.dJWqc8A6CuM6C1PH9XF51Fm-cYKOKjseqZu-q_PPQnY' # Bruker: 19esp.A
Chris_ovn_key = '28642'
Chris_lys_key = '17789'
Chris_strompris_key = '27587'
Chris_temp_ute_key = '32499'
Chris_vind_ute_key = '5357'

Syver_token = 'eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI1NTI0In0.HMd7y-hVnXAyXwa3iw4mg6mx_pIMPH6mG-SxA3XguSw' #Bruker: 19esp.B
Syver_ovn_key = '4956'
Syver_lys_key = '20084'
Syver_strompris_key = '20975'
Syver_temp_ute_key = '26048'
Syver_vind_ute_key = '9827'

Fossum_token = 'eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI1NTI1In0.35WCAAoyYW-6_mlary9G3l2V3WcduFQfrIKMGgUTrhU' #Bruker: 19esp.C
Fossum_ovn_key = '5302'
Fossum_lys_key = '30747'
Fossum_strompris_key = '17601'
Fossum_temp_ute_key = '31834'
Fossum_vind_ute_key = '28753' 

Tor_Martin_token = 'eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI1NTI2In0.oiJfnponTjMnbeD5tZVVM7n561DkRJ_ovNLtrB9xbOE' #Bruker: 19esp.D
Tor_Martin_ovn_key = '31770'
Tor_Martin_lys_key = '31191'
Tor_Martin_strompris_key = '11937'
Tor_Martin_temp_ute_key = '24672'
Tor_Martin_vind_ute_key = '11424'

Tobias_token = 'eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI2MTA1In0.05tsq5uv49kNs_WNj9EOnJ8Usr2Bc160PMl4socXt8M' #Bruker: 19esp.E
Tobias_ovn_key = '10681'
Tobias_lys_key = '23023'
Tobias_strompris_key = '13980'
Tobias_temp_ute_key = '24587'
Tobias_vind_ute_key = '1756'

Home_token = 'eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI1NTIyIn0.y0VQUSFF4uJe5FUobIRMUxSZvA7O_AYxMIOt1sl58OM' #Bruker: 19esp.CTRL
Home_totalEffekt_key ='9735'
Home_StromprisTotal_key = '31159'
Home_TemperaturUte_key = '14230'
Home_VindUte_key = '21036'


Chris_ovn = {'Key': Chris_ovn_key ,
             'Token': Chris_token 
    } # Parametre til Chris ovn

Chris_Lys = {'Key': Chris_lys_key ,
             'Token': Chris_token
    } # Parametre til Chris lys

Syver_ovn = {'Key': Syver_ovn_key ,
             'Token': Syver_token
    } # Parametre til Syver ovn

Syver_Lys = {'Key': Syver_lys_key ,
             'Token': Syver_token
    } # Parametre til Syver lys

Fossum_ovn = {'Key': Fossum_ovn_key ,
              'Token': Fossum_token
    } # Parametre til Fossum ovn

Fossum_Lys = {'Key': Fossum_lys_key ,
              'Token': Fossum_token
    } # Parametre til Fossum lys

Tor_Martin_ovn = {'Key': Tor_Martin_ovn_key ,
              'Token': Tor_Martin_token
    } # Parametre til Tor Martin ovn

Tor_Martin_Lys = {'Key': Tor_Martin_lys_key ,
              'Token': Tor_Martin_token
    } # Parametre til Tor Martin lys

Tobias_ovn = {'Key': Tobias_ovn_key ,
              'Token': Tobias_token
    } # Parametre til Tobias ovn

Tobias_Lys = {'Key': Tobias_lys_key ,
              'Token': Tobias_token
    } # Parametre til Tobias lys

###############################################################################

# Funksjoner

def HentTemp(endpoint, parameters, client_id):
    
    r = requests.get(endpoint, parameters, auth=(client_id,'')) #Hent ut data fra nettsiden med endpoint, parametre og autentifikasjon
    
    json = r.json() # Gjør om dataen til json format
    
    data = json['data'] # Lagrer kun verdiene fra 'data'
    
    df = pd.DataFrame() # Lager en dataframe
    for i in range(len(data)):
        row = pd.DataFrame(data[i]['observations'])
        row['referenceTime'] = data[i]['referenceTime']
        row['sourceId'] = data[i]['sourceId']
        df = df.append(row) # Legger til dataene i forskjellige kategorier
        
    df = df.reset_index() # Resetter indeks så man kan indeksere med tall
    temp = float(df['value'].iloc[0]) # Henter kun ut den ene verdien som er tatt ved 5m høyde
    return temp # Returnerer temperaturen

def strompris(Zone):
    
    link = 'https://norway-power.ffail.win/?' # Endpoint til nettsiden som leverer strømpriser

    date = dt.now() # Henter ut datoen nå
    date = date.strftime('%Y-%m-%d') # formaterer datoen til YYYY-MM-DD Format
    
    priser = requests.get(link, params = {'zone': Zone, 'date': date}) # Henter ut data fra nettsiden med sone parameter, samt datoen i dag som vi definerte ovenfor
    
    json = priser.json() # Gjør om return funksjonen til json format
    
    df = pd.DataFrame.from_dict(json) # Gjør om til dataframe
    df = df.transpose()  # Fikser dataframen til å stå riktig vei
    df = df.drop(columns= ["valid_from", "valid_to"] ) # Fjerner unødvendige kolonner
    df = df.reset_index() # Resetter indeks, slik at dataframen kan indekseres med tall, fremor datoer
    df = df.rename(columns = {'index': 'Real_Time'}) # Gir nytt navn til den tidligere index kolonnen
    
    return df #returnerer et dataframe med indeks 0-23 og strømpriser for hver time
    
def pris_naa(Dataframe):
    Hour = int(dt.now().strftime('%H')) # Henter ut hvilken time av døgnet vi er i
    
    price_Now = Dataframe.loc[Hour, 'NOK_per_kWh'] # Velger verdi fra dataframe med indeks gitt fra hvilken time av døgnet vi er i
    
    return price_Now # Returnerer prisen

def Skydekke(Endpoint, Parameters):
    request = requests.get(Endpoint, Parameters) # Henter data fra endpoint og parametre
    request = request.json() # Gjør om return verdiene til json format
    Skydekke = (request['current'])['clouds'] # Henter ut % skydekke
    Soloppgang = (request['current'])['sunrise'] # Henter ut tid for soloppgang i time.time() format (sekunder siden 1970)
    Solnedgang = (request['current'])['sunset'] # Henter ut tid for solnedgang i time.time() format (sekunder siden 1970)
    VindHastighet = (request['current'])['wind_speed'] # HEnter ut vindhastigheten i m/s
    Liste = [Skydekke, Soloppgang, Solnedgang, VindHastighet]  # Legger alle verdier i en liste som kan indekseres
    return Liste # Returnerer listen

def CoT_Verdi(Parameters):
    response = requests.get('https://circusofthings.com/ReadValue', Parameters) # Enkel funksjon for å hente ut verdier av signaler fra CoT
    response = json.loads(response.content) # Gjør om svaret til json format
    value = response.get('Value') # Velger verdien vi skal ha
    return value # Returnerer verdien

def CoT_Write_Verdi(Token, Key, Value):
    headers = {'Content-Type': 'application/json'} # Definerer headersene
    data = {'Key': Key,
            'Token': Token,
            'Value': Value
            } # Definerer dataen
    response = requests.put('https://circusofthings.com/WriteValue', data = json.dumps(data), headers = headers) # Sender verdier til CoT signal

Sollys = False # Setter sollys til false til å begynne med
hour_last = int(dt.now().strftime('%H')) # Definerer timen av døgnet
Day_last = int(dt.now().strftime('%d')) # Definerer dagen det er
Week_last = int(dt.now().strftime('%W')) # Definerer ukenummeret
Tids_Delay_Strompriser = round(time.time()) # Setter punkt for start av nedtelling før strømprisene skal oppdateres
Tids_Delay_VaerInnhenting = round(time.time()) # Setter punkt for start av nedtelling før været skal oppdateres
Tids_Delay_MainLoop = time.time() # Setter punkt for start av nedtelling før hoved-loopen skal kjøre
Effektavlesning_start = time.time() # Setter punkt for start av nedtelling før effektavlesningen skal oppdateres
Tids_Delay_VaerInnhenting_2 = time.time() # Setter punkt for start av nedtelling før været skal hentes inn fra OpenWeather API

temp = HentTemp(endpoint, parameters, client_id) # Henter ut temperaturen fra Frost API
CoT_Write_Verdi(Chris_token, Chris_temp_ute_key, temp) #Skriver temperaturen til alle brukerenes Temperatur-Sgnal
CoT_Write_Verdi(Syver_token, Syver_temp_ute_key, temp)
CoT_Write_Verdi(Fossum_token, Fossum_temp_ute_key, temp)
CoT_Write_Verdi(Tor_Martin_token, Tor_Martin_temp_ute_key, temp)
CoT_Write_Verdi(Tobias_token, Tobias_temp_ute_key, temp)
pris = strompris(Strompris_sone) # Henter ut døgnets strømpris
price_Now = pris_naa(pris) # Henter ut timens strømpris
pris.plot(grid = True, figsize = (15,10)) # Plotter døgnets strømpris

VaerData = Skydekke(EndpointSky, ParametersSky) # Henter ut data
SkydekkeProsent = VaerData[0] # definerer hva som er skydekke
Soloppgang = VaerData[1] # definerer hva som er tid for soloppgang
Solnedgang = VaerData[2] # definerer hva som er tid for solnedgang
VindHastighet = VaerData[3] # definerer vindhastigheten ute

with open('Ukespriser.csv', "a") as file:
    file.write('Uke'+','+'Chris'+','+'Syver'+','+'Fossum'+','+'Tor_Martin'+','+'Tobias') # Starter en CSV fil der strømprisene for alle brukerene, samt totalen oppdateres en gang i uken

while(True): # Starter loopen som skal kjøre kontinuerlig
    if((time.time() - Effektavlesning_start) > 10): # Sjekker om det er lengre enn 10 sekunder siden siste effektavlesning
        Effektavlesning_start = time.time() # Resetter timeren for funksjonen
        Syver_ovn_Effekt = OvnEffekt * (CoT_Verdi(Syver_ovn)/100) #Regner ut effekten for brukerenes utstyr
        Syver_lys_Effekt = LysEffekt * CoT_Verdi(Syver_Lys)
        Chris_ovn_Effekt = OvnEffekt * (CoT_Verdi(Chris_ovn)/100)
        Chris_lys_Effekt = LysEffekt * CoT_Verdi(Chris_Lys)
        Fossum_ovn_Effekt = OvnEffekt * (CoT_Verdi(Fossum_ovn)/100)
        Fossum_lys_Effekt = LysEffekt * CoT_Verdi(Fossum_Lys)
        Tor_Martin_ovn_Effekt = OvnEffekt * (CoT_Verdi(Tor_Martin_ovn)/100)
        Tor_Martin_lys_Effekt = LysEffekt * CoT_Verdi(Tor_Martin_Lys)
        Tobias_ovn_Effekt = OvnEffekt * (CoT_Verdi(Tobias_ovn)/100)
        Tobias_lys_Effekt = LysEffekt * CoT_Verdi(Tobias_Lys)
        EffektUtSyver = Syver_ovn_Effekt + Syver_lys_Effekt #regner ut brukerenes totale effekt
        EffektUtChris = Chris_ovn_Effekt + Chris_lys_Effekt
        EffektUtFossum = Fossum_ovn_Effekt + Fossum_lys_Effekt
        EffektUtTorMartin = Tor_Martin_ovn_Effekt + Tor_Martin_lys_Effekt
        EffektUtTobias = Tobias_ovn_Effekt + Tobias_lys_Effekt
        EffektUt = EffektUtSyver + EffektUtChris + EffektUtFossum + EffektUtTorMartin + EffektUtTobias # Regner ut total effekt
    
    if((time.time() - Tids_Delay_Strompriser) > 30): # Sjekker om det er lengre enn 30 sekunder siden siste godkjenning av strømprisene
        Tids_Delay_Strompriser = time.time() # Resetter timeren
        Day_now = int(dt.now().strftime('%d')) # sjekker på nytt hvilken dag det er i dag
        Hour_now = int(dt.now().strftime('%H')) # Sjekker på nytt hvilken time det er nå
        if (Day_now != Day_last): # Sjekker om dagen den leste av nå er ulik dagen den leste av sist
            pris = strompris(Strompris_sone) # Hent inn nye dagspriser
            Day_last = int(dt.now().strftime('%d')) # Oppdater dagen
            print('Nye Dagspriser') 
        if (Hour_now != hour_last): # Sjekker om timen nå var ulik timen den leste av sist
            price_Now = pris_naa(pris) # Oppdaterer timesprisen
            hour_last = int(dt.now().strftime('%H')) # Oppdater hvilken time det er
            print('Ny pris på: ')
            print(price_Now)
            
            
    if((time.time() - Tids_Delay_VaerInnhenting) > VaerAvlesning_minuttDelay * 60): # Sjekker om det har gått lenger enn VaerAvlesning_minuttDelay Antall minutter siden sist loopen kjørte
        Tids_Delay_VaerInnhenting = time.time() # Oppdater timeren på loopen
        temp = HentTemp(endpoint, parameters, client_id) # Hent ut temperaturen fra Frost API
        CoT_Write_Verdi(Chris_token, Chris_temp_ute_key, temp) # Skriv temperaturen til de forskjellige brukerene
        CoT_Write_Verdi(Syver_token, Syver_temp_ute_key, temp)
        CoT_Write_Verdi(Fossum_token, Fossum_temp_ute_key, temp)
        CoT_Write_Verdi(Tor_Martin_token, Tor_Martin_temp_ute_key, temp)
        CoT_Write_Verdi(Tobias_token, Tobias_temp_ute_key, temp)
        CoT_Write_Verdi(Home_token, Home_TemperaturUte_key, temp)
        
        
        
    if ((time.time() - Tids_Delay_VaerInnhenting_2) > 120): # Sjekker om det er lengere enn 120 sekunder siden siste gang loopen kjørte
        Tids_Delay_VaerInnhenting_2 = time.time() # oppdater timeren på loopen
        VaerData = Skydekke(EndpointSky, ParametersSky) # Henter ut data
        SkydekkeProsent = VaerData[0] # definerer hva som er skydekke
        Soloppgang = VaerData[1] # definerer hva som er tid for soloppgang
        Solnedgang = VaerData[2] # definerer hva som er tid for solnedgang
        VindHastighet = VaerData[3] # definerer hva som er vindhastigheten ute
        CoT_Write_Verdi(Home_token, Home_VindUte_key, VindHastighet) # Skriver vindhastigheten til de forskjellige brukerene
        CoT_Write_Verdi(Tobias_token , Tobias_vind_ute_key , VindHastighet)
        CoT_Write_Verdi(Tor_Martin_token , Tor_Martin_vind_ute_key , VindHastighet)
        CoT_Write_Verdi(Fossum_token, Fossum_vind_ute_key , VindHastighet)
        CoT_Write_Verdi(Syver_token, Syver_vind_ute_key , VindHastighet)
        CoT_Write_Verdi(Chris_token, Chris_vind_ute_key , VindHastighet)
        print(SkydekkeProsent)
    
    if((time.time() - Tids_Delay_MainLoop) > MainLoopintervall): # Sjekker om det har gått lengre tid enn "MainLoopIntervall" Sekunder siden sist loopen kjørte
        Tids_Delay_MainLoop = time.time() # Resetter Intervallet
        if((time.time() > Soloppgang) and (time.time() < Solnedgang)): # Sjekker om tiden nå er innenfor tiden definert mellom soloppgang og solnedgang
            Sollys = True #Sier det er sollys ute dersom solen er mellom oppgang og nedgangstid
            EffektInn = SolcellepanelMaxEffekt * (1 - (SkydekkeProsent/100)) # Reduserer Effekten til solcellepanelene basert på Skydekke
            effektDelta = EffektUt - EffektInn
            # vi har effekt, antar at den er samme alle 60 sekundene mellom avlesning.
            effektDeltakWh = effektDelta/(1000 * 60) # Delta effekt gitt i W. delt på 1000 for å få Kw. avlesning hvert minutt git verdier på kWm, deler på 60 for å få kWh
            effektSyverDeltakWhPris = ((EffektUtSyver - (EffektInn/5)) / (1000 * 60)) * price_Now
            effektChrisDeltakWhPris = ((EffektUtChris - (EffektInn/5)) / (1000 * 60)) * price_Now
            effektFossumDeltakWhPris = ((EffektUtFossum - (EffektInn/5)) / (1000 * 60)) * price_Now
            effektTorMartinDeltakWhPris = ((EffektUtTorMartin - (EffektInn/5)) / (1000 * 60)) * price_Now
            effektTobiasDeltakWhPris = ((EffektUtTobias - (EffektInn/5)) / (1000 * 60)) * price_Now
            effektDeltakWhPris = effektDeltakWh * price_Now # Lagrer delta pris
            prislisteTotal.append(effektDeltakWhPris) # Skriver til brukerenes prisliste
            prislisteSyver.append(effektSyverDeltakWhPris)
            prislisteChris.append(effektChrisDeltakWhPris)
            prislisteFossum.append(effektFossumDeltakWhPris)
            prislisteTorMartin.append(effektTorMartinDeltakWhPris)
            prislisteTobias.append(effektTobiasDeltakWhPris)
                
        if((time.time() < Soloppgang) or (time.time() > Solnedgang)): # Sjekker om solen har gått ned
            Sollys = False #Sier at sollyset er borte dersom solen har gått ned
            EffektUtkWh = EffektUt/(1000 * 60) # Fjerner Solcellepanelet som et element dersom solen er nede
            EffektUtkWhPris = EffektUtkWh * price_Now
            effektSyverDeltakWhPris = (EffektUtSyver / (1000* 60)) * price_Now # Oppdaterer brukerenes strømpris
            effektChrisDeltakWhPris = (EffektUtChris / (1000* 60)) * price_Now
            effektFossumDeltakWhPris = (EffektUtFossum / (1000* 60)) * price_Now
            effektTorMartinDeltakWhPris = (EffektUtTorMartin / (1000* 60)) * price_Now
            effektTobiasDeltakWhPris = (EffektUtTobias / (1000* 60)) * price_Now
            prislisteTotal.append(EffektUtkWhPris) # Skriver strømprisen til brukerene
            prislisteSyver.append(effektSyverDeltakWhPris)
            prislisteChris.append(effektChrisDeltakWhPris)
            prislisteFossum.append(effektFossumDeltakWhPris)
            prislisteTorMartin.append(effektTorMartinDeltakWhPris)
            prislisteTobias.append(effektTobiasDeltakWhPris)
            
        if (len(prislisteTotal) > 60): # Sjekker om listen med strømpriser har overskredet 60 elementer, gjort for å spare plass
            listeforkortelse = sum(prislisteTotal) # Summerer listen
            prislisteTotal.clear() # Tømmer listen
            prislisteTotal.append(listeforkortelse) # Skriver inn verdien vi summerte
            listeforkortelseSyver = sum(prislisteSyver)
            prislisteSyver.clear()
            prislisteSyver.append(listeforkortelseSyver)
            listeforkortelseChris = sum(prislisteChris)
            prislisteChris.clear()
            prislisteChris.append(listeforkortelseChris)
            listeforkortelseFossum = sum(prislisteFossum)
            prislisteFossum.clear()
            prislisteFossum.append(listeforkortelseFossum)
            listeforkortelseTorMartin = sum(prislisteTorMartin)
            prislisteTorMartin.clear()
            prislisteTorMartin.append(listeforkortelseTorMartin)
            listeforkortelseTobias = sum(prislisteTobias)
            prislisteTobias.clear()
            prislisteTobias.append(listeforkortelseTobias)

        if (int(dt.now().strftime('%W')) != Week_last): # Sjekker om uken den leser av nå er ulik fra forrige uke
            Week_last = int(dt.now().strftime('%W')) # Oppdaterer Uken det er nå
            # Resetter prislisten ved ukesskifte. sender også regning til CSV fil
            with open('Ukespriser.csv', "a") as file: #Skriv til CSV.
                file.write( dt.now().strftime('%W') +','+ str(sum(prislisteChris))+','+ str(sum(prislisteSyver)) +','+ str(sum(prislisteFossum)) +','+ str(sum(prislisteTorMartin)) +','+ str(sum(prislisteTobias)) +','+str(sum(prislisteTotal)))
            
            print('Denne månedens totale strømpris ble: ')
            print(sum(prislisteTotal)) # Printer Månedsprisen for strøm
            print('Syvers strømpris ble: ')
            print(sum(prislisteSyver)) # Printer Månedsprisen for strøm
            print('Chris strømpris ble: ')
            print(sum(prislisteChris)) # Printer Månedsprisen for strøm
            print('Fossums strømpris ble: ')
            print(sum(prislisteFossum)) # Printer Månedsprisen for strøm
            print('Tor Martins strømpris ble: ')
            print(sum(prislisteTorMartin)) # Printer Månedsprisen for strøm
            print('Tobias strømpris ble: ')
            print(sum(prislisteTobias)) # Printer Månedsprisen for strøm
            prislisteTotal.clear() # Resetter listene til beboerene
            prislisteSyver.clear()
            prislisteChris.clear()
            prislisteFossum.clear()
            prislisteTorMartin.clear()
            prislisteTobias.clear()
            

        prissum = sum(prislisteTotal) # Oppdaterer beboerenes prissum
        prissumSyver = sum(prislisteSyver)
        prissumChris = sum(prislisteChris)
        prissumFossum = sum(prislisteFossum)
        prissumTorMartin = sum(prislisteTorMartin)
        prissumTobias = sum(prislisteTobias)
        print (prissum)
        CoT_Write_Verdi(Chris_token, Chris_strompris_key, prissumChris) # Skriver prissummen til alle beboerenes dashbord
        CoT_Write_Verdi(Syver_token, Syver_strompris_key, prissumSyver)
        CoT_Write_Verdi(Fossum_token, Fossum_strompris_key, prissumFossum)
        CoT_Write_Verdi(Tor_Martin_token, Tor_Martin_strompris_key, prissumTorMartin)
        CoT_Write_Verdi(Tobias_token, Tobias_strompris_key, prissumTobias)
        CoT_Write_Verdi(Home_token, Home_totalEffekt_key , EffektUt)
        CoT_Write_Verdi(Home_token, Home_StromprisTotal_key, prissum)
        