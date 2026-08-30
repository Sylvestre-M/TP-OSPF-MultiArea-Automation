# Conception OSPF — TP OSPF Multi-Area Automation

## 1. Objectif

Cette documentation décrit la conception logique du routage **OSPF Multi-Area** utilisée dans le TP.

L'architecture est organisée autour d'un backbone **Area 0** et de plusieurs zones spécialisées :

- **Area 0** : backbone OSPF ;
- **Area 1** : zone OSPF standard ;
- **Area 2** : zone **Totally Stubby** ;
- **Area 3** : zone **NSSA** ;
- **Area 4** : zone **Stub**.

L'objectif est de mettre en œuvre une architecture multi-area, de contrôler la propagation des LSAs et de valider les adjacencies et le routage inter-area.

---

## 2. Processus OSPF

Tous les routeurs utilisent :

```text
OSPF Process ID : 1
```

Le Process ID est local au routeur. Il n'a pas besoin d'être identique entre plusieurs routeurs pour établir une adjacency, mais il est conservé à `1` de manière homogène dans ce TP pour simplifier l'exploitation.

---

## 3. Router-ID

Chaque routeur possède une Loopback0 utilisée comme Router-ID OSPF.

| Routeur | Router-ID |
|---|---:|
| ABR1 | `8.8.8.8` |
| ABR2 | `5.5.5.5` |
| ABR3 | `7.7.7.7` |
| ABR4 | `6.6.6.6` |
| BR1 | `1.1.1.1` |
| BR2 | `2.2.2.2` |
| BR3 | `3.3.3.3` |
| BR4 | `4.4.4.4` |
| IR1 | `9.9.9.9` |
| IR2 | `10.10.10.10` |
| IR3 | `11.11.11.11` |
| TSR1 | `12.12.12.12` |
| TSR2 | `13.13.13.13` |
| TSR3 | `15.15.15.15` |
| TSR4 | `14.14.14.14` |
| ASBR1 | `19.19.19.19` |
| ASBR2 | `21.21.21.21` |
| ASBR3 | `20.20.20.20` |
| SR1 | `18.18.18.18` |
| SR2 | `16.16.16.16` |
| SR3 | `17.17.17.17` |

Exemple :

```cisco
router ospf 1
 router-id 7.7.7.7
```

---

# 4. Area 0 — Backbone

L'**Area 0** est le backbone de l'architecture.

Elle relie les différents ABR et assure le transport du routage inter-area.

Les routeurs concernés sont notamment :

```text
BR1
BR2
BR3
BR4
ABR1
ABR2
ABR3
ABR4
```

Les liens de l'Area 0 utilisent les réseaux `/30` définis dans le plan d'adressage.

---

# 5. Area 1 — Zone standard

L'Area 1 est une zone OSPF classique.

Elle comprend :

```text
ABR2
 │
 ├── IR1
 │    └── IR2
 │         └── IR3
```

Les routeurs internes de cette zone utilisent une configuration OSPF standard.

Aucun paramètre `stub` ou `nssa` n'est appliqué à l'Area 1.

---

# 6. Area 2 — Totally Stubby Area

L'Area 2 est conçue comme une **Totally Stubby Area**.

Elle comprend :

```text
             ABR1
               │
              TSR4
            /  │           TSR1 TSR2 TSR3
```

ABR1 est le routeur frontière de l'Area 2.

## Configuration ABR1

ABR1 utilise :

```cisco
router ospf 1
 router-id 8.8.8.8
 area 2 stub no-summary
```

## Routeurs internes

Les routeurs TSR utilisent :

```cisco
router ospf 1
 area 2 stub
```

Le mot-clé `no-summary` est appliqué sur l'ABR et non sur les routeurs internes.

L'objectif est de limiter les informations de routage inter-area injectées dans cette zone.

---

# 7. Area 3 — NSSA

L'Area 3 est configurée comme **NSSA (Not-So-Stubby Area)**.

Elle comprend :

```text
             ABR4
            /            ASBR1    ASBR3
           \      /
             ASBR2
```

Les routeurs concernés sont :

```text
ABR4
ASBR1
ASBR2
ASBR3
```

La configuration de la zone est :

```cisco
router ospf 1
 area 3 nssa
```

## Rôle des ASBR

