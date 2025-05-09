#!/usr/bin/env python3

import subprocess
import re

ASTERISK_CLI = 'asterisk -rx'  # Chemin vers l'interface de commande d'Asterisk

def get_active_pjsip_endpoint_details():
    """
    Récupère les détails (numéro, IP, statut, RTT) des endpoints PJSIP actifs (enregistrés) dans Asterisk.

    Returns:
        list: Une liste de dictionnaires, où chaque dictionnaire contient les détails d'un endpoint actif.
              Chaque dictionnaire a les clés: 'numero', 'ip', 'statut', 'rtt_ms'.
              Retourne une liste vide en cas d'erreur ou si aucun contact n'est trouvé.
    """
    active_endpoints_details = []
    try:
        # Commande Asterisk CLI pour afficher les contacts PJSIP actifs
        command = f"{ASTERISK_CLI} 'pjsip show contacts'"
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        output = result.stdout

        # Analyse de la sortie pour extraire les informations
        contact_pattern = re.compile(r"Contact:\s+(?P<aor>\S+)/sip:(?P<numero>\S+)@(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):\d+;.*?\s+(?P<hash>\S+)\s+(?P<statut>\S+)\s+(?P<rtt>\S+)", re.MULTILINE)

        for line in output.splitlines():
            match = contact_pattern.search(line)
            if match:
                aor = match.group('aor')
                numero = match.group('numero')
                ip = match.group('ip')
                statut = match.group('statut')
                rtt_ms_str = match.group('rtt')

                # Gérer le cas où RTT est vide ou non numérique
                try:
                    rtt_ms = float(rtt_ms_str) if rtt_ms_str != '-' else None
                except ValueError:
                    rtt_ms = None

                active_endpoints_details.append({
                    'numero': numero,
                    'ip': ip,
                    'statut': statut,
                    'rtt_ms': rtt_ms
                })

    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de la commande Asterisk CLI: {e}")
        print(f"Sortie (stdout):\n{e.stdout}")
        if e.stderr:
            print(f"Sortie (stderr):\n{e.stderr}")
        return []
    except FileNotFoundError:
        print(f"Erreur: Le binaire Asterisk CLI '{ASTERISK_CLI}' n'a pas été trouvé. Assurez-vous qu'Asterisk est installé et que le chemin est correct.")
        return []
    except Exception as e:
        print(f"Une erreur inattendue s'est produite: {e}")
        return []

    return active_endpoints_details

if __name__ == "__main__":
    endpoint_details = get_active_pjsip_endpoint_details()
    print(endpoint_details )
    if endpoint_details:
        print("Détails des endpoints PJSIP actifs (enregistrés):")
        for endpoint in endpoint_details:
            print(f"- Numéro: {endpoint['numero']}, IP: {endpoint['ip']}, Statut: {endpoint['statut']}, RTT(ms): {endpoint['rtt_ms']}")
        print("\nSous forme de tableau (liste de dictionnaires):")
        print(endpoint_details)
    else:
        print("Aucun endpoint PJSIP actif (enregistré) trouvé ou une erreur s'est produite.")