#!/usr/bin/env python3
import os
import re
import argparse
from configparser import ConfigParser

# Configuration des chemins
CONF_DIR = "/etc/asterisk"
PJSIP_MAIN = os.path.join(CONF_DIR, "pjsip.conf")
PJSIP_AOR = os.path.join(CONF_DIR, "pjsip_aor.conf")
PJSIP_AUTH = os.path.join(CONF_DIR, "pjsip_auth.conf")
PJSIP_ENDPOINT = os.path.join(CONF_DIR, "pjsip_endpoints.conf")
EXTENSIONS_CONF = os.path.join(CONF_DIR, "extensions.conf")

def check_config_files():
    """Vérifie et initialise les fichiers de configuration si absents"""
    if not os.path.exists(PJSIP_MAIN):
        with open(PJSIP_MAIN, 'w') as f:
            f.write("""[transport-udp]
type = transport
protocol = udp
bind = 0.0.0.0:5060
#include pjsip_endpoints.conf
#include pjsip_aor.conf
#include pjsip_auth.conf

""")

    if not os.path.exists(EXTENSIONS_CONF):
        with open(EXTENSIONS_CONF, 'w') as f:
            f.write("""[default]
;EBANDI
;FIN_EBANDI
""")

    for f in [PJSIP_AOR, PJSIP_AUTH, PJSIP_ENDPOINT]:
        if not os.path.exists(f):
            open(f, 'a').close()

class PJSIPManager:
    def __init__(self):
        self.configs = {
            'aor': ConfigParser(allow_no_value=True),
            'auth': ConfigParser(allow_no_value=True),
            'endpoint': ConfigParser(allow_no_value=True)
        }
        self.configs['aor'].read(PJSIP_AOR)
        self.configs['auth'].read(PJSIP_AUTH)
        self.configs['endpoint'].read(PJSIP_ENDPOINT)

    def _save_configs(self):
        """Sauvegarde toutes les configurations"""
        with open(PJSIP_AOR, 'w') as f:
            self.configs['aor'].write(f)
        with open(PJSIP_AUTH, 'w') as f:
            self.configs['auth'].write(f)
        with open(PJSIP_ENDPOINT, 'w') as f:
            self.configs['endpoint'].write(f)

    def add_user(self, extension, password, codecs="opus,alaw,ulaw,g729,gsm"):
        """Ajoute un utilisateur avec cohérence de nommage"""
        # Vérification extension numérique
        if not extension.isdigit():
            raise ValueError("L'extension doit être numérique")

        # Configuration AOR (même nom que l'extension)codecs
        if extension not in self.configs['aor']:
            self.configs['aor'][extension] = {
                'type': 'aor',
                'max_contacts': '1',
                'qualify_frequency': '60'
            }

        # Configuration Auth (suffixe -auth)
        auth_section = f"{extension}-auth"
        if auth_section not in self.configs['auth']:
            self.configs['auth'][auth_section] = {
                'type': 'auth',
                'auth_type': 'userpass',
                'username': extension,
                'password': password
            }

        # Configuration Endpoint
        if extension not in self.configs['endpoint']:
            self.configs['endpoint'][extension] = {
                'type': 'endpoint',
                'context': 'default',
                'disallow': 'all',
                'allow': codecs,
                'aors': extension,  # Référence directe à la section AOR
                'auth': auth_section,
                'direct_media': 'no'
            }

        # Ajout dans extensions.conf
        self._update_extensions_conf(extension, action='add')
        self._save_configs()
        print(f"Utilisateur {extension} configuré avec succès")

    def edit_user(self, extension, password=None, codecs=None):
        """Modifie un utilisateur existant"""
        if extension not in self.configs['endpoint']:
            raise ValueError(f"Extension {extension} non trouvée")

        auth_section = f"{extension}-auth"
        
        if password and auth_section in self.configs['auth']:
            self.configs['auth'][auth_section]['password'] = password
            
        if codecs and extension in self.configs['endpoint']:
            self.configs['endpoint'][extension]['allow'] = codecs

        self._save_configs()
        print(f"Utilisateur {extension} mis à jour")

    def delete_user(self, extension):
        """Supprime complètement un utilisateur"""
        # Suppression des sections
        for section in [extension, f"{extension}-auth"]:
            if section in self.configs['aor']:
                del self.configs['aor'][section]
            if section in self.configs['auth']:
                del self.configs['auth'][section]
            if section in self.configs['endpoint']:
                del self.configs['endpoint'][section]

        # Suppression de l'extension
        self._update_extensions_conf(extension, action='remove')
        self._save_configs()
        print(f"Utilisateur {extension} supprimé")

    def _update_extensions_conf(self, extension, action='add'):
        """Gère les modifications dans extensions.conf"""
        with open(EXTENSIONS_CONF, 'r+') as f:
            content = f.read()
            
            pattern = re.compile(
                r'(;EBANDI)(.*?)(;FIN_EBANDI)',
                re.DOTALL
            )
            
            if not pattern.search(content):
                content = content.replace(
                    '[default]', 
                    '[default]\n;EBANDI\n;FIN_EBANDI'
                )
            
            if action == 'add':
                new_exten = f"\nexten => {extension},1,Dial(PJSIP/{extension})"
                content = pattern.sub(
                    r'\1\2' + new_exten + r'\n\3',
                    content
                )
            else:
                content = re.sub(
                    rf'\n?exten => {extension},.*?Dial\(PJSIP/{extension}\).*?\n',
                    '',
                    content
                )
            
            f.seek(0)
            f.write(content)
            f.truncate()

    def show_user(self, extension=None):
        """Affiche les informations utilisateur"""
        if extension:
            if extension not in self.configs['endpoint']:
                print(f"Erreur: Extension {extension} non trouvée")
                return

            print(f"\nConfiguration de {extension}:")
            print("="*40)
            
            print("\n[Endpoint]")
            for k, v in self.configs['endpoint'][extension].items():
                print(f"{k:20} = {v}")
                
            print("\n[AOR]")
            if extension in self.configs['aor']:
                for k, v in self.configs['aor'][extension].items():
                    print(f"{k:20} = {v}")
                    
            print("\n[Auth]")
            auth_section = f"{extension}-auth"
            if auth_section in self.configs['auth']:
                print(f"{'username':20} = {self.configs['auth'][auth_section]['username']}")
                print(f"{'password':20} = {'********'}")
        else:
            print("\nExtensions configurées:")
            print("="*40)
            for ext in self.configs['endpoint'].sections():
                print(f"- {ext}")

