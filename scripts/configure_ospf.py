#!/usr/bin/env python3

"""
====================================================================
CONFIGURATION OSPF MULTI-AREA
====================================================================

Topologie :

    Area 0  : Backbone
    Area 1  : Standard Area
    Area 2  : Totally Stubby
    Area 3  : NSSA
    Area 4  : Stub

Fonctions :

    - Connexion Telnet GNS3
    - Configuration du process OSPF
    - Configuration du router-id
    - Configuration des network statements
    - Configuration des types de zones
    - Vérification OSPF
    - Sauvegarde startup-config
    - Backup running-config
    - Rapport final

Le script ne configure PAS les adresses IP.

Prérequis :

    pip install netmiko pyyaml
"""


import os
import sys
import time
import yaml

from netmiko import ConnectHandler
from netmiko.exceptions import (
    NetmikoTimeoutException,
    NetmikoAuthenticationException,
)


# ====================================================================
# FICHIERS
# ====================================================================

DEVICES_FILE = "config/devices.yaml"
OSPF_FILE = "config/ospf.yaml"

BACKUP_DIR = "configs"


# ====================================================================
# CHARGEMENT YAML
# ====================================================================

def load_yaml(filename):

    try:

        with open(
            filename,
            "r",
            encoding="utf-8"
        ) as file:

            return yaml.safe_load(file)

    except FileNotFoundError:

        print(
            f"[ERREUR] Fichier introuvable : {filename}"
        )

        sys.exit(1)

    except yaml.YAMLError as error:

        print(
            f"[ERREUR] YAML invalide : {filename}"
        )

        print(error)

        sys.exit(1)


# ====================================================================
# CONNEXION
# ====================================================================

def connect_router(router_name, device):

    parameters = {

        "device_type": device.get(
            "device_type",
            "cisco_ios_telnet"
        ),

        "host": device.get(
            "host",
            "127.0.0.1"
        ),

        "port": int(
            device["port"]
        ),

        "username": "",
        "password": "",

        "fast_cli": False,

        "conn_timeout": 10,

        "auth_timeout": 5,

        "banner_timeout": 15,
    }

    print(
        f"[{router_name}] "
        f"Connexion "
        f"{parameters['host']}:{parameters['port']}"
    )

    connection = ConnectHandler(
        **parameters
    )

    connection.send_command(
        "terminal length 0"
    )

    try:

        connection.enable()

    except Exception:

        pass

    print(
        f"[{router_name}] Connexion OK"
    )

    return connection


# ====================================================================
# CONFIGURATION OSPF
# ====================================================================

def configure_ospf(
    connection,
    router_name,
    router_data,
    process_id
):

    router_id = router_data["router_id"]

    areas = router_data.get(
        "areas",
        {}
    )

    commands = [

        f"router ospf {process_id}",

        f"router-id {router_id}",
    ]

    # ------------------------------------------------------------
    # Network statements
    # ------------------------------------------------------------

    for area, networks in areas.items():

        for network in networks:

            # Les Loopbacks sont configurées en /32.
            # On utilise donc une wildcard /32.
            if network == router_id:

                wildcard = "0.0.0.0"

            else:

                wildcard = "0.0.0.3"

            commands.append(
                f"network "
                f"{network} "
                f"{wildcard} "
                f"area {area}"
            )

    print()
    print(
        f"[{router_name}] "
        "Configuration OSPF..."
    )

    output = connection.send_config_set(
        commands,
        cmd_verify=True
    )

    print(
        f"[{router_name}] "
        "OSPF configuré."
    )

    return output


# ====================================================================
# TYPES DE ZONES
# ====================================================================

