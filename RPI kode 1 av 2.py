# -*- coding: utf-8 -*-
"""
Created on Sun May  9 09:42:07 2021

@author: syver
"""

import paho.mqtt.client as mqtt #mqtt bibliotek
import requests #hente ut fra cot
import json #koble opp mot cot
import time #brukes for å sette tidsstempel
import datetime #hente ut måned og uke nummer
import csv #brukes for csv funksjonene


MQTT_ADDRESS = '192.168.5.242' #IP adresse til RPI for oppkobling mot mqtt
MQTT_USER = 'topher' #Brukernavn mqtt
MQTT_PASSWORD = 'topher' #Passord mqtt
MQTT_TOPIC = 'home/incoming'#Topic for innkommende data MQTT
mottatMelding =  ''
data_list = [] #data som kommer inn blir lagt inn i denne listen, blir tømt etter bruk

#Under er emnene for tilakemelding pr person
topher_topic, syver_topic, tobias_topic, fossum_topic, tor_martin_topic = "outgoing/topher", "outgoing/syver", "outgoing/tobias", "outgoing/fossum", "outgoing/tor_martin" 

#Emnene legges inn i liste for aksessering ved bruk av user_id senere
users_topic = [topher_topic, syver_topic, tobias_topic, fossum_topic, tor_martin_topic] #tuppel for å hindre endring

#Token til CoT
token = "eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI0OTAxIn0.M0Syaed5ANA7qATf5meAiDhk6eQuQT_iW93x_s1O2Ds"

#Key til ulike rom i CoT
kitchen_key, living_room_key, toilet_key, bathroom_key = "15270", "28016", "17350" ,"13600"

#Maksbegrensninger for hver rom rom
kitchen_count, living_room_count, toilet_count, bathroom_count = 5, 5, 1, 1

#Ulike bruker_id ene til hver person
chris_id, syver_id, tobias_id, fossum_id, tor_martin_id = 0,1,2,3,4

#Legges inn i liste for uthenting ved innkommend edata
users_id = [chris_id, syver_id, tobias_id, fossum_id, tor_martin_id]


#Lagerer key-ene i en liste for uthenting senere ut i fra room_id i overføringen
room_list = [kitchen_key, living_room_key, toilet_key, bathroom_key]

#Maksimum begrensingene lagt i liste for sammenligning senre
room_max_count = [kitchen_count, living_room_count, toilet_count, bathroom_count]

#Navn på rommene
room_names = [("Kitchen"), ("Living room"), ("toilet"), ("bathroom")]

booking_list = [] #Bokking liste for å lagre og aksessere booking data for å registrere tid brukt

booking_dict = { #dictionary for bookinger, key er booking id, user id, rom id og evt device id
    
    }

#room_names = [("kitchen"), ("bathroom"), ("living_room"), ("general")] #for å hente verdier fra dictionary

#kWH forbruk pr. enhet

komfyr_forbruk, kjokkenVifte_forbruk, kaffetrakter_forbruk, oppvaskmaskin_forbruk, brodrister_forbruk, vannkoker_forbruk = 2.2, 0.075, 1.5, 2, 1, 1.2

vaskemaskin_forbruk, torketrommer_forbruk, hairdryer_forbruk, barbermaskin_forbruk, varmekabler_forbruk = 2.5, 3, 0.75, 0.01, 0.5

tv_forbruk, stereoanlegg_forbruk = 0.1, 0.025

panelovn_forbruk, varmtvannsbereder_forbruk, lys_forbruk , kjoleskap_forbruk, fryseboks_forbruk, stovsuger_forbruk = 0.5, 2, 1, 0.16, 0.175, 1


#Dictonary med effektpriser til ulike elementer for senere uthenting
device_dict = {
    ("kitchen"): [komfyr_forbruk, kjokkenVifte_forbruk, kaffetrakter_forbruk, oppvaskmaskin_forbruk, brodrister_forbruk, vannkoker_forbruk],
    ("bathroom"): [vaskemaskin_forbruk, torketrommer_forbruk, hairdryer_forbruk, barbermaskin_forbruk, varmekabler_forbruk],
    ("living_room"): [tv_forbruk, stereoanlegg_forbruk],
    ("general"): [panelovn_forbruk, varmtvannsbereder_forbruk, lys_forbruk, kjoleskap_forbruk, fryseboks_forbruk, stovsuger_forbruk]
   }

guest_dict_names = [("Chris_guests"), ("Syver_guests"), ("Fossum_guests"), ("Tobias_guests"), ("Tor_Martin_guests" )]

guests = [("Guest1"), ("Guest2")]


