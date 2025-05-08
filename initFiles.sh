#!/bin/bash
# Script de configuration initiale PJSIP pour Asterisk
# Crée tous les fichiers nécessaires avec la structure de base

# Variables
CONF_DIR="/etc/asterisk"
FILES=(
    "pjsip.conf"
    "pjsip_aor.conf"
    "pjsip_auth.conf"
    "pjsip_endpoints.conf"
    "extensions.conf"
)

# Fonction pour créer un fichier de configuration s'il n'existe pas
create_config_file() {
    local file="$1"
    local content="$2"
    
    if [ ! -f "${CONF_DIR}/${file}" ]; then
        echo "Création de ${file}..."
        echo "$content" > "${CONF_DIR}/${file}"
        chown asterisk:asterisk "${CONF_DIR}/${file}"
        chmod 640 "${CONF_DIR}/${file}"
        echo "  → Fichier ${file} créé avec succès"
    else
        echo "  → Le fichier ${file} existe déjà (non modifié)"
    fi
}

# Contenu des fichiers
PJSIP_CONF="[transport-udp]
type = transport
protocol = udp
bind = 0.0.0.0:5060

; Inclusion des autres fichiers
#include pjsip_aor.conf
#include pjsip_auth.conf
#include pjsip_endpoints.conf"

PJSIP_AOR="; Configuration des AORs (Adresse Of Record)
; Format:
; [nom-aor]
; type = aor
; max_contacts = 5
; qualify_frequency = 60"

PJSIP_AUTH="; Configuration d'authentification
; Format:
; [nom-auth]
; type = auth
; auth_type = userpass
; username = extension
; password = motdepasse"

PJSIP_ENDPOINT="; Configuration des endpoints
; Format:
; [extension]
; type = endpoint
; context = from-internal
; disallow = all
; allow = opus,g729
; aors = nom-aor
; auth = nom-auth
; direct_media = no"

EXTENSIONS_CONF=";EBANDI
[from-internal]
;FIN_EBANDI"

# Début du script
echo "===================================="
echo " Configuration PJSIP pour Asterisk"
echo "===================================="

# Vérification des permissions
if [ "$(id -u)" -ne 0 ]; then
    echo "ERREUR: Ce script doit être exécuté en tant que root" >&2
    exit 1
fi

# Vérification du répertoire de configuration
if [ ! -d "$CONF_DIR" ]; then
    echo "ERREUR: Répertoire $CONF_DIR introuvable" >&2
    exit 1
fi

# Création des fichiers
echo "Création des fichiers de configuration..."
create_config_file "pjsip.conf" "$PJSIP_CONF"
create_config_file "pjsip_aor.conf" "$PJSIP_AOR"
create_config_file "pjsip_auth.conf" "$PJSIP_AUTH"
create_config_file "pjsip_endpoints.conf" "$PJSIP_ENDPOINT"
create_config_file "extensions.conf" "$EXTENSIONS_CONF"

# Vérification finale
echo ""
echo "Résumé des fichiers créés :"
echo "--------------------------"
for file in "${FILES[@]}"; do
    if [ -f "${CONF_DIR}/${file}" ]; then
        echo "✓ ${file}"
    else
        echo "✗ ${file} (erreur de création)"
    fi
done

echo ""
echo "Configuration terminée avec succès !"
echo "Redémarrez Asterisk pour appliquer les changements :"
echo "  systemctl restart asterisk"