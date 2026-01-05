# monitoring.py
import mysql.connector
import subprocess
import socket
from datetime import datetime

class MonitoringReseau:
    """
    Classe principale pour gérer le monitoring des équipements réseau.
    Permet de vérifier la disponibilité des équipements, scanner les ports,
    générer des alertes et calculer des statistiques.
    """
    
    def __init__(self, db_config):
        """
        Initialise la connexion à la base de données.
        
        Args:
            db_config (dict): Dictionnaire contenant les paramètres de connexion à la base de données
                             (host, user, password, database)
        """
        self.db = mysql.connector.connect(**db_config)
        self.cursor = self.db.cursor(dictionary=True)

    def ping_equipement(self, ip_address):
        """
        Effectue un test de ping ICMP vers une adresse IP pour vérifier la disponibilité d'un équipement.
        
        Args:
            ip_address (str): Adresse IP de l'équipement à tester
            
        Returns:
            tuple: (statut, temps_reponse, message_erreur)
                   - statut: "OK" si l'équipement répond, "CRITICAL" sinon
                   - temps_reponse: Temps de réponse en ms si disponible, None sinon
                   - message_erreur: Message d'erreur en cas de problème, None sinon
        """
        try:
            result = subprocess.run(
                ["ping", "-n", "1", ip_address],
                capture_output=True,
                text=True
            )
            if "Réponse de" in result.stdout or "Reply from" in result.stdout:
                temps = None
                for line in result.stdout.splitlines():
                    if "Temps=" in line or "time=" in line:
                        temps = float(line.split("Temps=")[1].replace("ms", "").strip()) if "Temps=" in line else float(line.split("time=")[1].replace("ms", "").strip())
                return ("OK", temps, None)
            else:
                return ("CRITICAL", None, "Pas de réponse ICMP")
        except Exception as e:
            return ("CRITICAL", None, str(e))

    def scan_port(self, ip_address, port):
        """
        Vérifie si un port TCP spécifique est ouvert sur un équipement.
        Tente d'établir une connexion socket pour tester la disponibilité du port.
        
        Args:
            ip_address (str): Adresse IP de l'équipement
            port (int): Numéro du port à tester
            
        Returns:
            str: "OK" si le port est ouvert, "CRITICAL" si le port est fermé ou inaccessible
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        try:
            sock.connect((ip_address, port))
            sock.close()
            return "OK"
        except:
            return "CRITICAL"

    def verifier_tous_equipements(self):
        """
        Lance une vérification complète de tous les équipements actifs.
        Pour chaque équipement :
        - Effectue un test ping
        - Vérifie l'état de tous les ports surveillés
        - Génère des alertes en cas de problème détecté
        
        Returns:
            list: Liste de tuples contenant (nom_equipement, ip, resultat_ping) pour chaque équipement vérifié
        """
        self.cursor.execute("SELECT * FROM equipements WHERE actif=1")
        equipements = self.cursor.fetchall()
        results = []
        for e in equipements:
            # Test de connectivité de base
            ping_res = self.ping_equipement(e['adresse_ip'])
            results.append((e['nom'], e['adresse_ip'], ping_res))
            
            # Vérifie les ports configurés pour surveillance
            self.cursor.execute("SELECT numero_port FROM ports_surveilles WHERE id_equipement=%s", (e['id_equipement'],))
            ports = self.cursor.fetchall()
            for p in ports:
                port_res = self.scan_port(e['adresse_ip'], p['numero_port'])
                if port_res == "CRITICAL":
                    self.generer_alerte(e['id_equipement'], "CRITICAL", f"Port {p['numero_port']} fermé", f"Le port {p['numero_port']} est inaccessible sur {e['nom']}")
        return results

    def generer_alerte(self, id_equipement, niveau, titre, message):
        """
        Crée et enregistre une nouvelle alerte dans la base de données.
        
        Args:
            id_equipement (int): ID de l'équipement concerné par l'alerte
            niveau (str): Niveau de gravité de l'alerte (OK, WARNING, CRITICAL)
            titre (str): Titre court de l'alerte
            message (str): Description détaillée du problème détecté
        """
        self.cursor.execute(
            "INSERT INTO alertes (id_equipement, niveau, titre, message) VALUES (%s,%s,%s,%s)",
            (id_equipement, niveau, titre, message)
        )
        self.db.commit()

    def calculer_statistiques_journalieres(self):
        """
        Calcule et enregistre les statistiques de disponibilité journalières pour tous les équipements.
        Pour chaque équipement, calcule :
        - Le nombre total de vérifications effectuées
        - Le nombre de checks OK, WARNING et CRITICAL
        - Le taux de disponibilité (pourcentage de checks OK)
        - Le temps de réponse moyen
        
        Les statistiques sont calculées pour la journée en cours et insérées dans la table statistiques_disponibilite.
        """
        self.cursor.execute("SELECT * FROM equipements")
        equipements = self.cursor.fetchall()
        today = datetime.now().date()
        
        for e in equipements:
            # Récupère les données de checks de la journée
            self.cursor.execute(
                "SELECT COUNT(*) as total, SUM(CASE WHEN resultat='OK' THEN 1 ELSE 0 END) as ok, "
                "SUM(CASE WHEN resultat='WARNING' THEN 1 ELSE 0 END) as warning, "
                "SUM(CASE WHEN resultat='CRITICAL' THEN 1 ELSE 0 END) as critical, "
                "AVG(temps_reponse) as avg_time "
                "FROM checks WHERE id_equipement=%s AND DATE(date_check)=%s",
                (e['id_equipement'], today)
            )
            stats = self.cursor.fetchone()
            
            # Calcul du taux de disponibilité
            if stats['total'] == 0:
                taux = 0
            else:
                taux = (stats['ok'] / stats['total']) * 100
            
            # Insertion des statistiques dans la base
            self.cursor.execute(
                "INSERT INTO statistiques_disponibilite (id_equipement,date,nb_checks_total,nb_checks_ok,"
                "nb_checks_warning,nb_checks_critical,taux_disponibilite,temps_reponse_moyen) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (e['id_equipement'], today, stats['total'], stats['ok'], stats['warning'], stats['critical'], taux, stats['avg_time'])
            )
        self.db.commit()