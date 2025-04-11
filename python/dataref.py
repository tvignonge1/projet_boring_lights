import socket
import struct
import time

from send_usb import *

#connection au réseau local
udp_ip = "0.0.0.0"
udp_port = 0
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((udp_ip, udp_port))

tab_value=[] #tableau qui contiendras les valeurs reçu
list_idx=[] #tableau des datarefs auquels ont est abonnés

def createmessage(dataref,index,f): #créer un message pour l'envoyer au simulateur
    global list_idx
    msg = struct.pack("<4sxii400s", b'RREF',
                      f,  # Send data # times/second
                      index,  # include this index number with results
                      dataref.encode('utf-8'))  # remember to encode as bytestring

    name_inv = ""
    name_idx = ""

    for i in range(0,-len(dataref),-1): # récupere le dernier mot du dataref à l'envers
        if dataref[i] != '/':
            name_inv += dataref[i]
        else:
            break

    for i in range(1,len(name_inv)):    # l'inverse
        name_idx += name_inv[-i]

    list_idx.append(name_idx)   # ajout à la liste des datarefs suivi

    return msg

def list_message(freq): #créer une liste de tous les datarefs a suivre ou ne plus suivre (selon freq)
    message = [
        createmessage('sim/cockpit2/electrical/bus_volts[0]',1,freq),
        createmessage('sim/cockpit2/electrical/generator_amps[0]', 2, freq),
        createmessage('sim/cockpit2/annunciators/fuel_quantity', 3, freq),
        createmessage('sim/cockpit2/annunciators/chip_detected[0]', 4, freq),
        createmessage('sim/cockpit2/engine/indicators/oil_pressure_psi[0]', 5, freq),
        createmessage('sim/cockpit2/switches/rotor_brake', 6, freq),
        createmessage('sim/cockpit2/engine/actuators/governor_on[0]', 7, freq),
        createmessage('sim/flightmodel2/engines/starter_making_torque[0]', 8, freq)
    ]
    return message

def subscribe_to_dref():
    message=list_message(2) #créer la liste des datarefs à suivre
    #print(message)
    for i in range(0,len(message)): #envoie les messages au simulateur
        sock.sendto(message[i],("127.0.0.1", 49000))
        #print(message[i])

    #for i in range(0,len(list_idx)):
        #print(list_idx[i])

def unsubscribe_from_dref():
    message=list_message(0) #créer la liste des datarefs à ne plus suivre
    for i in range(0,len(message)): #envoie les messages au simulateur
        sock.sendto(message[i],("127.0.0.1", 49000))
        #print(message[i])

def main():
    subscribe_to_dref() #s'abonne aux datarefs

    sock.settimeout(10) #ajoute un timeout de 10sec si le socket ne recoit rien dans la fonction recvfrom
    #to=sock.gettimeout()
    #print(to)

    while True:
        global list_idx

        recvdata = False    #booléen si recvfrm a reçu du logiciel

        while not(recvdata):
            try:
                data, addr = sock.recvfrom(2048)    #attend de recevoir une réponse du simulateur
                print("received data from server")
                recvdata = True

            except:                                 #si le timeout a été dépassé ou la connection n'as pas été faite
                subscribe_to_dref()                 #on se réabonne aux datarefs
                list_idx = list_idx[:8]             #list_idx ne garde que ses 8 premieres pour ne pas dépasser la limite
                print("réabonnement")
                time.sleep(1)                       #attente de 1sec

        #if keyboard.is_pressed('l'):    #si "l" alors on se désabonne et arret du programme
        #    unsubscribe_from_dref()
        #    print("unsubscribed from dref ending program")
        #    break

        if data.startswith(b'RREF'):    #vérifie si le message nous intéresse

            values = data[5:]  # retire l'en tête "RREF" du message reçu
            print(values)
            num_values = int(len(values) / 8)  # chaque dataref fait 8 octets (index + valeur)
            for i in range(num_values):
                dref_info = data[(5 + 8 * i):(5 + 8 * (i + 1))]  # extrait les 8 octets
                (index, value) = struct.unpack("<if", dref_info)
                print(list_idx[index-1],value)
                tab_value.append(value) # ajoute la valeur au tableau de valeur
            data_usb_voyants(list_idx[:8], tab_value[:8]) #appelle la fonction pour créer l'octet de données à envoyer

        for i in range (0,len(list_idx)):   #supprime les anciennes valeurs du tableau
            tab_value.pop()

"""def data_usb_voyants(voyant_idx,voyant_val):
    data_usb = 0b00000000
    if (voyant_idx[0] == 'bus_volts[0]') & (voyant_val[0] >= 10):
        print(voyant_val)
        for i in range(1,len(voyant_val)):
            if voyant_idx[i] == 'generator_amps[0]':
                if voyant_val[i] == 0:
                    data_usb |= 0x01

            elif voyant_idx[i] == 'oil_pressure_psi[0]':
                if voyant_val[i] <= 25 :
                    data_usb |= 0x08

            else:
                data_usb |= int(voyant_val[i])*(2**(i-1))

    #print(bin(data_usb))
    data_usb_tab=[data_usb]
    #print(data_usb_tab)
    send_data(data_usb_tab)"""


main()
#PENSER A UNSUBSCRIBE
