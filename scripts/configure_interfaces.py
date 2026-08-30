#!/usr/bin/env python3

"""
====================================================================
Configuration automatique de l'adressage Cisco avec Netmiko
====================================================================

Fonctionnement :
    1. Charge devices.yaml
    2. Charge interfaces.yaml
    3. Se connecte aux routeurs GNS3 via Telnet
    4. Configure les adresses IP des interfaces
    5. Active les interfaces avec "no shutdown"
    6. Vérifie avec "show ip interface brief"
    7. Sauvegarde la configuration
    8. Affiche à la fin un tableau complet des adresses IP

Architecture :
    GNS3
      |
      +--- Telnet localhost:5000
      +--- Telnet localhost:5001
      +--- ...
      +--- Telnet localhost:5020

Dépendances :
    pip install netmiko pyyaml
"""

import sys
import time
import yaml

from netmiko import ConnectHandler
from netmiko.exceptions import (
    NetmikoTimeoutException,
    NetmikoAuthenticationException,
)


# ====================================================================
# Fichiers de configuration
# ====================================================================

DEVICES_FILE = "config/devices.yaml"
INTERFACES_FILE = "config/interfaces.yaml"


# ====================================================================
# Chargement d'un fichier YAML
# ====================================================================

def load_yaml(filename):
    """
    Charge un fichier YAML et retourne son contenu.

    En cas d'erreur, le script s'arrête immédiatement.
    """

    try:
        with open(filename, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)

    except FileNotFoundError:
        print(f"[ERREUR] Fichier introuvable : {filename}")
        sys.exit(1)

    except yaml.YAMLError as error:
        print(f"[ERREUR] YAML invalide : {filename}")
        print(error)
        sys.exit(1)


# ====================================================================
# Validation des fichiers YAML
# ====================================================================

def validate_config(devices_config, interfaces_config):
    """
    Vérifie que les deux fichiers YAML possèdent
    les sections nécessaires.
    """

    if not devices_config or "devices" not in devices_config:
        print("[ERREUR] Section 'devices' absente.")
        sys.exit(1)

    if not interfaces_config or "interfaces" not in interfaces_config:
        print("[ERREUR] Section 'interfaces' absente.")
        sys.exit(1)

    devices = devices_config["devices"]
    interfaces = interfaces_config["interfaces"]

    errors = []

    # Vérifie que chaque routeur présent dans interfaces.yaml
    # existe également dans devices.yaml.
    for router in interfaces:

        if router not in devices:
            errors.append(
                f"{router} est présent dans interfaces.yaml "
                f"mais absent de devices.yaml"
            )

        # Vérifie les informations de chaque interface.
        for interface in interfaces[router]:

            for field in ("name", "ip", "mask"):

                if field not in interface:
                    errors.append(
                        f"{router}: champ '{field}' manquant"
                    )

    # Si des erreurs sont détectées, on arrête le programme.
    if errors:

        print()
        print("[ERREUR] Configuration YAML incorrecte :")
        print()

        for error in errors:
            print(f"  - {error}")

        sys.exit(1)


# ====================================================================
# Connexion à un routeur GNS3
# ====================================================================

def connect_router(router_name, device):
    """
    Établit une connexion Telnet vers un routeur GNS3.

    Aucun username/password n'est utilisé.
    """

    connection_parameters = {
        "device_type": device.get(
            "device_type",
            "cisco_ios_telnet"
        ),

        "host": device.get(
            "host",
            "127.0.0.1"
        ),

        "port": int(device["port"]),

        # Pas d'authentification pour notre lab GNS3.
        "username": "",
        "password": "",

        # Timeout de connexion.
        "conn_timeout": 10,

        # Timeout d'authentification.
        "auth_timeout": 5,

        # Timeout de bannière IOS.
        "banner_timeout": 15,

        # Désactive certaines optimisations Netmiko
        # pour éviter des problèmes avec IOS/GNS3.
        "fast_cli": False,
    }

    print(
        f"[{router_name}] Connexion à "
        f"{connection_parameters['host']}:"
        f"{connection_parameters['port']}..."
    )

    connection = ConnectHandler(
        **connection_parameters
    )

    print(f"[{router_name}] Connexion OK")

    return connection


# ====================================================================
# Configuration des interfaces
# ====================================================================

def configure_interfaces(
    connection,
    router_name,
    interfaces
):
    """
    Configure toutes les interfaces définies
    dans interfaces.yaml.
    """

    commands = []

    print()
    print(f"[{router_name}] Interfaces à configurer :")

    # Parcourt toutes les interfaces du routeur.
    for interface in interfaces:

        name = interface["name"]
        ip = interface["ip"]
        mask = interface["mask"]

        print(
            f"    {name:<15} "
            f"{ip:<15} "
            f"{mask}"
        )

        # Commandes Cisco nécessaires.
        commands.extend([
            f"interface {name}",
            f"ip address {ip} {mask}",
            "no shutdown",
            "exit",
        ])

    # Envoie toutes les commandes au routeur.
    print(
        f"\n[{router_name}] "
        "Application de la configuration..."
    )

    output = connection.send_config_set(
        commands,
        cmd_verify=True
    )

    return output


