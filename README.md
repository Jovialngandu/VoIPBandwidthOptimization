Markdown

# VoIPBandwidthOptimization  Projet d'Optimisation de la Bande Passante VoIP

## Aperçu

Ce projet vise à optimiser dynamiquement la qualité des appels VoIP et l'utilisation de la bande passante pour les endpoints PJSIP d'Asterisk en fonction de la bande passante réseau disponible. Il surveille la bande passante accessible à chaque endpoint connecté et ajuste les codecs autorisés afin de privilégier les codecs à faible bande passante lorsque cela est nécessaire, assurant ainsi la stabilité des appels même dans des conditions de réseau contraintes.

Le projet comprend des scripts pour :

* **Initialiser la Configuration PJSIP :** Configurer les fichiers de configuration PJSIP de base pour Asterisk.
* **Récupérer les Endpoints Actifs :** Obtenir les détails (numéro, IP, statut, RTT) des endpoints PJSIP actuellement enregistrés.
* **Mesurer la Bande Passante :** Effectuer des tests de bande passante vers chaque endpoint actif en utilisant `iperf3`.
* **Gérer les Utilisateurs PJSIP :** Ajouter, modifier, supprimer et afficher les utilisateurs PJSIP et leurs configurations.
* **Optimiser les Codecs :** Ajuster automatiquement les codecs autorisés pour chaque endpoint en fonction de la bande passante mesurée.
* **Recharger Asterisk :** Appliquer les modifications de configuration en rechargeant le cœur d'Asterisk.

## Structure du Projet

Le dépôt contient les fichiers clés suivants :

VoIPBandwidthOptimization/
├── asteriskReload.sh
├── initfile.sh
├── getPjsipEndpoints
├── iperfRuner
├── ipperfGetBandWidth
├── pjsip_manage
├── optimise
└── README.md


* **`asteriskReload.sh`**: Un script shell pour recharger le cœur d'Asterisk, appliquant ainsi toutes les modifications de configuration.
* **`initFiles.sh`**: Un script shell pour initialiser les fichiers de configuration PJSIP de base (`pjsip.conf`, `pjsip_aor.conf`, `pjsip_auth.conf`, `pjsip_endpoints.conf`, `extensions.conf`) avec une structure de base.
* **`getPjsipEndpoints`**: Un script Python pour récupérer les détails (numéro, IP, statut, RTT) des endpoints PJSIP actifs connectés à Asterisk.
* **`iperfRuner`**: Un script shell basique pour démarrer un serveur `iperf3` (probablement utilisé pour les tests ,ce script peut etre utiliser sous Termux).
* **`ipperfGetBandWidth`**: Un script Python pour exécuter `iperf3` en mode client vers un serveur spécifié et récupérer la bande passante en MBit/s.
* **`pjsip_manager`**: Un script Python modulaire pour gérer les utilisateurs PJSIP dans Asterisk, permettant d'ajouter, de modifier, de supprimer et d'afficher les configurations des utilisateurs.
* **`optimizer`**: Le script Python principal qui orchestre la mesure de la bande passante pour chaque endpoint actif et ajuste dynamiquement leurs codecs autorisés en fonction des résultats.
* **`README.md`**: Ce fichier, fournissant une vue d'ensemble et des instructions pour le projet.

## Prérequis

Avant de pouvoir exécuter ce projet, vous devez avoir les éléments suivants installés et configurés sur votre système :

* **Asterisk :** Un serveur Asterisk correctement installé et configuré avec PJSIP activé.
* **`iperf3` :** L'outil de mesure de la bande passante réseau. Assurez-vous qu'il est installé sur la machine où vous exécuterez les tests de bande passante et potentiellement sur le serveur Asterisk si `iperfRuner` y est utilisé.
    ```bash
    sudo apt update
    sudo apt install iperf3
    ```
* **Python 3 :** Python 3 doit être installé sur le système où vous exécuterez les scripts Python.
    ```bash
    sudo apt update
    sudo apt install python3 python3-pip
    ```
* **`argparse` et `configparser` (Bibliothèques Python) :** Ces bibliothèques sont  utilisées par les scripts Python. Elles devraient être incluses dans les installations standard de Python, mais vous pouvez les installer si nécessaire :
    ```bash
    pip install argparse configparser
    ```
* **Permissions :** Les scripts peuvent nécessiter des privilèges `sudo` pour interagir avec les fichiers de configuration d'Asterisk et recharger le service Asterisk.

## Installation et Exécution

Suivez ces étapes pour installer et exécuter le projet d'Optimisation de la Bande Passante VoIP :

1.  **Cloner le Dépôt :**
    ```bash
    git clone [https://github.com/Jovialngandu/VoIPBandwidthOptimization](https://github.com/Jovialngandu/VoIPBandwidthOptimization)
    cd VoIPBandwidthOptimization
    ```

2.  **Initialiser la Configuration PJSIP (Optionnel mais Recommandé pour une Nouvelle Installation) :**
    Exécutez le script `initFiles.sh` pour créer les fichiers de configuration PJSIP de base s'ils n'existent pas.
    ```bash
    sudo bash initFiles.sh
    ```
    **Note :** Examinez et personnalisez les fichiers de configuration dans `/etc/asterisk/` après avoir exécuté ce script pour qu'ils correspondent à votre configuration Asterisk spécifique. Le fichier pjsip.conf et extensions.conf d'asterisk doivent avoir les textes de base surtout s'ils existent dejà
    pjsip.conf_____
    transport-udp]
    type = transport
    protocol = udp
    bind = 0.0.0.0:5060

