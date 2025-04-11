import time
import usb.core
import usb.util
import libusb
import usb.backend.libusb1

backend = usb.backend.libusb1.get_backend(find_library=lambda x: "C:\\Windows\\SysWOW64\\libusb-1.0.dll")

data=[0x00] #pour test
def send_data(data):
    print(data)
    dev = usb.core.find(backend=backend, idVendor=0x0483, idProduct=0x5750)  #cherche un microcontrolleur connecté en usb avec ces id

    # was it found?
    if dev is None:     #si aucun microcontrolleur n'est détecté
        print('Device not found')
    else:
        # if dev.is_kernel_driver_active(0):
        #     dev.detach_kernel_driver(0)

        # set the active configuration. With no arguments, the first
        # configuration will be the active one
        dev.set_configuration()
        # envoie l'octet de data au microcontrolleur connecté
        dev.ctrl_transfer(bmRequestType=0x20,bRequest=0x09,wValue=0x0200,wIndex=0x00,data_or_wLength=data)

def data_usb_voyants(voyant_idx,voyant_val):
    data_usb = 0b00000000 # créer un octet de 0
    if (voyant_idx[0] == 'bus_volts[0]') & (voyant_val[0] >= 10):   # vérifie si le tableau de bord est alimenté
        print(voyant_val)
        for i in range(1,len(voyant_val)):
            if voyant_idx[i] == 'generator_amps[0]':    # vérifie que l'alternateur ne fonctionne pas
                if voyant_val[i] == 0:
                    data_usb |= 0x01 << len(voyant_val)-2   # ajout d'un 1 sur le premier bit

            elif voyant_idx[i] == 'oil_pressure_psi[0]': # vérifie que la pression d'huile n'est pas sous le seuil critique
                if voyant_val[i] <= 25 :
                    data_usb |= 0x01 << len(voyant_val)-5    # ajout d'un 1 sur le 4eme bit

            elif voyant_idx[i] == 'governor_on[0]':
                if voyant_val[i] == 0:
                    data_usb |= 0x01 << len(voyant_val)-7

            else:
                data_usb |= int(voyant_val[i]) << (len(voyant_val)-(i+1))
                # l'ordre des datarefs à été choisi au préalable et ils envoient soit 0 soit 1
                # on peut donc juste ajouter leurs valeurs au bit correspondant à son emplacement en une seule ligne

    print(bin(data_usb))
    data_usb_tab=[data_usb] # la fonction send_dat prend un tableau en entrée
    #print(data_usb_tab)
    send_data(data_usb_tab) # appel la fonction pour envoyer l'octet crée

"""
import socket
msg = str.encode("RREF Hello Client!")
# Créer une socket datagramme
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Lier à l'adresse IP et le port
s.bind(("127.0.0.1", 49000))
print("Serveur UDP à l'écoute")
# Écoutez les datagrammes entrants
while(True):
    addr = s.recvfrom(1024)
    message = addr[0]
    address = addr[1]
    clientMsg = "Message du client: {}".format(message)
    clientIP  = "Adresse IP du client: {}".format(address)
    print(clientMsg)
    print(clientIP)
    # Envoi d'une réponse au client
    s.sendto(msg, address)"""