# ====================================================================
# Vérification des interfaces
# ====================================================================

def verify_interfaces(connection, router_name):
    """
    Exécute "show ip interface brief".

    Cette commande permet de vérifier :
        - le nom de l'interface
        - l'adresse IP
        - le statut physique
        - le protocole
    """

    print()
    print(
        f"[{router_name}] "
        "Vérification des interfaces"
    )

    print("-" * 70)

    output = connection.send_command(
        "show ip interface brief"
    )

    print(output)

    return output


# ====================================================================
# Sauvegarde de la configuration
# ====================================================================

def save_configuration(connection, router_name):
    """
    Sauvegarde la configuration courante
    dans startup-config.
    """

    print(
        f"[{router_name}] "
        "Sauvegarde de la configuration..."
    )

    output = connection.save_config()

    print(
        f"[{router_name}] "
        "Configuration sauvegardée."
    )

    return output


# ====================================================================
# Extraction des IP depuis "show ip interface brief"
# ====================================================================

def parse_interface_brief(output, router_name):
    """
    Analyse la sortie de :

        show ip interface brief

    et transforme les informations en dictionnaires.

    Exemple de ligne IOS :

        GigabitEthernet0/0  192.168.10.254  YES NVRAM  up  up

    Résultat :

        {
            "router": "BR1",
            "interface": "GigabitEthernet0/0",
            "ip": "192.168.10.254",
            "status": "up",
            "protocol": "up"
        }
    """

    addresses = []

    for line in output.splitlines():

        line = line.strip()

        # Ignore les lignes inutiles.
        if not line:
            continue

        if line.startswith("Interface"):
            continue

        # Découpe la ligne sur les espaces.
        fields = line.split()

        # Une ligne valide doit contenir au minimum
        # interface + IP + status + protocol.
        if len(fields) < 6:
            continue

        interface = fields[0]
        ip = fields[1]

        # On ne garde que les lignes possédant
        # une adresse IPv4 valide.
        if ip == "unassigned":
            continue

        # Dans "show ip interface brief", les deux derniers
        # champs correspondent généralement au Status et au Protocol.
        status = fields[-2]
        protocol = fields[-1]

        addresses.append({
            "router": router_name,
            "interface": interface,
            "ip": ip,
            "status": status,
            "protocol": protocol,
        })

    return addresses


# ====================================================================
# Configuration complète d'un routeur
# ====================================================================

def configure_router(
    router_name,
    device,
    interfaces
):
    """
    Configure un routeur complet.

    Retourne :
        - True/False pour le résultat
        - la liste des interfaces détectées
    """

    connection = None
    addresses = []

    try:

        print()
        print("=" * 80)
        print(f" ROUTEUR : {router_name}")
        print("=" * 80)

        # ------------------------------------------------------------
        # Connexion
        # ------------------------------------------------------------

        connection = connect_router(
            router_name,
            device
        )

        # ------------------------------------------------------------
        # Désactivation du paging IOS
        # ------------------------------------------------------------

        connection.send_command(
            "terminal length 0"
        )

        # ------------------------------------------------------------
        # Passage en mode privilégié
        # ------------------------------------------------------------

        try:
            connection.enable()
        except Exception:
            # Certains labs GNS3 arrivent déjà en mode privilégié.
            pass

        # ------------------------------------------------------------
        # Configuration IP
        # ------------------------------------------------------------

        configure_interfaces(
            connection,
            router_name,
            interfaces
        )

        # Petite pause pour laisser IOS traiter les commandes.
        time.sleep(1)

        # ------------------------------------------------------------
        # Vérification
        # ------------------------------------------------------------

        verification = verify_interfaces(
            connection,
            router_name
        )

        # ------------------------------------------------------------
        # Extraction des adresses IP
        # ------------------------------------------------------------

        addresses = parse_interface_brief(
            verification,
            router_name
        )

        # ------------------------------------------------------------
        # Sauvegarde
        # ------------------------------------------------------------

        save_configuration(
            connection,
            router_name
        )

        return True, addresses

    except NetmikoTimeoutException:

        print(
            f"[{router_name}] "
            "ERREUR : timeout de connexion."
        )

        return False, addresses

    except NetmikoAuthenticationException:

        print(
            f"[{router_name}] "
            "ERREUR : problème d'authentification."
        )

        return False, addresses

    except Exception as error:

        print(
            f"[{router_name}] "
            f"ERREUR : {error}"
        )

        return False, addresses

    finally:

        # Ferme toujours la connexion.
        if connection:

            try:
                connection.disconnect()
            except Exception:
                pass


# ====================================================================
# Affichage du tableau final
# ====================================================================