def configure_area_type(
    connection,
    router_name,
    area_type
):

    commands = []

    # ------------------------------------------------------------
    # Totally Stubby Area
    # ------------------------------------------------------------

    for area, config in area_type.items():

        zone_type = config["type"]

        if zone_type == "totally_stub":

            # ABR1
            if router_name == "ABR1":

                commands.append(
                    f"router ospf 1"
                )

                commands.append(
                    f"area {area} stub no-summary"
                )

            # Routeurs internes
            elif router_name in [
                "TSR1",
                "TSR2",
                "TSR3",
                "TSR4"
            ]:

                commands.append(
                    "router ospf 1"
                )

                commands.append(
                    f"area {area} stub"
                )

    # ------------------------------------------------------------
    # NSSA
    # ------------------------------------------------------------

        elif zone_type == "nssa":

            if router_name in [
                "ABR4",
                "ASBR1",
                "ASBR2",
                "ASBR3"
            ]:

                commands.append(
                    "router ospf 1"
                )

                commands.append(
                    f"area {area} nssa"
                )

    # ------------------------------------------------------------
    # Stub Area
    # ------------------------------------------------------------

        elif zone_type == "stub":

            if router_name == "ABR3":

                commands.append(
                    "router ospf 1"
                )

                commands.append(
                    f"area {area} stub no-summary"
                )

            elif router_name in [
                "SR1",
                "SR2",
                "SR3"
            ]:

                commands.append(
                    "router ospf 1"
                )

                commands.append(
                    f"area {area} stub"
                )

    if commands:

        print(
            f"[{router_name}] "
            "Configuration du type de zone..."
        )

        connection.send_config_set(
            commands,
            cmd_verify=True
        )

        print(
            f"[{router_name}] "
            f"Type de zone configuré."
        )


# ====================================================================
# VÉRIFICATION OSPF
# ====================================================================

def verify_ospf(
    connection,
    router_name
):

    print()
    print(
        f"[{router_name}] "
        "Vérifications OSPF..."
    )

    commands = [

        "show ip ospf",

        "show ip ospf neighbor",

        "show ip route ospf",

        "show ip protocols",
    ]

    results = {}

    for command in commands:

        print(
            f"[{router_name}] "
            f"> {command}"
        )

        try:

            output = connection.send_command(
                command,
                read_timeout=30
            )

            results[command] = output

        except Exception as error:

            results[command] = (
                f"ERREUR : {error}"
            )

    return results


# ====================================================================
# SAUVEGARDE
# ====================================================================

def save_configuration(
    connection,
    router_name
):

    print(
        f"[{router_name}] "
        "write memory..."
    )

    connection.send_command(
        "write memory",
        read_timeout=30
    )

    print(
        f"[{router_name}] "
        "Configuration sauvegardée."
    )


# ====================================================================
# BACKUP CONFIGURATION
# ====================================================================

def backup_configuration(
    connection,
    router_name
):

    os.makedirs(
        BACKUP_DIR,
        exist_ok=True
    )

    print(
        f"[{router_name}] "
        "Backup running-config..."
    )

    configuration = connection.send_command(
        "show running-config",
        read_timeout=60
    )

    filename = os.path.join(
        BACKUP_DIR,
        f"{router_name}.cfg"
    )

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(configuration)

    print(
        f"[{router_name}] "
        f"Backup : {filename}"
    )


# ====================================================================
# TRAITEMENT ROUTEUR
# ====================================================================

