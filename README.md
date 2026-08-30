# TP-OSPF-MultiArea-Automation

![Cisco](https://img.shields.io/badge/Cisco-IOS-blue)
![OSPF](https://img.shields.io/badge/Routing-OSPF-orange)
![Python](https://img.shields.io/badge/Python-3.x-yellow)
![Netmiko](https://img.shields.io/badge/Automation-Netmiko-green)
![YAML](https://img.shields.io/badge/Configuration-YAML-red)

## 📋 Présentation

Ce projet met en œuvre une infrastructure de routage dynamique basée sur **OSPF Multi-Area**, avec une partie dédiée à l'**automatisation de la configuration et des vérifications avec Python, Netmiko et YAML**.

Le TP a pour objectif de construire, configurer, vérifier et documenter une topologie Cisco composée de plusieurs zones OSPF.

L'infrastructure utilise notamment :

- **OSPF Area 0** comme backbone ;
- **OSPF Area 4** comme zone Stub ;
- un **ABR (Area Border Router)** assurant l'interconnexion entre les zones ;
- des **Loopback interfaces** utilisées notamment pour les Router-ID ;
- des liens série point-à-point ;
- une configuration déclarative avec des fichiers **YAML** ;
- l'automatisation avec **Python + Netmiko** ;
- des scripts de vérification et de sauvegarde ;
- des captures d'écran permettant de valider le fonctionnement de l'infrastructure.

---

## 🎯 Objectifs du TP

1. Construire la topologie réseau dans GNS3.
2. Configurer l'adressage IPv4 des interfaces.
3. Configurer les interfaces Loopback.
4. Mettre en place OSPF Process ID `1`.
5. Définir correctement les différentes Areas OSPF.
6. Configurer un ABR entre l'Area 0 et l'Area 4.
7. Configurer l'Area 4 comme **Stub Area**.
8. Établir les adjacencies OSPF.
9. Vérifier les LSDB et les tables de routage.
10. Vérifier la connectivité entre les différents routeurs.
11. Automatiser la configuration avec Netmiko.
12. Utiliser YAML comme source de données pour les scripts Python.
13. Automatiser les commandes de vérification.
14. Sauvegarder les configurations des équipements.
15. Documenter les validations.

---

## 🏗️ Topologie

La topologie est réalisée sous **GNS3**.

La topologie complète est disponible dans [`topology/`](topology/).

---

## 🌐 Architecture OSPF

### Area 0

L'**Area 0** constitue le backbone OSPF et assure la communication entre les différentes zones.

### Area 4

L'**Area 4** est configurée comme **Stub Area**.

ABR3 joue le rôle d'**ABR (Area Border Router)** :

```text
ABR3
├── Area 0
│   ├── Serial2/0
│   └── Serial2/1
│
└── Area 4
    └── Serial2/2
```

---

## 📡 Plan d'adressage

Le plan d'adressage complet est disponible dans [`docs/addressing-plan.md`](docs/addressing-plan.md).

### ABR3

| Interface | Adresse IPv4 | Masque | Area | Voisin |
|---|---|---|---|---|
| Loopback0 | `7.7.7.7/32` | `255.255.255.255` | 0 | — |
| Serial2/0 | `10.0.12.2/30` | `255.255.255.252` | 0 | BR3 |
| Serial2/1 | `10.0.8.2/30` | `255.255.255.252` | 0 | BR4 |
| Serial2/2 | `10.0.28.1/30` | `255.255.255.252` | 4 | SR1 |

### Interface non utilisée

`Serial2/3` sur ABR3 **n'est pas utilisée dans la topologie**.

Elle ne doit pas être adressée ni intégrée à OSPF.

---

## 🔢 Router-ID OSPF

Les Loopback0 sont utilisées pour fournir des Router-ID stables.

| Routeur | Router-ID |
|---|---:|
| ABR3 | `7.7.7.7` |
| BR3 | `3.3.3.3` |
| BR4 | `4.4.4.4` |
| SR1 | `18.18.18.18` |
| SR2 | `16.16.16.16` |
| SR3 | `17.17.17.17` |

Exemple :

```cisco
router ospf 1
 router-id 7.7.7.7
```

---

## ⚙️ Configuration OSPF

Le processus OSPF utilisé est :

```text
Process ID : 1
```

ABR3 possède des interfaces dans deux zones :

```text
Area 0
 ├── 10.0.8.0/30
 └── 10.0.12.0/30

Area 4
 └── 10.0.28.0/30
```

L'Area 4 est configurée comme Stub :

```cisco
router ospf 1
 area 4 stub
```

La configuration `stub` doit être cohérente sur les routeurs OSPF appartenant à cette zone.

---

## 🐍 Automatisation Python

La configuration et les vérifications sont automatisées avec **Python et Netmiko**.

```text
             YAML
              │
      ┌───────┼────────┐
      │       │        │
   devices  interfaces  ospf
      │       │        │
      └───────┼────────┘
              │
              ▼
        Scripts Python
              │
           Netmiko
              │
              ▼
        Routeurs Cisco
```

---

## 📄 Fichiers YAML

Les fichiers YAML servent de source de données pour les scripts.

### devices.yaml

Contient l'inventaire des équipements et leurs paramètres de connexion.

```yaml
devices:
  ABR3:
    host: 127.0.0.1
    port: 5007
    device_type: cisco_ios_telnet
```

### interfaces.yaml

Contient l'adressage des interfaces.

```yaml
devices:
  ABR3:
    Loopback0:
      ip: 7.7.7.7
      mask: 255.255.255.255

    Serial2/0:
      ip: 10.0.12.2
      mask: 255.255.255.252
```

### ospf.yaml

Contient les paramètres OSPF :

- Process ID ;
- Router-ID ;
- Areas ;
- réseaux ;
- paramètres Stub.

---

## 🛠️ Scripts Python

Les scripts sont regroupés dans [`scripts/`](scripts/).

### configure_interfaces.py

Configure l'adressage IPv4 des interfaces à partir de `interfaces.yaml`.

### configure_ospf.py

Configure OSPF à partir de `ospf.yaml`.

### configure_abr3.py

Script spécifique permettant de configurer ABR3, de nettoyer l'interface non utilisée, de configurer OSPF, de sauvegarder et de vérifier.

### verify_interfaces.py

Effectue les vérifications relatives aux interfaces :

```cisco
show ip interface brief
show interfaces
```

### verify_ospf.py

Effectue les vérifications OSPF :

```cisco
show ip ospf neighbor
show ip ospf interface brief
show ip route ospf
show ip ospf database
```

### backup_configs.py

Sauvegarde les configurations avec :

```cisco
show running-config
```

Les configurations sont stockées dans [`configs/`](configs/).

---

## 📦 Dépendances Python

Les dépendances sont définies dans [`requirements.txt`](requirements.txt).

Installation :

```bash
python3 -m pip install -r requirements.txt
```

Exemple :

```text
netmiko
PyYAML
```

---

## 🔌 Connexion aux équipements

L'environnement utilisé est **GNS3**.

Les routeurs sont accessibles via Telnet sur les ports configurés dans `devices.yaml`.

Exemple :

```yaml
ABR3:
  host: 127.0.0.1
  port: 5007
  device_type: cisco_ios_telnet
```

Les mots de passe ne doivent pas être stockés directement dans les fichiers versionnés.

---

## 🧪 Vérifications

### Vérification des interfaces

```cisco
show ip interface brief
```

Les interfaces utilisées doivent être `up/up`.

### Vérification des voisins OSPF

```cisco
show ip ospf neighbor
```

Les adjacencies doivent atteindre l'état :

```text
FULL
```

### Vérification des interfaces OSPF

```cisco
show ip ospf interface brief
```

### Vérification de la table de routage

```cisco
show ip route ospf
```

Codes attendus notamment :

```text
O
O IA
```

### Vérification de la LSDB

```cisco
show ip ospf database
```

---

## 🖥️ Tests de connectivité

Exemples :

```cisco
ping 7.7.7.7
ping 16.16.16.16
ping 17.17.17.17
ping 18.18.18.18
```

Les Loopback permettent notamment de vérifier la connectivité de bout en bout.

---

## 🔎 Dépannage

En cas de problème OSPF :

```text
1. Vérifier l'état des interfaces
        ↓
2. Vérifier l'adressage IP
        ↓
3. Tester les pings entre voisins directs
        ↓
4. Vérifier les Areas OSPF
        ↓
5. Vérifier les Router-ID
        ↓
6. Vérifier les adjacencies
        ↓
7. Vérifier la table de routage
        ↓
8. Vérifier la LSDB
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

## 📸 Captures d'écran

Les preuves de validation sont stockées dans [`screenshots/`](screenshots/).

Elles documentent notamment :

- l'état des interfaces ;
- les voisins OSPF ;
- les routes OSPF ;
- la fin de l'automatisation.

---

## 📁 Structure du projet

```text
TP-OSPF-MultiArea-Automation/
│
├── .gitignore
├── README.md
├── requirements.txt
│
├── configs/
├── docs/
├── logs/
├── output/
├── screenshots/
├── scripts/
├── topology/
└── yaml/
```

---

## 🚀 Mise en œuvre

### 1. Cloner le projet

```bash
git clone <URL_DU_REPOSITORY>
cd TP-OSPF-MultiArea-Automation
```

### 2. Créer l'environnement virtuel

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Vérifier les fichiers YAML

```bash
cat yaml/devices.yaml
cat yaml/interfaces.yaml
cat yaml/ospf.yaml
```

Les données doivent correspondre exactement à la topologie GNS3.

### 5. Configurer les interfaces

```bash
python3 scripts/configure_interfaces.py
```

### 6. Configurer OSPF

```bash
python3 scripts/configure_ospf.py
```

### 7. Vérifier l'infrastructure

```bash
python3 scripts/verify_interfaces.py
python3 scripts/verify_ospf.py
```

### 8. Sauvegarder les configurations

```bash
python3 scripts/backup_configs.py
```

---

## ✅ Critères de validation

Le TP est considéré comme fonctionnel lorsque :

- [ ] Toutes les interfaces utilisées sont `up/up`.
- [ ] Les adresses IP correspondent au plan d'adressage.
- [ ] Les Loopback sont opérationnelles.
- [ ] Les Router-ID sont correctement définis.
- [ ] Les adjacencies OSPF sont `FULL`.
- [ ] L'Area 0 fonctionne correctement.
- [ ] L'Area 4 fonctionne correctement.
- [ ] L'Area 4 est configurée comme Stub.
- [ ] ABR3 fonctionne comme ABR.
- [ ] Les routes inter-area sont présentes.
- [ ] Les Loopback sont joignables.
- [ ] Les configurations sont sauvegardées.
- [ ] Les scripts Python s'exécutent correctement.
- [ ] Les résultats des vérifications sont documentés.

---

## 📚 Documentation

Documentation complémentaire :

- [`docs/addressing-plan.md`](docs/addressing-plan.md)
- [`docs/ospf-design.md`](docs/ospf-design.md)
- [`docs/troubleshooting.md`](docs/troubleshooting.md)
- [`docs/verification.md`](docs/verification.md)

---

## 👤 Auteur

**Sylvestre Mouafo**

Projet réalisé dans le cadre de travaux pratiques de réseau et d'automatisation.