Les ASBR permettent d'introduire des routes externes dans la zone NSSA.

Ils constituent donc les points d'entrée du routage externe dans cette partie de l'architecture.

---

# 8. Area 4 — Stub Area

L'Area 4 est configurée comme **Stub Area**.

Elle comprend :

```text
             ABR3
              │
             SR1
            /             SR2---SR3
```

Les routeurs concernés sont :

```text
ABR3
SR1
SR2
SR3
```

Configuration sur ABR3 :

```cisco
router ospf 1
 router-id 7.7.7.7
 area 4 stub
```

Configuration sur les routeurs internes :

```cisco
router ospf 1
 area 4 stub
```

Contrairement à l'Area 2, l'Area 4 n'utilise pas :

```cisco
area 4 stub no-summary
```

---

# 9. Rôle des ABR

Un **ABR (Area Border Router)** possède des interfaces appartenant à plusieurs Areas.

Dans cette architecture :

| ABR | Areas |
|---|---|
| ABR1 | Area 0 / Area 2 |
| ABR2 | Area 0 / Area 1 |
| ABR3 | Area 0 / Area 4 |
| ABR4 | Area 0 / Area 3 |

Schéma logique :

```text
                     AREA 0
        ┌──────────────┼──────────────┐
        │              │              │
      ABR1           ABR2           ABR3          ABR4
        │              │              │              │
        ▼              ▼              ▼              ▼
      AREA 2         AREA 1         AREA 4         AREA 3
     Totally          Standard        Stub           NSSA
      Stubby
```

---

# 10. Types de LSAs et comportement attendu

La segmentation en Areas permet de limiter la propagation de certaines informations OSPF.

### Area 0

Zone backbone normale.

Les LSAs intra-area et inter-area nécessaires au fonctionnement du backbone sont présents.

### Area 1

Zone standard.

Elle fonctionne sans restriction particulière liée à un type de zone spécial.

### Area 2

Totally Stubby.

La zone est volontairement limitée afin de réduire les informations inter-area reçues par les routeurs internes.

### Area 3

NSSA.

Elle permet l'injection contrôlée de routes externes depuis les ASBR de la zone.

### Area 4

Stub.

Les routes externes sont limitées dans cette zone et un mécanisme de route par défaut est utilisé pour atteindre les destinations externes/inter-area selon la conception OSPF.

---

# 11. Interfaces OSPF

Le projet utilise une configuration OSPF directement sur les interfaces :

```cisco
interface Serial2/0
 ip ospf 1 area 0
```

Cette méthode permet de définir explicitement l'Area de chaque interface.

Elle évite notamment d'activer accidentellement OSPF sur une interface qui ne fait pas partie de la topologie.

Exemple ABR3 :

```cisco
interface Serial2/0
 ip ospf 1 area 0

interface Serial2/1
 ip ospf 1 area 0

interface Serial2/2
 ip ospf 1 area 4

interface Loopback0
 ip ospf 1 area 0
```

`Serial2/3` n'est pas utilisée sur ABR3 et ne doit pas être activée dans OSPF.

---

# 12. Adjacencies OSPF

Les liens série point-à-point doivent former des adjacencies OSPF entre les routeurs directement connectés.

Commande de vérification :

```cisco
show ip ospf neighbor
```

État attendu :

```text
FULL
```

Une adjacency ne doit être considérée comme valide que si :

- les interfaces sont `up/up` ;
- les adresses IP sont correctes ;
- les routeurs appartiennent à la même Area sur le lien ;
- les paramètres OSPF sont compatibles ;
- les paramètres Stub/NSSA sont cohérents lorsque nécessaire.

---

# 13. Vérification de l'interface OSPF

Commande :

```cisco
show ip ospf interface brief
```

Cette commande permet notamment de contrôler :

- l'Area ;
- l'adresse IP ;
- le coût ;
- l'état ;
- le nombre de voisins.

Exemple attendu pour ABR3 :

```text
Interface    PID   Area    IP Address/Mask    Cost  State  Nbrs F/C
Lo0          1     0       7.7.7.7/32         1     LOOP   0/0
Se2/0        1     0       10.0.8.2/30       64     P2P    ...
Se2/1        1     0       10.0.12.2/30      64     P2P    ...
Se2/2        1     4       10.0.28.1/30      64     P2P    ...
```

