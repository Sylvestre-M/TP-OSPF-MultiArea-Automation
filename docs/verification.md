# Verification — TP OSPF Multi-Area Automation

## 1. Objectif

Ce document définit la procédure de validation de la topologie OSPF Multi-Area.

La validation doit être effectuée après la configuration des interfaces et d'OSPF.

---

## 2. Vérification des interfaces

Commande :

```cisco
show ip interface brief
```

### Critères

Toutes les interfaces utilisées doivent être :

```text
up/up
```

Les interfaces non utilisées ne doivent pas être configurées accidentellement.

Exemple ABR3 :

```text
Serial2/0    10.0.8.2     up/up
Serial2/1    10.0.12.2    up/up
Serial2/2    10.0.28.1    up/up
Loopback0    7.7.7.7      up/up
```

`Serial2/3` n'est pas utilisée sur ABR3.

---

## 3. Vérification de l'adressage

Commande :

```cisco
show running-config
```

Comparer les adresses avec :

```text
docs/addressing-plan.md
```

Chaque lien `/30` doit présenter deux adresses appartenant au même réseau.

Exemple :

```text
10.0.28.0/30

ABR3  10.0.28.1
SR1   10.0.28.2
```

---

## 4. Vérification du Router-ID

Commande :

```cisco
show ip ospf
```

Le Router-ID doit correspondre à la Loopback0 prévue.

Exemple :

```text
ABR3
Router-ID : 7.7.7.7
Loopback0 : 7.7.7.7/32
```

---

## 5. Vérification des interfaces OSPF

Commande :

```cisco
show ip ospf interface brief
```

Vérifier :

- PID ;
- Area ;
- adresse IP ;
- coût ;
- état ;
- nombre de voisins.

Exemple ABR3 :

```text
Lo0        Area 0
Se2/0      Area 0
Se2/1      Area 0
Se2/2      Area 4
```

---

## 6. Vérification des voisins

Commande :

```cisco
show ip ospf neighbor
```

### État attendu

```text
FULL
```

Tous les voisins OSPF directs doivent être établis.

Une adjacency absente ou bloquée dans un état autre que `FULL` doit faire l'objet d'un diagnostic avant de poursuivre.

---

## 7. Vérification Area 0

Les routeurs du backbone doivent établir les adjacencies correspondant aux liens de l'Area 0.

Vérifier :

```cisco
show ip ospf neighbor
show ip ospf interface brief
```

Puis :

```cisco
show ip route ospf
```

Les routes inter-area doivent être visibles depuis les zones connectées au backbone.

---

## 8. Vérification Area 1

Vérifier les routeurs :

```text
ABR2
IR1
IR2
IR3
```

Commandes :

```cisco
show ip ospf neighbor
show ip ospf interface brief
show ip route ospf
```

L'Area 1 doit fonctionner comme une zone OSPF standard.

---

## 9. Vérification Area 2

L'Area 2 est **Totally Stubby**.

Routeurs :

```text
ABR1
TSR1
TSR2
TSR3
TSR4
```

Sur ABR1 :

```cisco
show running-config
```

Configuration attendue :

```cisco
area 2 stub no-summary
```

Sur les routeurs internes :

```cisco
area 2 stub
```

Vérifier également :

```cisco
show ip route
```

La table de routage des routeurs internes doit refléter le comportement attendu d'une Totally Stubby Area.

---

## 10. Vérification Area 3

L'Area 3 est une **NSSA**.

Routeurs :

```text
ABR4
ASBR1
ASBR2
ASBR3
```

Configuration attendue :

```cisco
router ospf 1
 area 3 nssa
```

Commandes :

```cisco
show ip ospf
show ip ospf neighbor
show ip ospf database
show ip route ospf
```

Les informations relatives aux routes externes doivent être vérifiées au niveau des ASBR et de l'ABR.

---

## 11. Vérification Area 4

L'Area 4 est une **Stub Area**.

Routeurs :

```text
ABR3
SR1
SR2
SR3
```

Configuration attendue :

```cisco
router ospf 1
 area 4 stub
```

Vérifier :

```cisco
show ip ospf neighbor
show ip ospf interface brief
show ip route ospf
```

L'adjacency ABR3 ↔ SR1 doit être `FULL`.

---

## 12. Vérification de la LSDB

Commande :

```cisco
show ip ospf database
```

La LSDB doit être cohérente avec le rôle du routeur et son Area.