; Inclusion des autres fichiers
#include pjsip_endpoints.conf
#include pjsip_aor.conf
#include pjsip_auth.conf__
extensions.conf __;EBANDI
[from-internal] ou [default]
;FIN_EBANDI__

4.  **Exécuter le Serveur `iperf3` (Si Nécessaire) :**
    Si vous prévoyez d'exécuter des tests de bande passante depuis le serveur Asterisk vers les endpoints, vous devrez peut-être exécuter un serveur `iperf3` sur les périphériques endpoints. Vous pouvez utiliser le script `iperfRuner` (ou exécuter manuellement `iperf3 -s`) côté endpoint.

5.  **Exécuter le Script d'Optimisation :**
    Exécutez le script Python `optimizer`. Ce script va :
    * Récupérer les endpoints PJSIP actifs.
    * Pour chaque endpoint, exécuter un test de bande passante en utilisant `ipperfGetBandWidth`.
    * En fonction de la bande passante mesurée, ajuster les codecs autorisés pour l'endpoint en utilisant `pjsip_manager`.
    * Recharger le cœur d'Asterisk pour appliquer les modifications en utilisant `asteriskReload.sh`.

    ```bash
    sudo python3 optimiser.py
    ```
    **Note :** Assurez-vous que l'utilisateur `asterisk` a les permissions nécessaires pour lire et écrire les fichiers de configuration PJSIP. Vous devrez peut-être ajuster la propriété des fichiers en utilisant `chown` si vous rencontrez des problèmes de permissions. Vérifiez également que la variable `ASTERISK_CLI` dans les scripts Python (`getPjsipEndpoints`, `ipperfGetBandWidth`, `pjsip_manage`r, `optimizer`) pointe correctement vers votre exécutable de l'interface de commande d'Asterisk (généralement `asterisk -rx`).

## ADD
### Utilisation du Gestionnaire PJSIP (`pjsip_manage.py`)

Ce script Python (`pjsip_manage.py`) fournit une interface en ligne de commande pour gérer les utilisateurs PJSIP dans Asterisk. Vous pouvez l'utiliser pour ajouter, modifier, supprimer et afficher les configurations des utilisateurs.

Voici quelques exemples d'utilisation :

**Ajouter un utilisateur :**

Pour ajouter un nouvel utilisateur avec l'extension `1001`, le mot de passe `motdepasse` et les codecs autorisés `opus` et `g729` :

sudo ./pjsip_manage.py add 1001 motdepasse --codecs "opus,g729"
Modifier un utilisateur :

Pour modifier le mot de passe de l'utilisateur 1001 en nouveaumdp et changer les codecs autorisés en g722 et g711 :

Bash

sudo ./pjsip_manage.py edit 1001 --password nouveaumdp --codecs "g722,g711"
Supprimer un utilisateur :

Pour supprimer complètement l'utilisateur 1001 :

Bash

sudo ./pjsip_manage.py del 1001
Afficher tous les utilisateurs :

Pour lister toutes les extensions PJSIP configurées :

Bash

sudo ./pjsip_manage.py show
Afficher les informations d'un utilisateur spécifique :

Pour afficher la configuration détaillée de l'utilisateur 1001 (endpoints, AOR, authentification) :


sudo ./pjsip_manage.py show 1001
Note importante : L'exécution de ces commandes nécessite généralement des privilèges sudo car elles modifient les fichiers de configuration d'Asterisk. Assurez-vous d'avoir les permissions nécessaires.
## Configuration

* **`initfile.sh` :** Modifiez les variables au début du script (`CONF_DIR`, `FILES`, et le contenu de chaque fichier de configuration) pour ajuster la configuration PJSIP initiale.
* **Scripts Python (`getPjsipEndpoints`, `ipperfGetBandWidth`, `pjsip_manager`, `optimizer`) :**
    * **`ASTERISK_CLI` :** Assurez-vous que cette variable pointe vers le chemin correct de l'exécutable de l'interface de commande d'Asterisk.
    * **`ipperfGetBandWidth` :** Vous devrez peut-être ajuster le port de serveur `iperf3` par défaut (`5201`) ou d'autres paramètres si votre configuration est différente.
    * **`pjsip_manage` :** Examinez la liste des codecs par défaut et la logique d'ajout/modification des utilisateurs.
    * **`optimizer` :** Les seuils d'ajustement des codecs (par exemple, `0.064`, `0.008` MBit/s) peuvent être modifiés pour affiner le comportement de l'optimisation en fonction des exigences de votre réseau et de vos préférences de codecs. L'intervalle d'exécution de l'optimisation est actuellement codé en dur dans le script `optimizre` (par exemple, `5 * 60 * len(endp)` secondes). Vous pourriez préférer l'ajuster ou utiliser un planificateur externe comme `cron`.

## Contribution

Les contributions à ce projet sont les bienvenues. N'hésitez pas à forker le dépôt et à soumettre des pull requests avec vos améliorations ou corrections de bugs.

## Licence

[Spécifiez la licence de votre projet ici, par exemple, Licence MIT]



