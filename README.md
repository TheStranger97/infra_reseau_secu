# TP1

## Part 1 - Network Setup

### Conf routeur

Après avoir ajouter toutes les machines et les avoirs allumés on peut commencer par configurer le routeur

`r1.tp1.efrei`

```bash
conf t
int fastEthernet 1/0.10
encapsulation dot1Q 10
ip addr 10.1.10.254 255.255.255.0
no sh
int fastEthernet 1/0.20
encapsulation dot1Q 20
ip addr 10.1.20.254 255.255.255.0
no sh
int fastEthernet 1/0.30
encapsulation dot1Q 30
ip addr 10.1.30.254 255.255.255.0
int fastEthernet 1/0.40
encapsulation dot1Q 40
ip addr 10.1.40.254 255.255.255.0
exit
int fastEthernet 1/0
no sh
```

### Conf switches

Ici toutes la configuration des switchs elles sont toute similaires à part au hostname et les vlans

- On déclare les vlans
- On nomme les vlans
- On set un hostname
- pour `core1.tp1.efrei` on set le trunk vers le routeur

`core1.tp1.efrei`

```bash
conf t
vlan 10
name admins
vlan 20
name clients
vlan 30
name servers
vlan 40
name guests
exit
hostname core1.tp1.efrei
int Ethernet 0/0
switchport trunk encapsulation dot1q
switchport mode trunk
switchport trunk allowed vlan add 10,20,30,40
switchport trunk allowed vlan remove 1
exit
exit
copy run start
```

La petite différence par rapport à `core1.tp1.efrei` ici est que là on va mettre du mode access sur les interfaces ethernet du switch qui sont branchées à des machines (mario, bowser, dhcp, etch) pour les mettres dans un vlan par exemple, `bowser` est dans le vlan 10 donc sur l’interface branchée à `bowser`

```bash
conf t
int ethernet x/x
switchport mode access
switchport access vlan 10
```

Toutes les commandes rentrées sur les switchs

`access1.tp1.efrei`

```bash
conf t
vlan 10
name admins
vlan 20
name clients
vlan 30
name servers
vlan 40
name guests
exit
hostname access1.tp1.efrei
int Ethernet 0/1
switchport mode access
switchport access vlan 20
int Ethernet 0/2
switchport mode access
switchport access vlan 20
exit
int Ethernet 0/0
switchport trunk encapsulation dot1q
switchport mode trunk
switchport trunk allowed vlan add 10,20
switchport trunk allowed vlan remove 1,30,40
exit
exit
copy run start
```

`access2.tp1.efrei`

```bash
conf t
vlan 10
name admins
vlan 20
name clients
vlan 30
name servers
vlan 40
name guests
exit
hostname access2.tp1.efrei
int Ethernet 0/1
switchport mode access
switchport access vlan 20
int Ethernet 0/2
switchport mode access
switchport access vlan 40
exit
int Ethernet 0/0
switchport trunk encapsulation dot1q
switchport mode trunk
switchport trunk allowed vlan add 10,20,40
switchport trunk allowed vlan remove 1,30
exit
exit
copy run start
```

`access3.tp1.efrei`

```bash
conf t
vlan 10
name admins
vlan 20
name clients
vlan 30
name servers
vlan 40
name guests
exit
hostname access3.tp1.efrei
int Ethernet 0/1
switchport mode access
switchport access vlan 20
int Ethernet 0/2
switchport mode access
switchport access vlan 10
exit
int Ethernet 0/0
switchport trunk encapsulation dot1q
switchport mode trunk
switchport trunk allowed vlan add 10,20,30,40
switchport trunk allowed vlan remove 1
exit
exit
copy run start
```

`access4.tp1.efrei`

```bash
conf t
vlan 10
name admins
vlan 20
name clients
vlan 30
name servers
vlan 40
name guests
exit
hostname access4.tp1.efrei
int Ethernet 0/1
switchport mode access
switchport access vlan 30
exit
int Ethernet 0/0
switchport trunk encapsulation dot1q
switchport mode trunk
switchport trunk allowed vlan add 30
switchport trunk allowed vlan remove 10,20,40
exit
exit
copy run start
```