#Dictionary hvor det lagres gjester pr. pers, og verdien er tidsstempel på når gjestene kom
guest_dict = {
    "Chris_guests" : {
        ("Guest1"): 0,   #Bruker tuppler som navn for å letter hente ut senere
        ("Guest2"): 0
        },
    "Syver_guests" : {
        ("Guest1"):0 ,
        ("Guest2"):0 
        },
    "Fossum_guests" : {
        ("Guest1"):0 ,
        ("Guest2"): 0
        },
    "Tobias_guests" : {
        ("Guest1"):0 ,
        ("Guest2"): 0
        },
    "Tor_Martin_guests" : {
        ("Guest1"): 0 ,
        ("Guest2"): 0
        }
    
    }


#Funksjonen som starter abonnement på innkommende emnet
def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print('Connected with result code ' + str(rc))
   # client.subscribe(outgoing_topic)
    client.subscribe(MQTT_TOPIC) #Abonnerer på emne
  

#Registrere rom bestilling i dictionary
def register_room_booking(user_id, booking_type, room_id):
    booking_time = time.time()
    booking_info = (user_id, booking_type, room_id) #liste til å utvide booking listen med
    booking_dict[booking_info] = booking_time
    
    
def total_room_time(user_id, booking_type, room_id):
    booking_info = (user_id, booking_type, room_id) #Henter ut key tuppelen for å få start tiden på rommet
    room_start_time = booking_dict(booking_info) #får ut startveriden fra dictionaryen
    booking_dict.pop(booking_info) #sletter elementet fra dictionaryen slik at man kan kan lagre verdier senere
    return room_start_time

#Funksjon som oppdaterer CoT
def bookeCoT(booking_type, user_id, room_id, person_count, client):
    response = requests.get('https://circusofthings.com/ReadValue', params = {'Key':room_list[room_id], 'Token':token}) #Henter data fra signal på CoT
    response = json.loads(response.content) #Bruker Json for å hente dataen
    value_string = response.get('Value') #Verdien på CoT
    current_room_count = int(value_string) #Gjør om dataen til heltall
    if (person_count + current_room_count) <= room_max_count[room_id]: #Sjekker om rom er ledig, med folk i rommet nå, antall som skal registreres og rom maks antall, kjører hvis ja
        data = {'Key':room_list[room_id], 'Token':token, 'Value':(person_count + current_room_count)} #Setter ny count er antall på rommet + antall som skal inn
        headers = {'Content-Type': 'application/json'} #For på laste opp dataen med json
        response = requests.put('https://circusofthings.com/WriteValue', data = json.dumps(data), headers = headers) #Endrer data på cot
        #Lagre bookingdata
        register_room_booking(user_id, booking_type, room_id) #Registrer inngang til rom
        #Publish rommet ble booket suksessfullt
        booking_status = "1" #En indikerer sukessfullt booking
        
        publish_topic = users_topic[user_id] #Bruker user_id for å sende tilbake til riktig bruker
        client.publish(publish_topic, booking_status) #Sender tilbake dataen
        print("The room was booked successfully")
    else: #Hvis rommet er fullt eller du booker for flere enn det er plass til nå. Tar hensys til eksisterende antall
        booking_status = "2"
        publish_data = booking_status
       # publish_topic = users_topic[user_id]
        client.publish(publish_topic, publish_data)
        print(room_names[room_id], "is unavailable. There are currently: ", current_room_count,"\n",
              "people at the room. People limit at room is: ", room_max_count[room_id],"\n", 
              "You are tring to book the room for: ", person_count, "people")
            #publish rommet er ikke tilgjengelig
            
#Fjerne person fra rom
def registere_ut_rom(booking_type, user_id, room_id, person_count, client):
    #Samme funksjon som for å registrere inn, bortsett fra at denne registerer ut og reduserer antall på CoT 
    response = requests.get('https://circusofthings.com/ReadValue', params = {'Key':room_list[room_id], 'Token':token})
    response = json.loads(response.content)
    value_string = response.get('Value') #Henter ut antall personer i rommet nå
    current_room_count = int(value_string) #Gjør antall personer om til int
    new_room_count = current_room_count - person_count #defienrer ny rom status til CoT
    if current_room_count - person_count >= 0:
        data = {'Key':room_list[room_id], 'Token':token, 'Value':(new_room_count)} #hvilket rom skal endres og til hva
        headers = {'Content-Type': 'application/json'}
        response = requests.put('https://circusofthings.com/WriteValue', data = json.dumps(data), headers = headers) #endrer romstatus

        
#Registerer reservering av enhet til dictionary booking_dict     
def register_device_booking(user_id, booking_type, room_id, device_id):
    booking_time = time.time()
    #Keyen i dictionaryet er bruker_id, booking type, rom og enhetsid
    booking_info = (user_id, booking_type, room_id, device_id) 
    #lager verdien som når enheten ble bestilt
    booking_dict[booking_info] = booking_time
    
    
    
