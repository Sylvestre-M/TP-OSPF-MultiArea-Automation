# Plan d'adressage — TP OSPF Multi-Area Automation

## 1. Vue d'ensemble

Ce document constitue la référence du plan d'adressage IPv4 utilisé pour la topologie du TP.

L'infrastructure utilise :

- des liens série point-à-point en `/30` ;
- des interfaces Loopback en `/32` ;
- OSPF Process ID `1` ;
- plusieurs Areas OSPF ;
- un backbone en Area 0 ;
- une Area 2 Stub/Totally Stubby ;
- une Area 3 NSSA ;
- une Area 4 Stub.

> Les informations de ce document doivent rester cohérentes avec la topologie GNS3 et les fichiers YAML du projet.

---

## 2. Router-ID / Loopback

| Routeur | Loopback0 | Masque | Router-ID |
|---|---|---|---|
| ABR1 | `8.8.8.8` | `/32` | `8.8.8.8` |
| ABR2 | `5.5.5.5` | `/32` | `5.5.5.5` |
| ABR3 | `7.7.7.7` | `/32` | `7.7.7.7` |
| ABR4 | `6.6.6.6` | `/32` | `6.6.6.6` |
| BR1 | `1.1.1.1` | `/32` | `1.1.1.1` |
| BR2 | `2.2.2.2` | `/32` | `2.2.2.2` |
| BR3 | `3.3.3.3` | `/32` | `3.3.3.3` |
| BR4 | `4.4.4.4` | `/32` | `4.4.4.4` |
| IR1 | `9.9.9.9` | `/32` | `9.9.9.9` |
| IR2 | `10.10.10.10` | `/32` | `10.10.10.10` |
| IR3 | `11.11.11.11` | `/32` | `11.11.11.11` |
| TSR1 | `12.12.12.12` | `/32` | `12.12.12.12` |
| TSR2 | `13.13.13.13` | `/32` | `13.13.13.13` |
| TSR3 | `15.15.15.15` | `/32` | `15.15.15.15` |
| TSR4 | `14.14.14.14` | `/32` | `14.14.14.14` |
| ASBR1 | `19.19.19.19` | `/32` | `19.19.19.19` |
| ASBR2 | `21.21.21.21` | `/32` | `21.21.21.21` |
| ASBR3 | `20.20.20.20` | `/32` | `20.20.20.20` |
| SR1 | `18.18.18.18` | `/32` | `18.18.18.18` |
| SR2 | `16.16.16.16` | `/32` | `16.16.16.16` |
| SR3 | `17.17.17.17` | `/32` | `17.17.17.17` |

---

## 3. Liens point-à-point

Tous les liens série utilisent un réseau `/30`.

