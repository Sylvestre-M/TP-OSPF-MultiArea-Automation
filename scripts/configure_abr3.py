#!/usr/bin/env python3

from netmiko import ConnectHandler
from tkinter import Tk, messagebox
import sys


# ============================================================
# PARAMETRES GNS3
# ============================================================

DEVICE = {
    "device_type": "cisco_ios_telnet",
    "host": "127.0.0.1",
    "port": 5007,              # ABR3 -> telnet localhost:5007
    "username": "",            # Laisser vide si aucun username
    "password": "",
    "secret": "",
    "fast_cli": False,
}


# ============================================================
# CONFIGURATION ABR3
# ============================================================

CONFIG = [

    # --------------------------------------------------------
    # Serial2/0 -> BR3
    # Réseau : 10.0.12.0/30
    # --------------------------------------------------------
    "interface Serial2/0",
    "description LINK_TO_BR3",
    "ip address 10.0.12.2 255.255.255.252",
    "no shutdown",
    "exit",

    # --------------------------------------------------------
    # Serial2/1 -> BR4
    # Réseau : 10.0.8.0/30
    # --------------------------------------------------------
    "interface Serial2/1",
    "description LINK_TO_BR4",
    "ip address 10.0.8.2 255.255.255.252",
    "no shutdown",
    "exit",

    # --------------------------------------------------------
    # Serial2/2 -> SR1
    # Area 4
    # Réseau : 10.0.28.0/30
    # --------------------------------------------------------
    "interface Serial2/2",
    "description LINK_TO_SR1",
    "ip address 10.0.28.1 255.255.255.252",
    "no shutdown",
    "exit",

    # --------------------------------------------------------
    # Loopback0
    # Router-ID
    # --------------------------------------------------------
    "interface Loopback0",
    "description OSPF_ROUTER_ID",
    "ip address 7.7.7.7 255.255.255.255",
    "exit",
]


# ============================================================
# OSPF
# ============================================================

OSPF_CONFIG = [

    "router ospf 1",

    # Router-ID ABR3
    "router-id 7.7.7.7",

    # Backbone Area 0
    "network 10.0.8.0 0.0.0.3 area 0",
    "network 10.0.12.0 0.0.0.3 area 0",

    # Area 4
    "network 10.0.28.0 0.0.0.3 area 4",

    # Loopback
    "network 7.7.7.7 0.0.0.0 area 0",

    "exit",
]


# ============================================================
# FONCTION BOITE DE DIALOGUE
# ============================================================

def show_message(title, message, error=False):
    root = Tk()
    root.withdraw()

    if error:
        messagebox.showerror(title, message)
    else:
        messagebox.showinfo(title, message)

    root.destroy()


# ============================================================
# PROGRAMME PRINCIPAL
# ============================================================

def main():

    connection = None

    try:

        print("=" * 65)
        print(" CONFIGURATION ABR3 - GNS3")
        print("=" * 65)

        print("\nConnexion à ABR3...")
        print("Adresse : 127.0.0.1")
        print("Port    : 5007")

        connection = ConnectHandler(**DEVICE)

        print("\n[OK] Connexion établie avec ABR3.")

        # ----------------------------------------------------
        # Passage en mode privilégié
        # ----------------------------------------------------

        if DEVICE["secret"]:
            connection.enable()

        # ----------------------------------------------------
        # NETTOYAGE DE SERIAL2/3
        # Cette interface n'est PAS utilisée dans la topologie
        # ----------------------------------------------------

        print("\n[1/4] Nettoyage de Serial2/3...")

        cleanup = [
            "default interface Serial2/3"
        ]

        output = connection.send_config_set(cleanup)

        print(output)
        print("[OK] Serial2/3 nettoyée.")

        # ----------------------------------------------------
        # CONFIGURATION DES INTERFACES
        # ----------------------------------------------------

        print("\n[2/4] Configuration des interfaces...")

        output = connection.send_config_set(CONFIG)

        print(output)
        print("[OK] Adressage configuré.")

        # ----------------------------------------------------
        # CONFIGURATION OSPF
        # ----------------------------------------------------

        print("\n[3/4] Configuration OSPF...")

        output = connection.send_config_set(OSPF_CONFIG)

        print(output)
        print("[OK] OSPF configuré.")

        # ----------------------------------------------------
        # SAUVEGARDE
        # ----------------------------------------------------

        print("\n[4/4] Sauvegarde de la configuration...")

        save_output = connection.send_command(
            "write memory",
            expect_string=r"#"
        )

        print(save_output)

        print("[OK] Configuration sauvegardée.")

        # ----------------------------------------------------
        # VERIFICATION
        # ----------------------------------------------------

        print("\n" + "=" * 65)
        print(" VERIFICATION DES INTERFACES")
        print("=" * 65)

        verification = connection.send_command(
            "show ip interface brief"
        )

        print(verification)

        print("\n" + "=" * 65)
        print(" VOISINAGE OSPF")
        print("=" * 65)

        ospf_neighbors = connection.send_command(
            "show ip ospf neighbor"
        )

        print(ospf_neighbors)

        # ----------------------------------------------------
        # DECONNEXION
        # ----------------------------------------------------

        connection.disconnect()

        print("\n[OK] Déconnexion d'ABR3.")

        # ----------------------------------------------------
        # BOITE DE DIALOGUE
        # ----------------------------------------------------

        show_message(
            "Configuration terminée",
            "La configuration de ABR3 est terminée.\n\n"
            "✓ Adressage configuré\n"
            "✓ Serial2/3 nettoyée\n"
            "✓ OSPF configuré\n"
            "✓ Configuration sauvegardée\n\n"
            "Vérification terminée."
        )

    except Exception as e:

        if connection:
            try:
                connection.disconnect()
            except Exception:
                pass

        print("\n" + "=" * 65)
        print(" ERREUR")
        print("=" * 65)

        print(str(e))

        show_message(
            "Erreur de configuration",
            f"La configuration d'ABR3 a échoué.\n\nErreur :\n{e}",
            error=True
        )

        sys.exit(1)


# ============================================================
# EXECUTION
# ============================================================

if __name__ == "__main__":
    main()