---

# 14. Vérification du routage

La table de routage doit contenir les routes apprises par OSPF.

Commande :

```cisco
show ip route ospf
```

Codes principaux :

```text
O      = route OSPF intra-area
O IA   = route OSPF inter-area
O E1   = route externe OSPF type 1
O E2   = route externe OSPF type 2
O N1   = route NSSA type 1
O N2   = route NSSA type 2
```

---

# 15. Vérification de la LSDB

Commande :

```cisco
show ip ospf database
```

Cette commande permet de vérifier la base de données OSPF et notamment la présence des différents types de LSAs.

Dans une architecture multi-area, la LSDB d'un routeur dépend de l'Area à laquelle il appartient.

Un routeur interne d'une zone ne possède donc pas nécessairement la même LSDB qu'un ABR ou qu'un routeur du backbone.

---

# 16. Vérification de la connectivité

Les Loopback sont utilisées pour tester la connectivité de bout en bout.

Exemples :

```cisco
ping 1.1.1.1
ping 7.7.7.7
ping 14.14.14.14
ping 18.18.18.18
ping 21.21.21.21
```

Les tests doivent être effectués depuis plusieurs zones afin de vérifier le routage inter-area.

---

# 17. Méthodologie de validation

La validation doit suivre cet ordre :

```text
1. Interfaces
       ↓
2. Adressage IP
       ↓
3. Ping des voisins directs
       ↓
4. OSPF Neighbor
       ↓
5. OSPF Interface
       ↓
6. OSPF Database
       ↓
7. Routing Table
       ↓
8. Ping des Loopback
       ↓
9. Validation inter-area
```

Commandes principales :

```cisco
show ip interface brief
show ip ospf neighbor
show ip ospf interface brief
show ip route ospf
show ip ospf database
```

---

# 18. Automatisation

L'infrastructure est automatisée avec :

```text
Python
   │
   ├── Netmiko
   │
   └── PyYAML
          │
          ▼
      Fichiers YAML
          │
          ▼
       Routeurs
```

Les fichiers YAML servent à centraliser les paramètres.

```text
yaml/
├── devices.yaml
├── interfaces.yaml
└── ospf.yaml
```

Les scripts Python exploitent ces données pour automatiser :

- l'adressage ;
- OSPF ;
- les vérifications ;
- la récupération des configurations ;
- la sauvegarde des configurations.

---

# 19. Architecture logique finale

```text
                           AREA 0
        ┌───────────────────────────────────────┐
        │                                       │
        │   BR1 ── BR2 ── BR3 ── BR4           │
        │    │      │      │      │             │
        │   ABR1   ABR2          ABR4            │
        │    │      │             │              │
        └────┼──────┼─────────────┼──────────────┘
             │      │             │
             │      │             │
          AREA 2  AREA 1       AREA 3
          Totally Standard      NSSA
          Stubby                 │
             │                   │
            TSR4              ASBR1
           / │  \                │
        TSR1 TSR2 TSR3        ASBR2
                                │
                              ASBR3


                         AREA 4
                          Stub
                           │
                          ABR3
                           │
                          SR1
                         /                          SR2───SR3
```

---

# 20. Résumé

| Élément | Configuration |
|---|---|
| OSPF Process | `1` |
| Backbone | Area `0` |
| Area 1 | Standard |
| Area 2 | Totally Stubby |
| Area 3 | NSSA |
| Area 4 | Stub |
| ABR1 | Area 0 ↔ Area 2 |
| ABR2 | Area 0 ↔ Area 1 |
| ABR3 | Area 0 ↔ Area 4 |
| ABR4 | Area 0 ↔ Area 3 |
| Router-ID | Loopback0 |
| Liens inter-routeurs | `/30` |
| Automatisation | Python + Netmiko + YAML |
| Vérification | `show ip ospf ...` + ping |

---

## Références du projet

- [`addressing-plan.md`](addressing-plan.md)
- [`../yaml/devices.yaml`](../yaml/devices.yaml)
- [`../yaml/interfaces.yaml`](../yaml/interfaces.yaml)
- [`../yaml/ospf.yaml`](../yaml/ospf.yaml)
- [`../scripts/`](../scripts/)
- [`../configs/`](../configs/)