| Réseau | Routeur A | Interface A | IP A | Routeur B | Interface B | IP B | Area |
|---|---|---|---|---|---|---|---:|
| `10.0.1.0/30` | ABR2 | Serial2/0 | `10.0.1.1` | BR2 | Serial2/2 | `10.0.1.2` | 0 |
| `10.0.2.0/30` | ABR4 | Serial2/0 | `10.0.2.1` | BR2 | Serial2/3 | `10.0.2.2` | 0 |
| `10.0.3.0/30` | BR2 | Serial2/1 | `10.0.3.2` | BR3 | Serial2/0 | `10.0.3.1` | 0 |
| `10.0.4.0/30` | BR1 | Serial2/0 | `10.0.4.1` | BR2 | Serial2/0 | `10.0.4.2` | 0 |
| `10.0.5.0/30` | BR1 | Serial2/1 | `10.0.5.1` | BR4 | Serial2/0 | `10.0.5.2` | 0 |
| `10.0.6.0/30` | BR3 | Serial2/1 | `10.0.6.1` | BR4 | Serial2/1 | `10.0.6.2` | 0 |
| `10.0.7.0/30` | BR4 | Serial2/2 | `10.0.7.1` | ABR1 | Serial2/1 | `10.0.7.2` | 0 |
| `10.0.8.0/30` | BR4 | Serial2/3 | `10.0.8.1` | ABR3 | Serial2/0 | `10.0.8.2` | 0 |
| `10.0.9.0/30` | BR1 | Serial2/3 | `10.0.9.1` | ABR1 | Serial2/0 | `10.0.9.2` | 0 |
| `10.0.10.0/30` | BR1 | Serial2/2 | `10.0.10.2` | ABR2 | Serial2/1 | `10.0.10.1` | 0 |
| `10.0.11.0/30` | BR3 | Serial2/2 | `10.0.11.2` | ABR4 | Serial2/1 | `10.0.11.1` | 0 |
| `10.0.12.0/30` | BR3 | Serial2/3 | `10.0.12.1` | ABR3 | Serial2/1 | `10.0.12.2` | 0 |
| `10.0.13.0/30` | ABR2 | Serial2/2 | `10.0.13.1` | IR1 | Serial2/0 | `10.0.13.2` | 1 |
| `10.0.14.0/30` | IR1 | Serial2/1 | `10.0.14.1` | IR2 | Serial2/0 | `10.0.14.2` | 1 |
| `10.0.15.0/30` | IR3 | Serial2/0 | `10.0.15.1` | IR2 | Serial2/1 | `10.0.15.2` | 1 |
| `10.0.16.0/30` | ABR2 | Serial2/3 | `10.0.16.1` | IR3 | Serial2/1 | `10.0.16.2` | 1 |
| `10.0.17.0/30` | TSR4 | Serial2/0 | `10.0.17.1` | TSR1 | Serial2/0 | `10.0.17.2` | 2 |
| `10.0.18.0/30` | TSR4 | Serial2/1 | `10.0.18.1` | TSR2 | Serial2/0 | `10.0.18.2` | 2 |
| `10.0.19.0/30` | TSR4 | Serial2/3 | `10.0.19.1` | TSR3 | Serial2/0 | `10.0.19.2` | 2 |
| `10.0.20.0/30` | TSR4 | Serial2/2 | `10.0.20.1` | ABR1 | Serial2/2 | `10.0.20.2` | 2 |
| `10.0.21.0/30` | ABR4 | Serial2/2 | `10.0.21.1` | ASBR1 | Serial2/0 | `10.0.21.2` | 3 |
| `10.0.22.0/30` | ABR4 | Serial2/3 | `10.0.22.1` | ASBR3 | Serial2/1 | `10.0.22.2` | 3 |
| `10.0.23.0/30` | ASBR2 | Serial2/0 | `10.0.23.1` | ASBR1 | Serial2/1 | `10.0.23.2` | 3 |
| `10.0.24.0/30` | ASBR2 | Serial2/1 | `10.0.24.1` | ASBR3 | Serial2/0 | `10.0.24.2` | 3 |
| `10.0.25.0/30` | SR2 | Serial2/0 | `10.0.25.1` | SR1 | Serial2/1 | `10.0.25.2` | 4 |
| `10.0.26.0/30` | SR3 | Serial2/0 | `10.0.26.1` | SR1 | Serial2/2 | `10.0.26.2` | 4 |
| `10.0.27.0/30` | SR2 | Serial2/1 | `10.0.27.1` | SR3 | Serial2/1 | `10.0.27.2` | 4 |
| `10.0.28.0/30` | ABR3 | Serial2/2 | `10.0.28.1` | SR1 | Serial2/0 | `10.0.28.2` | 4 |

---

## 4. Répartition des Areas

| Area | Type | Routeurs principaux |
|---:|---|---|
| 0 | Backbone | BR1, BR2, BR3, BR4, ABR1, ABR2, ABR3, ABR4 |
| 1 | Standard | ABR2, IR1, IR2, IR3 |
| 2 | Totally Stubby | ABR1, TSR1, TSR2, TSR3, TSR4 |
| 3 | NSSA | ABR4, ASBR1, ASBR2, ASBR3 |
| 4 | Stub | ABR3, SR1, SR2, SR3 |

---

## 5. Interfaces non utilisées

Une interface qui n'apparaît pas dans le tableau des liens n'est pas considérée comme un lien de la topologie.

En particulier, **ABR3 Serial2/3 n'est pas utilisé** dans cette architecture.

Il ne doit donc pas recevoir d'adresse IP ni être activé dans OSPF.

---

## 6. Cohérence avec OSPF

Les interfaces de chaque routeur doivent être associées à l'Area indiquée dans le tableau.

Exemple ABR3 :

```text
Loopback0   7.7.7.7/32       Area 0
Serial2/0   10.0.8.2/30      Area 0
Serial2/1   10.0.12.2/30     Area 0
Serial2/2   10.0.28.1/30     Area 4
Serial2/3   NON UTILISÉE
```

Configuration attendue :

```cisco
router ospf 1
 router-id 7.7.7.7
 area 4 stub
```

---

## 7. Validation

Les commandes suivantes doivent être utilisées pour vérifier l'adressage et OSPF :

```cisco
show ip interface brief
show ip ospf neighbor
show ip ospf interface brief
show ip route ospf
show ip ospf database
```

Pour chaque voisin direct, l'adjacency OSPF doit normalement atteindre :

```text
FULL
```

Les Loopback doivent être joignables depuis les autres zones lorsque le routage inter-area est opérationnel.

---

## 8. Source de vérité

L'ordre de référence du projet est :

```text
Topologie GNS3
      ↓
addressing-plan.md
      ↓
interfaces.yaml
      ↓
ospf.yaml
      ↓
Scripts Python
      ↓
Configuration des routeurs
      ↓
Vérifications
```

Toute modification de la topologie ou de l'adressage doit être répercutée dans ce document avant de modifier les fichiers YAML et les scripts.