### Clients

Les VPCS concrètement on leur donne juste une ip soit en statique soit par dhcp

`vpcs`

```bash
ip 10.1.xx.x/xx 10.1.xx.xxx
```

```bash
ip dhcp
```

```bash
save
```

Maintenant capture Wireshark pour montrer que ça peut se ping  
[`p1_routed_ping.pcap`](/tp1/p1/p1_routed_ping.pcapng)

# Part 2 - Avec internet

Pour l’accès à internet on va aller sur l’interface du routeur branchée au NAT sur gns3 et demander une ip en dhcp

`r1.tp1.efrei`

```bash
conf t
int fastEthernet 0/0
ip addr dhcp
no sh
exit
exit
```

Capture wireshark pour montrer que `r1.tp1.efrei` peut ping internet  
[`p2_no_nat.pcap`](/tp1/p2/p2_no_nat.pcapng)
<br>
<br>


## Accès internet client
Ici on fait le NAT pour que les clients aient aussi un accès internet

```bash
conf t
int fastEthernet 0/0
ip nat outside
int fastEthernet 1/0.10
ip nat inside
int fastEthernet 1/0.20
ip nat inside
int fastEthernet 1/0.30
ip nat inside
int fastEthernet 1/0.40
ip nat inside
exit
access-list 1 permit any
ip nat inside source list 1 int fastEthernet 0/0 overload
```  
Capture wireshark pour montrer que ça peut ping hors du LAN  
[`p2_nat.pcap`](/tp1/p2/p2_nat.pcapng)
<br>
<br>

On donne l’ip d’un dns au client pour qu’il puisse demander des ips en dehors du réseau local

`vpcs`

```bash
ip dns 1.1.1
```
Capture wireshark pour montrer qu'on peut résoundre des noms  
[`p2_routed_ping.pcap`](/tp1/p2/p2_routed_ping.pcapng)
<br>
<br>

Les confs des routeurs sont et de `dnsmasq` [ici](/tp1/configs/)

# TP2 - Offensive sec
## Part 1 - DHCP attacks
### Installation serveur dhcp
`dhcp.tp1.efrei`

```bash
sudo dnf install dnsmasq -y
```

```bash
sudo nano +185 /etc/dnsmasq.conf
```

`/etc/dnsmasq.conf` ligne 185

```bash
interface=enp2s4

#vlan10
dhcp-range=10.1.10.10,10.1.10.100,255.255.255.0,12h
dhcp-option=tag:10.1.10.0/24,option:router,10.1.10.254
dhcp-option=tag:10.1.10.0/24,option:dns-server,1.1.1.1

#vlan20
dhcp-range=10.1.20.10,10.1.20.100,255.255.255.0,12h
dhcp-option=tag:10.1.20.0/24,option:router,10.1.20.254
dhcp-option=tag:10.1.20.0/24,option:dns-server,1.1.1.1

#vlan40
dhcp-range=10.1.40.10,10.1.40.100,255.255.255.0,12h
dhcp-option=tag:10.1.40.0/24,option:router,10.1.40.254
dhcp-option=tag:10.1.40.0/24,option:dns-server,1.1.1.1
```

```bash
sudo systemctl restart dnsmasq
```

`r1.tp1.efrei`

```bash
conf t
int fastEthernet 1/0.10
ip helper-address 10.1.30.1
int fastEthernet 1/0.20
ip helper-address 10.1.30.1
int fastEthernet 1/0.40
ip helper-address 10.1.30.1
```

Capture wireshak pour montrer que tout work  
[`p1_dhcp_race.pcap`](/tp2/p1_dhcp_race.pcapng)  

<br>
<br>

Et plus rien... désolé j'ai mis tout mon temps sur le projet fil rouge et j'ai pas pu terminé celui-ci à temps