#Hvor lenge enheten ble brukt    
def total_device_time(user_id, booking_type, room_id, device_id): #Burde egentlig hete devive_start_time
    #Henter ut verdien til det som samsvarer med keyen registert ovenfor
    booking_info = (user_id, booking_type, room_id, device_id) #for å finne starttid på device
    #Her blir veriden hentet ut som når bookingen ble startet
    device_start_time = booking_dict(booking_info) #får ut startverdi på devicen fra dictionarien
    device_dict.pop(booking_info) #sletter elementet fra dictionaryen slik at det enheten kan bli bestilt av brukeren flere ganger
    return device_start_time #returnerer start tiden, som blir sammenlignet senere mot når bestillingen avsluttes

#Henter ut strømverdi fra csv 
def price_from_csv():
     with open('price.csv','r' ) as file:
         reader = csv.reader(file) #bruker csv biblioteket til å lese filen
         for row in reader:
             price = row #Siden det kun er en rad, settes førte rad til prisen
             file.close() #Lukker filen
             return price #Returnerer strømprisen
   
def total_devicelectricity_price(room_id, booking_type, device_id, user_id):
    current_time = time.time() #tiden nå i sekunder
    start_time = total_device_time(user_id, booking_type, room_id, device_id) #device start tid i sekunder
    total_time = (current_time - start_time)/3600 #total tid på rommet i timer
    #total_time = device_price[room_names[room_id]][device_id]
    device_cost = device_dict[room_names[room_id]][device_id] #Henter ut kwH prisen pr. sekund
    price_Now = price_from_csv()
    electricity_cost = device_cost * total_time * price_Now #siden roomtime kommer i sekunder må kw prisen være pr. sekund
    return electricity_cost    

#Hvilken uke som er nå for lagring i csv fil
def current_week():
    
    my_date = datetime.date.today() # if date is 01/01/2018
    year, week_num, day_of_week = my_date.isocalendar()
    return week_num #retunrere uke nummer
    
#Hvilken måned som er nå 
def current_month():
    month = datetime.now().month
    return month #returnerer måned


def device_datalagring(user_id, room_id, booking_type, device_id): 
    
    #henter ut data når roombooking blir avsluttet, gjør om dataene til string for enkel sammenslåing
    user_id_string = str(user_id) #user id som string
    room_id_string = str(room_id) #gjør omt il string
    month_string = str(current_month()) #gjør om til string
    week_string = str(current_week()) #gjør om til string
    device_id_string = str(device_id)
    price_string = str(total_devicelectricity_price(room_id, booking_type, device_id, user_id))
    data_string = user_id_string + "," + month_string + "," + week_string + "," + room_id_string + "," + device_id_string + "," + price_string
    return data_string #lagre til fil
    
#Lagrer enhetshistorikk til csv fil for å hente ut strømkostnad
def write_device_to_file(user_id, room_id, booking_type, device_id):
    with open("datalagring.csv", "a") as file: #bruker file som navn
        data_string = device_datalagring(user_id, room_id, booking_type, device_id)
        file.write(data_string + '\n') #lager ny linje
        file.close()
        
#Hvilken gjest som må forlate dersom det kommer en ny gjest
def which_guest_must_leave(guest_dict, user_id, ): #Hvis det kommer gjest og det er fullt
    guests_time = guest_dict[((guest_dict_names)[user_id])] #Henter ut riktig medlemms gjester
    guest1_time = guests_time[("Guest1")] 
    guest2_time = guests_time[("Guest2")]
    #Siden gjestene blir registrert med tidsstempel, vil det laveste tidsstempelet ha vært der lengst
    if guest1_time < guest2_time:
        return ("Guest1") #Gjest 1 kom først
    elif guest2_time < guest1_time:
        return ("Guest2") #Gjest 2 kom først
    else:
        return ("Guest1") #I tilfelle begge er tomme så legger den inn på guest 1

#Legger inn ny gjest på riktig gjestenummer til riktig meldem
def register_guest(user_id, guest_dict, guest_dict_names):  #Må kjøres opp i en for loop opp mot person_count på antall gjester som registreres inn
    guest = which_guest_must_leave(guest_dict, user_id) #Henter ut riktig gjest fra forrgie funksjon
    guest_dict[((guest_dict_names)[user_id])][guest] = time.time() #Legger gjest til i dictionary

#Legger gjesten(e) til i oversikten
def add_guest_to_dict(user_id, guest_dict, guest_dict_names, person_count, client):
    i = 0
    while(i < person_count): #kjører antall ganger antall personer skal registreres
        register_guest(user_id, guest_dict, guest_dict_names) #Kjører funksjonen for å legge til ny gjest
        print(guest_dict[((guest_dict_names)[user_id])] )    
        i += 1
    booking_status = "1" #vellykktenm
        
    publish_topic = users_topic[user_id] #hvilken bruker som skal motta bekreftelsen
    client.publish(publish_topic, booking_status) #Sender tilbake til konsoll