def process_router(
    router_name,
    device,
    router_data,
    process_id,
    area_types
):

    connection = None

    try:

        print()
        print("=" * 80)
        print(
            f" ROUTEUR : {router_name}"
        )
        print("=" * 80)

        # ------------------------------------------------------------
        # Connexion
        # ------------------------------------------------------------

        connection = connect_router(
            router_name,
            device
        )

        # ------------------------------------------------------------
        # OSPF
        # ------------------------------------------------------------

        configure_ospf(
            connection,
            router_name,
            router_data,
            process_id
        )

        # ------------------------------------------------------------
        # Type des areas
        # ------------------------------------------------------------

        configure_area_type(
            connection,
            router_name,
            area_types
        )

        # ------------------------------------------------------------
        # Pause
        # ------------------------------------------------------------

        time.sleep(2)

        # ------------------------------------------------------------
        # Vérification
        # ------------------------------------------------------------

        verification = verify_ospf(
            connection,
            router_name
        )

        # ------------------------------------------------------------
        # Sauvegarde
        # ------------------------------------------------------------

        save_configuration(
            connection,
            router_name
        )

        # ------------------------------------------------------------
        # Backup
        # ------------------------------------------------------------

        backup_configuration(
            connection,
            router_name
        )

        return {
            "status": "OK",
            "verification": verification
        }

    except NetmikoTimeoutException:

        print(
            f"[{router_name}] "
            "TIMEOUT"
        )

        return {
            "status": "TIMEOUT"
        }

    except NetmikoAuthenticationException:

        print(
            f"[{router_name}] "
            "AUTHENTIFICATION FAILED"
        )

        return {
            "status": "AUTH ERROR"
        }

    except Exception as error:

        print(
            f"[{router_name}] "
            f"ERREUR : {error}"
        )

        return {
            "status": "ERROR",
            "error": str(error)
        }

    finally:

        if connection:

            try:

                connection.disconnect()

            except Exception:

                pass


# ====================================================================
# RAPPORT
# ====================================================================

def display_report(results):

    print()
    print()
    print("=" * 80)
    print(
        " RAPPORT OSPF FINAL"
    )
    print("=" * 80)

    print(
        f"{'ROUTEUR':<12}"
        f"{'STATUT':<15}"
        f"{'BACKUP'}"
    )

    print("-" * 80)

    success = 0
    failed = 0

    for router, result in results.items():

        status = result["status"]

        if status == "OK":

            backup = "OK"
            success += 1

        else:

            backup = "NON"
            failed += 1

        print(
            f"{router:<12}"
            f"{status:<15}"
            f"{backup}"
        )

    print("-" * 80)

    print(
        f"Routeurs configurés : {success}"
    )

    print(
        f"Routeurs en erreur   : {failed}"
    )

    print("=" * 80)


# ====================================================================
# MAIN
# ====================================================================

def main():

    print()
    print("=" * 80)
    print(
        " OSPF MULTI-AREA - CONFIGURATION AUTOMATIQUE"
    )
    print("=" * 80)

    # ------------------------------------------------------------
    # Chargement
    # ------------------------------------------------------------

    devices_data = load_yaml(
        DEVICES_FILE
    )

    ospf_data = load_yaml(
        OSPF_FILE
    )

    devices = devices_data["devices"]

    ospf = ospf_data["ospf"]

    process_id = ospf.get(
        "process_id",
        1
    )

    routers = ospf["routers"]

    area_types = ospf.get(
        "area_types",
        {}
    )

    # ------------------------------------------------------------
    # Vérification
    # ------------------------------------------------------------

    print()
    print(
        f"Process OSPF : {process_id}"
    )

    print(
        f"Routeurs     : {len(routers)}"
    )

    print()

    for router in routers:

        print(
            f"  - {router:<10} "
            f"RID : "
            f"{routers[router]['router_id']}"
        )

    # ------------------------------------------------------------
    # Confirmation
    # ------------------------------------------------------------

    print()
    print("=" * 80)
    print(
        "ATTENTION : OSPF sera configuré sur "
        "TOUS les routeurs."
    )
    print("=" * 80)

    confirmation = input(
        "\nTape OSPF pour continuer : "
    )

    if confirmation != "OSPF":

        print(
            "Opération annulée."
        )

        return

    # ------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------

    results = {}

    for router_name, router_data in routers.items():

        if router_name not in devices:

            print(
                f"[ERREUR] "
                f"{router_name} absent de devices.yaml"
            )

            results[router_name] = {
                "status": "NO DEVICE"
            }

            continue

        results[router_name] = process_router(
            router_name,
            devices[router_name],
            router_data,
            process_id,
            area_types
        )

        time.sleep(1)

    # ------------------------------------------------------------
    # Rapport
    # ------------------------------------------------------------

    display_report(
        results
    )

    print()
    print(
        "Configuration OSPF terminée."
    )


# ====================================================================
# ENTRY POINT
# ====================================================================

if __name__ == "__main__":

    main()