def main():
    check_config_files()
    manager = PJSIPManager()

    parser = argparse.ArgumentParser(
        description="Gestionnaire PJSIP modulaire pour Asterisk",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Commande add
    add_parser = subparsers.add_parser('add', help='Ajouter un utilisateur')
    add_parser.add_argument('extension', help='Numéro d\'extension (ex: 100)')
    add_parser.add_argument('password', help='Mot de passe SIP')
    add_parser.add_argument('--codecs', 
                          help='Liste des codecs (par défaut: opus,g729)',
                          default='opus,g729,ulaw,alaw,gsm')

    # Commande edit
    edit_parser = subparsers.add_parser('edit', help='Modifier un utilisateur')
    edit_parser.add_argument('extension', help='Numéro d\'extension à modifier')
    edit_parser.add_argument('--password', help='Nouveau mot de passe')
    edit_parser.add_argument('--codecs', help='Nouveaux codecs')

    # Commande del
    del_parser = subparsers.add_parser('del', help='Supprimer un utilisateur')
    del_parser.add_argument('extension', help='Numéro d\'extension à supprimer')

    # Commande show
    show_parser = subparsers.add_parser('show', help='Afficher les informations')
    show_parser.add_argument('extension', nargs='?', 
                           help='Numéro d\'extension (optionnel)')

    args = parser.parse_args()

    try:
        if args.command == 'add':
            manager.add_user(args.extension, args.password, args.codecs)
        elif args.command == 'edit':
            if not any([args.password, args.codecs]):
                parser.error("Spécifier au moins --password ou --codecs")
            manager.edit_user(args.extension, args.password, args.codecs)
        elif args.command == 'del':
            manager.delete_user(args.extension)
        elif args.command == 'show':
            manager.show_user(args.extension)
    except Exception as e:
        print(f"\nErreur: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()