Comparer notamment les informations présentes sur :

- un routeur de l'Area 0 ;
- un routeur de l'Area 1 ;
- un routeur de l'Area 2 ;
- un routeur de l'Area 3 ;
- un routeur de l'Area 4.

---

## 13. Vérification des routes

Commande :

```cisco
show ip route ospf
```

Codes importants :

```text
O      Intra-area
O IA   Inter-area
O E1   Externe type 1
O E2   Externe type 2
O N1   NSSA type 1
O N2   NSSA type 2
```

Le type de route doit être cohérent avec l'architecture OSPF.

---

## 14. Tests de connectivité

Tester les Loopback depuis plusieurs zones.

Exemples :

```cisco
ping 1.1.1.1
ping 7.7.7.7
ping 8.8.8.8
ping 14.14.14.14
ping 18.18.18.18
ping 19.19.19.19
ping 20.20.20.20
ping 21.21.21.21
```

Les résultats doivent être interprétés avec la table de routage et les routes de retour.

---

## 15. Vérification du mode privilégié

Le script d'automatisation doit exécuter les commandes de vérification en mode privilégié.

Commande :

```cisco
show privilege
```

Résultat attendu :

```text
Current privilege level is 15
```

Le prompt doit être :

```text
Router#
```

et non :

```text
Router>
```

---

## 16. Vérification de l'automatisation

Le script Python doit :

1. charger `devices.yaml` ;
2. se connecter aux routeurs en Telnet ;
3. passer en mode `enable` ;
4. exécuter les commandes `show` ;
5. récupérer `show running-config` ;
6. générer les fichiers `.cfg` ;
7. sauvegarder la configuration ;
8. afficher le résultat final.

Commandes exécutées :

```cisco
show ip interface brief
show ip ospf neighbor
show ip ospf interface brief
show ip route ospf
show ip ospf database
show running-config
show privilege
```

---

## 17. Résultat attendu du script

Pour chaque routeur :

```text
[TELNET] Connexion...
[OK] Connexion Telnet établie
[ENABLE] Passage en mode privilégié
[OK] Mode privilégié activé
[SHOW] show ip interface brief
[SHOW] show ip ospf neighbor
[SHOW] show ip ospf interface brief
[SHOW] show ip route ospf
[SHOW] show ip ospf database
[CFG] Récupération de show running-config
[OK] Fichier créé
[SAVE] Sauvegarde running-config -> startup-config
[OK] Configuration sauvegardée
```

Lorsque tous les routeurs ont été traités :

```text
Configuration terminée
```

Une boîte de dialogue doit également être affichée.

---

## 18. Tableau de validation

| Vérification | Commande | Résultat attendu | Statut |
|---|---|---|---|
| Interfaces | `show ip interface brief` | Interfaces utilisées `up/up` | ☐ |
| OSPF | `show ip ospf` | Processus 1 actif | ☐ |
| Router-ID | `show ip ospf` | Router-ID correct | ☐ |
| Interfaces OSPF | `show ip ospf interface brief` | Areas correctes | ☐ |
| Voisins | `show ip ospf neighbor` | Adjacencies `FULL` | ☐ |
| Routage | `show ip route ospf` | Routes OSPF présentes | ☐ |
| LSDB | `show ip ospf database` | LSDB cohérente | ☐ |
| Connectivité | `ping <Loopback>` | Réponse OK | ☐ |
| Privilèges | `show privilege` | Niveau 15 | ☐ |
| Sauvegarde | `show startup-config` | Configuration sauvegardée | ☐ |
| CFG | `configs/*.cfg` | Fichier présent par routeur | ☐ |

---

## 19. Validation finale

Le TP est validé lorsque :

```text
[ ] Toutes les interfaces utilisées sont up/up
[ ] Tous les adressages sont conformes au plan
[ ] Tous les Router-ID sont corrects
[ ] Les voisins OSPF sont FULL
[ ] Area 0 fonctionne
[ ] Area 1 fonctionne
[ ] Area 2 est Totally Stubby
[ ] Area 3 est NSSA
[ ] Area 4 est Stub
[ ] Les routes OSPF sont présentes
[ ] Les Loopback sont joignables
[ ] Le mode privilégié est utilisé
[ ] Les configurations sont sauvegardées
[ ] Les CFG sont générés
[ ] L'automatisation se termine sans erreur
```