def which_guest_to_reset(guest_dict, user_id, ): #Hvis det kommer gjest og det er fullt
    guests_time = guest_dict[((guest_dict_names)[user_id])]
    guest1_time = guests_time[("Guest1")]
    guest2_time = guests_time[("Guest2")]
    
    if guest1_time - guest2_time > 0:
        return ("Guest2") #Gjest 2 skal bli skrevet over, da den er mindre så den kom først
    elif guest2_time - guest1_time > 0 and guest1_time != 0: #
        return ("Guest1") #Gjest 1 blir skrevet over, da den er mindre enn gjest2 og kom først5
    elif guest2_time - guest1_time > 0 and guest1_time == 0:
        return ("Guest1")  #Gjest 1 blir skrevet over
    else:
        return ("Guest2") #I tilfelle begge er tomme så legger den inn på guest 1

def out_register_guest(user_id, guest_dict, guest_dict_names):  #Må kjøres opp i en for loop opp mot person_count på antall gjester som registreres inn
    guest = which_guest_to_reset(guest_dict, user_id ) #Henter ut riktig gjest fra riktgi medlem
    guest_dict[((guest_dict_names)[user_id])][guest] = 0 #dersom en gjest forlater blir den som har vært lengst satt til 0 

#fjerner gjest fra dictionary
def remove_guest_from_dict(user_id, guest_dict, guest_dict_names, person_count, client):
    i = 0
    print(guest_dict[((guest_dict_names)[user_id])] )    
    while(i < person_count): #Hvis flere gjester skal ut, så kjører så mange ganger så alle blir fjernet
        out_register_guest(user_id, guest_dict, guest_dict_names) #kjører funksjonen som setter tiden til 0 på gjeldene gjester
        print(guest_dict[((guest_dict_names)[user_id])] )    
        i += 1
    booking_status = "1"
        
    publish_topic = users_topic[user_id]
    client.publish(publish_topic, booking_status) #Gir tilbakemelding til esp32


def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    #mottatMelding = msg.payload
    data_list.clear() #fjerner data fra forrige melding,  slik at det kun blir registrert mottat data nå
    melding_streng = str(msg.payload, 'UTF-8') #gjør om dataen fra byte til streng
    print(melding_streng)
    
   # melding_streng = msg.payload
    melding_streng_split = melding_streng.split('x') #splitter meldingen på x
    melding_int = map(int, melding_streng_split) #gjør om verdiene til int
    data_list.extend(melding_int)#legger inn i liste for analyse
    
    booking_type = data_list[0] #første verdi indikerer bestillingstype
    user_id = data_list[1] #andre verdi indikerer hvilken bruker som bestiller
    room_id = data_list[2] #tredje verdi indikerer hvilket rom det angår
    person_count = data_list[3] #fjerde verdi indikerer person antall dersom det gjelder rom eller gjester
    device_id = data_list[3] #hvis det gjelder enhet indikerer fjerde verdi hvilken enhet
    if booking_type == 0:     #Booke rom
        bookeCoT(booking_type, user_id, room_id, person_count, client)  
        
    if booking_type== 1:  #Avbooke rom + registrere rom i dataoversikt
        registere_ut_rom(booking_type, user_id, room_id, person_count, client)
        
    if booking_type == 2: #Booke device
        register_device_booking(user_id, booking_type, room_id, device_id)
       
    if booking_type == 3: #avbooker device og lagrer strømdata 
        write_device_to_file(user_id, room_id, booking_type, device_id)
        
    if booking_type == 4: #legger til gjest i dictionary
        add_guest_to_dict(user_id, guest_dict, guest_dict_names, person_count, client)
        
    if booking_type == 5: #fjerner gjest fra dictionary
        remove_guest_from_dict(user_id, guest_dict, guest_dict_names, person_count, client)
                     
    print(str(msg.payload)) #printet ut til konsoll meldingen
    print(" ")
    
def main(): #fra inkludert bibliotek paho mqtt, som kjører ved mottat melding
    mqtt_client = mqtt.Client() #starter oppkobling
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD) #bruker og passord til passordbeskyttet server
    mqtt_client.on_connect = on_connect #abonnmerer på emne
    mqtt_client.on_message = on_message #kjører dersom det mottas ny melding, kjører kun en gang
    mqtt_client.connect(MQTT_ADDRESS, 1883) #hvilken tjener den skal koble opp til og hvilken port på tjener
    mqtt_client.loop_forever() #gjør at funksjonen kjører konstant


    if __name__ == '__main__':
        print('MQTT to InfluxDB bridge') #oppstartsmelding
        main()
