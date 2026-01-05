# monitoring.py

# === IMPORTS ===
# mysql.connector : Bibliothèque pour se connecter à MySQL
# Installation : pip install mysql-connector-python
import mysql.connector

# subprocess : Module Python standard pour exécuter des commandes système
# Permet de lancer des programmes externes (comme ping)
import subprocess

# socket : Module Python standard pour la communication réseau
# Permet de créer des connexions TCP/IP
import socket

# time : Module Python standard pour les délais et mesures de temps
import time

# datetime : Module Python standard pour manipuler les dates et heures
from datetime import datetime

# threading : Module Python standard pour exécuter du code en parallèle
# Prévu pour améliorer les performances futures
import threading


# === CLASSE PRINCIPALE ===
class MonitoringReseau: 
    def __init__(self, db_config):
        """
        Constructeur de la classe MonitoringReseau.
        Initialise la connexion à la base de données MySQL.
        
        Cette méthode est appelée automatiquement quand on crée un objet :
        monitoring = MonitoringReseau(config)
        
        Paramètres:
            db_config (dict) : Dictionnaire contenant les infos de connexion MySQL
                              Format : {"host": "...", "user": "...", "password": "...", "database": "..."}
        
        Attributs créés:
            self.db : Objet de connexion MySQL (type MySQLConnection)
            self.cursor : Curseur pour exécuter des requêtes SQL (type MySQLCursor)
        
        Lève:
            mysql.connector.Error : Si la connexion échoue
        """
        # mysql.connector.connect() : Fonction qui établit la connexion à MySQL
        # **db_config : Opérateur de déballage, équivaut à passer host=..., user=..., etc.
        # Retour : Objet MySQLConnection
        self.db = mysql.connector.connect(**db_config)
        
        # self.db.cursor() : Méthode qui crée un curseur pour exécuter des requêtes
        # dictionary=True : Les résultats seront des dict au lieu de tuples
        # Exemple : {"id": 1, "nom": "Serveur"} au lieu de (1, "Serveur")
        self.cursor = self.db.cursor(dictionary=True)
    
    def ping_equipement(self, ip_address):
        try:
            # subprocess.run() : Fonction qui exécute une commande système
            # Paramètres :
            #   - Liste des arguments : ["ping", "-n", "1", ip_address]
            #   - capture_output=True : Capture stdout et stderr
            #   - text=True : Retourne du texte (str) au lieu de bytes
            # Retour : Objet CompletedProcess avec .stdout, .stderr, .returncode
            result = subprocess.run(
                ["ping", "-n", "1", ip_address],  # list[str] : Commande à exécuter
                capture_output=True,              # bool : Capturer la sortie
                text=True                         # bool : Mode texte (pas binaire)
            )
            
            # Vérifier si le ping a réussi en analysant la sortie
            # "Réponse de" : Texte présent dans la sortie Windows française
            # "Reply from" : Texte présent dans la sortie Windows anglaise
            # in : Opérateur Python pour tester la présence d'une sous-chaîne
            if "Réponse de" in result.stdout or "Reply from" in result.stdout:
                # Variable pour stocker le temps de réponse
                # Type : float|None (float ou None si pas trouvé)
                temps = None
                
                # Parcourir chaque ligne de la sortie
                # result.stdout.splitlines() : Méthode qui découpe le texte en lignes
                # Retour : list[str] (liste de chaînes de caractères)
                for line in result.stdout.splitlines():
                    # Chercher la ligne contenant le temps
                    # "Temps=" : Format Windows français
                    # "time=" : Format Windows anglais/Linux
                    if "Temps=" in line or "time=" in line:
                        # Extraire le nombre de millisecondes
                        if "Temps=" in line:
                            # line.split("Temps=")[1] : Découpe la chaîne et prend la partie après "Temps="
                            # .replace("ms", "") : Retire "ms"
                            # .strip() : Retire les espaces
                            # float() : Convertit en nombre décimal
                            temps = float(line.split("Temps=")[1].replace("ms", "").strip())
                        else:
                            temps = float(line.split("time=")[1].replace("ms", "").strip())
                
                # Retourner le résultat positif
                # tuple : (str, float|None, None)
                return ("OK", temps, None)
            else:
                # Pas de réponse = équipement injoignable
                # tuple : (str, None, str)
                return ("CRITICAL", None, "Pas de réponse ICMP")
                
        except Exception as e:
            # Exception : Classe de base de toutes les erreurs Python
            # e : Variable contenant l'objet exception
            # str(e) : Convertit l'exception en chaîne de caractères
            # Exemples d'erreurs possibles : IP invalide, erreur réseau, timeout
            return ("CRITICAL", None, str(e))

    def scan_port(self, ip_address, port):
        # socket.socket() : Fonction qui crée un nouveau socket réseau
        # socket.AF_INET : Constante pour IPv4 (vs AF_INET6 pour IPv6)
        # socket.SOCK_STREAM : Constante pour TCP (vs SOCK_DGRAM pour UDP)
        # Retour : Objet socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # sock.settimeout() : Méthode qui définit le délai d'attente maximum
        # Paramètre : float (en secondes)
        # Si la connexion prend plus de 1 seconde, une exception est levée
        sock.settimeout(1)
        
        try:
            # sock.connect() : Méthode qui tente d'établir une connexion TCP
            # Paramètre : tuple (ip, port) - ATTENTION : doit être un tuple !
            # Si réussit : La connexion est établie
            # Si échoue : Lève une exception socket.error
            sock.connect((ip_address, port))
            
            # sock.close() : Méthode qui ferme proprement la connexion
            # Important pour libérer les ressources système
            sock.close()
            
            # Port ouvert = service actif
            return "OK"
            
        except:
            # except sans type : Capture TOUTES les exceptions
            # Exceptions possibles : socket.timeout, socket.error, ConnectionRefusedError
            # Port fermé, filtré, ou service inactif
            return "CRITICAL"

    def verifier_tous_equipements(self):
        # Requête SQL pour récupérer tous les équipements actifs
        # SELECT * : Sélectionne toutes les colonnes
        # FROM equipements : De la table equipements
        # WHERE actif=1 : Uniquement ceux marqués comme actifs
        self.cursor.execute("SELECT * FROM equipements WHERE actif=1")
        
        # self.cursor.fetchall() : Méthode qui récupère tous les résultats
        # Retour : list[dict] grâce à dictionary=True dans __init__
        # Exemple : [{"id_equipement": 1, "nom": "Serveur", ...}, {...}]
        equipements = self.cursor.fetchall()
        
        # Liste pour stocker les résultats de surveillance
        # Type : list[tuple]
        results = []
        
        # Boucle for : Parcourt chaque équipement
        # e : Variable temporaire contenant un dict (un équipement)
        for e in equipements:
            # === VÉRIFICATION PING ===
            # Appeler la méthode ping_equipement avec l'IP de l'équipement
            # e['adresse_ip'] : Accès au dictionnaire avec la clé 'adresse_ip'
            # ping_res : tuple (statut, temps, message)
            ping_res = self.ping_equipement(e['adresse_ip'])
            
            # Ajouter le résultat à la liste
            # .append() : Méthode qui ajoute un élément à la fin d'une liste
            results.append((e['nom'], e['adresse_ip'], ping_res))
            
            # === ENREGISTREMENT DANS LA TABLE CHECKS ===
            # INSERT INTO : Commande SQL pour insérer une nouvelle ligne
            # VALUES (%s, %s, ...) : Placeholders pour éviter l'injection SQL
            self.cursor.execute(
                "INSERT INTO checks (id_equipement, type_check, resultat, temps_reponse, message) "
                "VALUES (%s, %s, %s, %s, %s)",
                (
                    e['id_equipement'],  # int : ID de l'équipement
                    'Ping',              # str : Type de vérification
                    ping_res[0],         # str : Statut (OK ou CRITICAL)
                    ping_res[1],         # float|None : Temps en ms
                    ping_res[2]          # str|None : Message d'erreur
                )
            )
            
            # self.db.commit() : Méthode qui valide la transaction SQL
            # Sans commit(), les changements ne sont pas sauvegardés !
            self.db.commit()
            
            # === GÉNÉRATION D'ALERTE SI PROBLÈME ===
            # if : Structure conditionnelle Python
            # == : Opérateur de comparaison (égalité)
            if ping_res[0] == "CRITICAL":
                # Appeler la méthode pour créer une alerte
                # f"..." : f-string (formatted string literal)
                # {variable} : Insère la valeur de la variable
                self.generer_alerte(
                    e['id_equipement'],                           # int : ID équipement
                    "CRITICAL",                                   # str : Niveau
                    f"Équipement {e['nom']} injoignable",        # str : Titre
                    f"Pas de réponse ping pour {e['adresse_ip']}" # str : Message
                )
            
            # === VÉRIFICATION DES PORTS ===
            # Récupérer la liste des ports à surveiller pour cet équipement
            self.cursor.execute(
                "SELECT numero_port FROM ports_surveilles WHERE id_equipement=%s",
                (e['id_equipement'],)  # tuple avec un seul élément (virgule obligatoire !)
            )
            
            # ports : list[dict] avec les numéros de ports
            # Exemple : [{"numero_port": 80}, {"numero_port": 443}]
            ports = self.cursor.fetchall()
            
            # Boucle pour scanner chaque port
            # p : dict contenant {"numero_port": 80}
            for p in ports:
                # Appeler la méthode de scan
                # p['numero_port'] : int, numéro du port
                # port_res : str ("OK" ou "CRITICAL")
                port_res = self.scan_port(e['adresse_ip'], p['numero_port'])
                
                # Enregistrer le résultat du scan
                self.cursor.execute(
                    "INSERT INTO checks (id_equipement, type_check, resultat, message) "
                    "VALUES (%s, %s, %s, %s)",
                    (
                        e['id_equipement'],              # int : ID équipement
                        'Port',                          # str : Type = Port
                        port_res,                        # str : OK ou CRITICAL
                        f"Port {p['numero_port']}"       # str : Description
                    )
                )
                self.db.commit()
                
                # Alerte si le port est fermé
                if port_res == "CRITICAL":
                    self.generer_alerte(
                        e['id_equipement'],
                        "CRITICAL",
                        f"Port {p['numero_port']} fermé",
                        f"Le port {p['numero_port']} est inaccessible sur {e['nom']}"
                    )
        
        # Retourner la liste des résultats
        # return : Mot-clé pour retourner une valeur depuis une fonction
        return results

    def generer_alerte(self, id_equipement, niveau, titre, message):
        # INSERT INTO alertes : Commande SQL pour créer une alerte
        # Les colonnes date_creation et statut ont des valeurs par défaut
        # date_creation : DEFAULT CURRENT_TIMESTAMP (remplie automatiquement)
        # statut : DEFAULT 'Ouverte'
        self.cursor.execute(
            "INSERT INTO alertes (id_equipement, niveau, titre, message) "
            "VALUES (%s,%s,%s,%s)",
            (id_equipement, niveau, titre, message)  # tuple : Les 4 valeurs
        )
        
        # Sauvegarder l'alerte en base
        self.db.commit()

    def calculer_statistiques_journalieres(self):
        # Récupérer tous les équipements (actifs et inactifs)
        self.cursor.execute("SELECT * FROM equipements")
        equipements = self.cursor.fetchall()
        
        # datetime.now() : Fonction qui retourne la date/heure actuelle
        # .date() : Méthode qui extrait uniquement la partie date (sans l'heure)
        # Type : datetime.date
        today = datetime.now().date()
        
        # Parcourir chaque équipement
        for e in equipements:
            # === AGRÉGATION DES CHECKS DU JOUR ===
            # Requête SQL complexe avec fonctions d'agrégation :
            # - COUNT(*) : Compte le nombre total de lignes
            # - SUM(CASE WHEN ...) : Compte conditionnelle (combien de OK, WARNING, etc.)
            # - AVG(temps_reponse) : Moyenne arithmétique du temps de réponse
            # - DATE(date_check) : Extrait la partie date (ignore l'heure)
            self.cursor.execute(
                "SELECT "
                "COUNT(*) as total, "  # int : Nombre total de checks
                "SUM(CASE WHEN resultat='OK' THEN 1 ELSE 0 END) as ok, "  # int : Nb de OK
                "SUM(CASE WHEN resultat='WARNING' THEN 1 ELSE 0 END) as warning, "  # int : Nb WARNING
                "SUM(CASE WHEN resultat='CRITICAL' THEN 1 ELSE 0 END) as critical, "  # int : Nb CRITICAL
                "AVG(temps_reponse) as avg_time "  # float|None : Temps moyen en ms
                "FROM checks "
                "WHERE id_equipement=%s AND DATE(date_check)=%s",
                (e['id_equipement'], today)
            )
            
            # self.cursor.fetchone() : Méthode qui récupère UNE SEULE ligne
            # Retour : dict avec les clés 'total', 'ok', 'warning', 'critical', 'avg_time'
            stats = self.cursor.fetchone()
            
            # === CALCUL DU TAUX DE DISPONIBILITÉ ===
            # Vérifier s'il y a des checks (éviter la division par zéro)
            if stats['total'] == 0:
                taux = 0  # Aucun check = disponibilité inconnue = 0%
            else:
                # Formule : (nombre de checks OK / nombre total) * 100
                # Type : float (nombre décimal)
                # Exemple : (90 / 100) * 100 = 90.0
                taux = (stats['ok'] / stats['total']) * 100
            
            # === VÉRIFIER SI DES STATS EXISTENT DÉJÀ ===
            # Pour éviter les doublons si on relance le calcul dans la même journée
            self.cursor.execute(
                "SELECT id_stat FROM statistiques_disponibilite "
                "WHERE id_equipement=%s AND date=%s",
                (e['id_equipement'], today)
            )
            
            # existing : dict|None (None si aucune ligne trouvée)
            existing = self.cursor.fetchone()
            
            # === UPDATE OU INSERT ===
            # if/else : Structure conditionnelle
            if existing:
                # Des stats existent déjà : faire un UPDATE
                # UPDATE : Modifie une ligne existante
                self.cursor.execute(
                    "UPDATE statistiques_disponibilite SET "
                    "nb_checks_total=%s, nb_checks_ok=%s, "
                    "nb_checks_warning=%s, nb_checks_critical=%s, "
                    "taux_disponibilite=%s, temps_reponse_moyen=%s "
                    "WHERE id_equipement=%s AND date=%s",
                    (
                        stats['total'],      # int : Total de checks
                        stats['ok'],         # int : Nombre OK
                        stats['warning'],    # int : Nombre WARNING
                        stats['critical'],   # int : Nombre CRITICAL
                        taux,                # float : Taux en %
                        stats['avg_time'],   # float|None : Temps moyen
                        e['id_equipement'],  # int : WHERE condition
                        today                # date : WHERE condition
                    )
                )
            else:
                # Aucune stats : faire un INSERT
                # INSERT : Crée une nouvelle ligne
                self.cursor.execute(
                    "INSERT INTO statistiques_disponibilite "
                    "(id_equipement,date,nb_checks_total,nb_checks_ok,"
                    "nb_checks_warning,nb_checks_critical,taux_disponibilite,temps_reponse_moyen) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                    (
                        e['id_equipement'],  # int
                        today,               # date
                        stats['total'],      # int
                        stats['ok'],         # int
                        stats['warning'],    # int
                        stats['critical'],   # int
                        taux,                # float
                        stats['avg_time']    # float|None
                    )
                )
        
        # Sauvegarder toutes les modifications
        self.db.commit()