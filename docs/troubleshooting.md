# Troubleshooting — TP OSPF Multi-Area Automation

## 1. Méthode de diagnostic

Toujours diagnostiquer dans cet ordre :

```text
Interface
   ↓
Adressage IP
   ↓
Connectivité du lien
   ↓
OSPF
   ↓
Adjacency
   ↓
LSDB
   ↓
Table de routage
   ↓
Connectivité inter-area
```

---

## 2. Vérifier les interfaces

Commande :

```cisco
show ip interface brief
```

Une interface utilisée doit être :

```text
Status     : up
Protocol   : up
```

Si elle est `administratively down` :

```cisco
interface Serial2/0
 no shutdown
```

Si elle est `up/down`, vérifier en priorité :

- le câblage GNS3 ;
- l'interface distante ;
- le type de lien ;
- le côté DCE/DTE ;
- l'adressage.

---

## 3. Vérifier l'adressage

Commande :

```cisco
show ip interface brief
```

Puis :

```cisco
show running-config
```

Pour un lien `/30`, vérifier que les deux extrémités appartiennent au même réseau.

Exemple :

```text
10.0.28.0/30

ABR3 = 10.0.28.1
SR1  = 10.0.28.2
```

Tester ensuite :

```cisco
ABR3#ping 10.0.28.2
```

Le ping du voisin direct doit fonctionner avant de chercher un problème OSPF.

---

## 4. Adjacency OSPF absente

Commande :

```cisco
show ip ospf neighbor
```

L'état attendu est :

```text
FULL
```

Si aucun voisin n'apparaît, vérifier :

```cisco
show ip ospf interface brief
```

Points à contrôler :

- interface activée dans OSPF ;
- même Area des deux côtés ;
- même réseau IP ;
- interface `up/up` ;
- paramètres OSPF compatibles ;
- zone Stub/NSSA cohérente.

---

## 5. Vérifier l'Area OSPF

Commande :

```cisco
show ip ospf interface brief
```

Exemple ABR3 :

```text
Se2/0    Area 0
Se2/1    Area 0
Se2/2    Area 4
Lo0      Area 0
```

`Serial2/3` sur ABR3 n'est pas utilisée et ne doit pas être activée dans OSPF.

---

## 6. Problème de Stub Area

Une zone Stub doit être configurée de manière cohérente sur tous les routeurs OSPF de la zone.

### Area 4

ABR3 :

```cisco
router ospf 1
 area 4 stub
```

SR1, SR2 et SR3 :

```cisco
router ospf 1
 area 4 stub
```

Une incohérence de type de zone peut empêcher l'adjacency de devenir `FULL`.

---

## 7. Problème Totally Stubby

L'Area 2 utilise :

```cisco
area 2 stub no-summary
```

sur ABR1.

Les routeurs internes utilisent :

```cisco
area 2 stub
```

Ne pas appliquer `no-summary` sur les routeurs internes.

---

## 8. Problème NSSA

L'Area 3 utilise :

```cisco
area 3 nssa
```

sur ABR4 et les routeurs de l'Area 3.

Vérifier :

```cisco
show ip ospf
show ip ospf database
show ip ospf neighbor
```

Les ASBR de cette zone sont :

```text
ASBR1
ASBR2
ASBR3
```

---

## 9. Router-ID

Vérifier :

```cisco
show ip ospf
```

Le Router-ID doit correspondre à la Loopback définie dans le plan d'adressage.

Exemple :

```text
ABR3
Loopback0 = 7.7.7.7
Router-ID  = 7.7.7.7
```

Après modification d'un Router-ID sur un processus OSPF déjà actif, un redémarrage du processus peut être nécessaire :

```cisco
clear ip ospf process
```

À utiliser avec prudence sur une infrastructure en production. Dans ce TP, cela peut être utilisé pour appliquer immédiatement un nouveau Router-ID.

---

## 10. Routes OSPF absentes

Commande :

```cisco
show ip route ospf
```

Puis :

```cisco
show ip ospf database
```

Si une route n'est pas présente :

1. vérifier l'adjacency ;
2. vérifier que le réseau est bien annoncé ;
3. vérifier l'Area ;
4. vérifier la LSDB ;
5. vérifier le type de zone.

---

## 11. Ping inter-area impossible

Tester d'abord le voisin direct :

```cisco
ping <IP_voisin>
```

Puis la Loopback du routeur distant :

```cisco
ping <LOOPBACK>
```

Si le voisin direct fonctionne mais pas la Loopback :

```text
Lien IP OK
     ↓
Adjacency OK ?
     ↓
Route OSPF présente ?
     ↓
Route de retour présente ?
```

Vérifier :

```cisco
show ip route <destination>
```

---

## 12. Vérification des routes de retour

Un ping peut échouer même si la route aller existe.

Vérifier les deux côtés :

```cisco
show ip route <IP_destination>
```

et :

```cisco
show ip route <IP_source>
```

Une connectivité bidirectionnelle nécessite une route aller et une route retour.

---

## 13. Problème Telnet / Netmiko

Le projet utilise les consoles GNS3 :

```text
127.0.0.1:5000
127.0.0.1:5001
...
127.0.0.1:5020
```

Vérifier que le routeur est démarré dans GNS3.

Tester manuellement :

```bash
telnet 127.0.0.1 5007
```

Pour ABR3.

Si Netmiko échoue :

- vérifier le port ;
- vérifier que GNS3 est démarré ;
- vérifier l'authentification ;
- vérifier le `secret` enable ;
- vérifier `device_type: cisco_ios_telnet`.

---

## 14. Passage en mode privilégié

Le script doit exécuter les commandes `show` en mode privilégié :

```text
Router>
   ↓
enable
   ↓
Router#
```

Vérification manuelle :

```cisco
show privilege
```

Résultat attendu :

```text
Current privilege level is 15
```

---

## 15. Problème Tkinter

Si Python retourne :

```text
ModuleNotFoundError: No module named 'tkinter'
```

sur Debian/Ubuntu :

```bash
sudo apt update
sudo apt install python3-tk
```

Puis :

```bash
python3 -c "import tkinter; print('Tkinter OK')"
```

---

## 16. Commandes de diagnostic principales

```cisco
show ip interface brief
show ip ospf
show ip ospf neighbor
show ip ospf interface brief
show ip route
show ip route ospf
show ip ospf database
show running-config
show privilege
```

---

## 17. Checklist rapide

```text
[ ] Interfaces utilisées up/up
[ ] Adresses IP correctes
[ ] Ping des voisins directs OK
[ ] OSPF activé sur les bonnes interfaces
[ ] Areas correctes
[ ] Router-ID corrects
[ ] Neighbors FULL
[ ] LSDB cohérente
[ ] Routes OSPF présentes
[ ] Routes de retour présentes
[ ] Loopback joignables
[ ] Stub cohérent
[ ] NSSA cohérente
[ ] Telnet opérationnel
[ ] Mode privilégié niveau 15
```