def display_final_table(addresses):
    """
    Affiche un tableau regroupant toutes les adresses IP
    détectées sur tous les routeurs.
    """

    print()
    print()
    print("=" * 100)
    print(" TABLEAU FINAL DES ADRESSES IP")
    print("=" * 100)

    # En-tête.
    print(
        f"{'ROUTEUR':<10}"
        f"{'INTERFACE':<25}"
        f"{'ADRESSE IP':<18}"
        f"{'STATUS':<10}"
        f"{'PROTOCOLE':<10}"
    )

    print("-" * 100)

    # Tri :
    #   1. par routeur
    #   2. par interface
    addresses.sort(
        key=lambda x: (
            x["router"],
            x["interface"]
        )
    )

    # Affichage de chaque interface.
    for entry in addresses:

        print(
            f"{entry['router']:<10}"
            f"{entry['interface']:<25}"
            f"{entry['ip']:<18}"
            f"{entry['status']:<10}"
            f"{entry['protocol']:<10}"
        )

    print("=" * 100)

    print(
        f"Total d'interfaces avec une IP : "
        f"{len(addresses)}"
    )

    print()


# ====================================================================
# Affichage du résultat des routeurs
# ====================================================================

def display_router_results(results):
    """
    Affiche un résumé du résultat de la configuration
    de chaque routeur.
    """

    print()
    print("=" * 60)
    print(" RÉSULTAT DE LA CONFIGURATION")
    print("=" * 60)

    print(
        f"{'ROUTEUR':<15}"
        f"{'INTERFACES':<15}"
        f"{'RÉSULTAT'}"
    )

    print("-" * 60)

    success = 0
    failed = 0

    for router, result in results.items():

        number = result["interfaces"]

        if result["success"]:
            status = "OK"
            success += 1
        else:
            status = "ÉCHEC"
            failed += 1

        print(
            f"{router:<15}"
            f"{number:<15}"
            f"{status}"
        )

    print("-" * 60)

    print(f"Succès : {success}")
    print(f"Échecs : {failed}")

    print("=" * 60)


# ====================================================================
# Programme principal
# ====================================================================

def main():

    print()
    print("=" * 80)
    print(" CONFIGURATION AUTOMATIQUE DE L'ADRESSAGE CISCO")
    print(" GNS3 + Netmiko + YAML")
    print("=" * 80)

    # ----------------------------------------------------------------
    # Chargement des fichiers
    # ----------------------------------------------------------------

    devices_config = load_yaml(
        DEVICES_FILE
    )

    interfaces_config = load_yaml(
        INTERFACES_FILE
    )

    # ----------------------------------------------------------------
    # Validation
    # ----------------------------------------------------------------

    validate_config(
        devices_config,
        interfaces_config
    )

    devices = devices_config["devices"]
    interfaces = interfaces_config["interfaces"]

    # ----------------------------------------------------------------
    # Résumé
    # ----------------------------------------------------------------

    print()
    print(
        f"Nombre de routeurs : "
        f"{len(interfaces)}"
    )

    print()
    print("Routeurs à configurer :")

    for router in interfaces:

        print(
            f"  - {router:<10} "
            f"{len(interfaces[router])} interface(s)"
        )

    # ----------------------------------------------------------------
    # Demande de confirmation
    # ----------------------------------------------------------------

    print()
    print("=" * 80)
    print(" ATTENTION")
    print("=" * 80)

    print(
        "Le script va modifier l'adressage IP "
        "des interfaces des routeurs."
    )

    print(
        "Les interfaces seront également activées "
        "avec 'no shutdown'."
    )

    print(
        "La configuration sera sauvegardée."
    )

    print()

    confirmation = input(
        "Tape CONFIGURE pour continuer : "
    )

    if confirmation != "CONFIGURE":

        print()
        print("Opération annulée.")
        return

    # ----------------------------------------------------------------
    # Configuration de tous les routeurs
    # ----------------------------------------------------------------

    results = {}

    all_addresses = []

    for router_name, router_interfaces in interfaces.items():

        device = devices[router_name]

        success, addresses = configure_router(
            router_name,
            device,
            router_interfaces
        )

        # Sauvegarde du résultat.
        results[router_name] = {
            "success": success,
            "interfaces": len(router_interfaces),
        }

        # Ajout des interfaces trouvées
        # dans le tableau global.
        all_addresses.extend(addresses)

        # Pause entre deux routeurs.
        time.sleep(1)

    # ----------------------------------------------------------------
    # Résumé des routeurs
    # ----------------------------------------------------------------

    display_router_results(
        results
    )

    # ----------------------------------------------------------------
    # Tableau final des adresses IP
    # ----------------------------------------------------------------

    display_final_table(
        all_addresses
    )

    # ----------------------------------------------------------------
    # Fin du programme
    # ----------------------------------------------------------------

    print()
    print("=" * 80)
    print(" CONFIGURATION TERMINÉE")
    print("=" * 80)


# ====================================================================
# Point d'entrée
# ====================================================================

if __name__ == "__main__":
    main()