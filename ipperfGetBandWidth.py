#!/usr/bin/env python3

import subprocess
import argparse
import re

def get_iperf_bandwidth(server_ip, port=5201, duration=10, udp=False, bitrate=None):
    """
    Exécute iperf3 en mode client et récupère la bande passante en Mbits/sec.

    Args:
        server_ip (str): Adresse IP du serveur iperf3.
        port (int): Port du serveur iperf3 (par défaut: 5201).
        duration (int): Durée du test en secondes (par défaut: 10).
        udp (bool): Utiliser le protocole UDP (par défaut: False pour TCP).
        bitrate (str): Débit cible pour UDP (ex: '10M', '100K').

    Returns:
        float or None: La bande passante moyenne en Mbits/sec, ou None en cas d'erreur.
    """
    command = ['iperf3', '-c', server_ip, '-p', str(port), '-t', str(duration)]
    if udp:
        command.append('-u')
        if bitrate:
            command.extend(['-b', bitrate])

    try:
        print(f"Démarrage du test iperf3 vers {server_ip}:{port} ({'UDP' if udp else 'TCP'}) pour {duration} secondes...")
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        output = result.stdout
        print(output)

        bandwidth_match = re.search(r"\[\s*\d+\]\s+0\.00-\d+\.\d+\s+sec\s+[\d\.]+ ([KMGT]?Bytes)\s+([\d\.]+)\s+([KMGT]?bits/sec)", output)
        if bandwidth_match:
            data_size_unit = bandwidth_match.group(1).strip()
            bandwidth_value = float(bandwidth_match.group(2))
            bandwidth_unit = bandwidth_match.group(3).strip()

            # Conversion en Mbits/sec
            if bandwidth_unit.lower() == "kbits/sec":
                bandwidth_mbps = bandwidth_value / 1000
            elif bandwidth_unit.lower() == "mbits/sec":
                bandwidth_mbps = bandwidth_value
            elif bandwidth_unit.lower() == "gbits/sec":
                bandwidth_mbps = bandwidth_value * 1000
            elif bandwidth_unit.lower() == "tbits/sec":
                bandwidth_mbps = bandwidth_value * 1000 * 1000
            else:
                print(f"Unité de bande passante non reconnue: {bandwidth_unit}")
                return None

            print(f"\nBande passante moyenne: {bandwidth_mbps} Mbits/sec")
            return bandwidth_mbps
        else:
            print("Erreur: Impossible de trouver la bande passante dans la sortie d'iperf3.")
            return None

    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution d'iperf3: {e}")
        print(f"Sortie (stdout):\n{e.stdout}")
        if e.stderr:
            print(f"Sortie (stderr):\n{e.stderr}")
        return None
    except FileNotFoundError:
        print("Erreur: La commande 'iperf3' n'a pas été trouvée. Assurez-vous qu'iperf3 est installé.")
        return None
    except Exception as e:
        print(f"Une erreur inattendue s'est produite: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script Python pour exécuter iperf3 et récupérer la bande passante en Mbits/sec.")
    parser.add_argument("server_ip", help="Adresse IP du serveur iperf3.")
    parser.add_argument("-p", "--port", type=int, default=5201, help="Port du serveur iperf3 (par défaut: 5201).")
    parser.add_argument("-t", "--duration", type=int, default=10, help="Durée du test en secondes (par défaut: 10).")
    parser.add_argument("-u", "--udp", action="store_true", help="Utiliser le protocole UDP.")
    parser.add_argument("-b", "--bitrate", help="Débit cible pour UDP (ex: 10M, 100K).")

    args = parser.parse_args()

    bandwidth = get_iperf_bandwidth(args.server_ip, args.port, args.duration, args.udp, args.bitrate)

    if bandwidth is not None:
        print(f"La bande passante moyenne mesurée est de {bandwidth} Mbits/sec.")