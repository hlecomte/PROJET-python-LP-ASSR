# cli.py
"""
Interface en ligne de commande du système de monitoring.

"""

#IMPORTS
import mysql.connector  # Connexion MySQL
from datetime import datetime, timedelta  # datetime : Date/heure, timedelta : Différence de temps
import csv  # Module pour lire/écrire des fichiers CSV (Comma-Separated Values)
import json  # Module pour manipuler du JSON (JavaScript Object Notation)
from monitoring import MonitoringReseau  # Notre classe de monitoring
import threading  # Module pour exécuter du code en parallèle
import time  # Module pour les délais (sleep) et timestamps
from dotenv import load_dotenv
import os

load_dotenv()  # 👈 CHERCHE ET CHARGE LE .env

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}


# VARIABLES GLOBALES
# monitoring : Instance (objet) de la classe MonitoringReseau
# Cette variable est partagée par toutes les fonctions du module
monitoring = MonitoringReseau(DB_CONFIG)

# surveillance_thread : Thread qui exécute la surveillance automatique
# Type : threading.Thread|None (peut être None si pas de surveillance active)
# None : Valeur Python représentant "rien" ou "pas d'objet"
surveillance_thread = None

# surveillance_active : Flag (drapeau) pour contrôler le thread
# Type : bool (booléen : True ou False)
# True = la surveillance tourne, False = arrêtée
surveillance_active = False
# FONCTIONS DE GESTION DES ÉQUIPEMENTS
def lister_equipements():
    # SELECT * : Sélectionne toutes les colonnes
    # FROM equipements : De la table equipements
    monitoring.cursor.execute("SELECT * FROM equipements")
    
    # fetchall() : Récupère toutes les lignes du résultat
    # Retour : list[dict] (liste de dictionnaires)
    rows = monitoring.cursor.fetchall()
    
    # print() : Fonction Python pour afficher du texte
    # \n : Caractère spécial pour un saut de ligne
    print("\n=== Équipements ===")
    
    # Boucle for : Parcourt chaque ligne
    # row : dict contenant les infos d'un équipement
    for row in rows:
        # Opérateur ternaire (if/else sur une ligne)
        # Format : valeur_si_vrai if condition else valeur_si_faux
        # row['actif'] : bool ou int (1 = actif, 0 = inactif)
        statut = "Actif" if row['actif'] else "Inactif"
        
        # f-string : Chaîne formatée avec des variables
        # {variable} : Insère la valeur de la variable
        print(f"{row['id_equipement']} - {row['nom']} ({row['type']}) - "
              f"{row['adresse_ip']} - {statut}")
    
    print()  # Ligne vide pour l'espacement


def ajouter_equipement():
    # input() : Fonction Python qui affiche un message et attend une saisie
    # Retour : str (chaîne de caractères tapée par l'utilisateur)
    nom = input("Nom de l'équipement: ")
    type_eq = input("Type (Serveur/Routeur/Switch/Firewall/AP): ")
    ip = input("Adresse IP: ")
    os_eq = input("Système d'exploitation: ")
    localisation = input("Localisation: ")
    
    # Requête SQL d'insertion
    # INSERT INTO : Commande pour ajouter une ligne
    # VALUES (%s, %s, ...) : Placeholders (évite l'injection SQL)
    # """ """ : Triple quotes pour une chaîne multi-lignes
    sql = """INSERT INTO equipements (nom, type, adresse_ip, systeme_exploitation, localisation)
             VALUES (%s, %s, %s, %s, %s)"""
    
    # execute() : Exécute la requête avec les valeurs
    # Le tuple (nom, type_eq, ...) remplace les %s dans l'ordre
    monitoring.cursor.execute(sql, (nom, type_eq, ip, os_eq, localisation))
    
    # commit() : Valide la transaction (sauvegarde définitive)
    monitoring.db.commit()
    
    # Emoji ✅ : Caractère Unicode pour un symbole visuel
    print("Équipement ajouté ✅\n")


def modifier_equipement():
    # Afficher d'abord la liste pour que l'utilisateur sache quel ID choisir
    lister_equipements()
    
    # Demander l'ID
    id_eq = input("ID de l'équipement à modifier: ")
    
    # Demander les nouvelles valeurs (toutes optionnelles)
    nom = input("Nouveau nom (vide = pas de changement): ")
    type_eq = input("Nouveau type (vide = pas de changement): ")
    ip = input("Nouvelle IP (vide = pas de changement): ")
    os_eq = input("Nouveau OS (vide = pas de changement): ")
    loc = input("Nouvelle localisation (vide = pas de changement): ")

    # Listes pour construire la requête dynamiquement
    # updates : list[str] avec les fragments SQL ("nom=%s")
    updates = []
    # params : list avec les valeurs correspondantes
    params = []

    # Pour chaque champ, vérifier s'il est rempli
    # if nom : True si nom n'est pas vide ("" est False en Python)
    if nom:
        updates.append("nom=%s")  # Ajoute le fragment SQL
        params.append(nom)        # Ajoute la valeur
    if type_eq:
        updates.append("type=%s")
        params.append(type_eq)
    if ip:
        updates.append("adresse_ip=%s")
        params.append(ip)
    if os_eq:
        updates.append("systeme_exploitation=%s")
        params.append(os_eq)
    if loc:
        updates.append("localisation=%s")
        params.append(loc)

    # Vérifier s'il y a au moins un champ à modifier
    if updates:
        # ', '.join(updates) : Méthode qui assemble une liste en string
        # Exemple : ["nom=%s", "type=%s"] devient "nom=%s, type=%s"
        sql = f"UPDATE equipements SET {', '.join(updates)} WHERE id_equipement=%s"
        
        # Ajouter l'ID à la fin des paramètres (pour la clause WHERE)
        params.append(id_eq)
        
        # Exécuter l'UPDATE
        monitoring.cursor.execute(sql, params)
        monitoring.db.commit()
        print("Équipement modifié ✅\n")
    else:
        # Aucun champ rempli = aucune modification
        print("Aucune modification.\n")


def supprimer_equipement():
    # Afficher la liste pour choisir
    lister_equipements()
    
    # Demander l'ID à supprimer
    id_eq = input("ID de l'équipement à supprimer: ")
    
    # DELETE FROM : Commande SQL pour supprimer
    # WHERE : Clause pour cibler une ligne spécifique
    sql = "DELETE FROM equipements WHERE id_equipement=%s"
    
    # (id_eq,) : Tuple avec UN SEUL élément (la virgule est obligatoire !)
    # Pourquoi ? Pour différencier (x,) tuple de (x) qui est juste x entre parenthèses
    monitoring.cursor.execute(sql, (id_eq,))
    monitoring.db.commit()
    
    print("Équipement supprimé ✅\n")


def ajouter_port_surveille():
 
    lister_equipements()
    id_eq = input("ID de l'équipement: ")
    port = input("Numéro de port: ")
    service = input("Nom du service (ex: SSH, HTTP): ")
    desc = input("Description: ")
    
    sql = "INSERT INTO ports_surveilles (id_equipement, numero_port, service, description) VALUES (%s,%s,%s,%s)"
    monitoring.cursor.execute(sql, (id_eq, port, service, desc))
    monitoring.db.commit()
    print("Port ajouté ✅\n")


def activer_desactiver_equipement():
    lister_equipements()
    id_eq = input("ID de l'équipement: ")
    action = input("Activer (1) ou Désactiver (0): ")
    
    # UPDATE : Modifie le champ 'actif'
    sql = "UPDATE equipements SET actif=%s WHERE id_equipement=%s"
    monitoring.cursor.execute(sql, (action, id_eq))
    monitoring.db.commit()
    print("Statut modifié ✅\n")


# === FONCTIONS DE SURVEILLANCE ===

def verifier_equipement_specifique():
    lister_equipements()
    id_eq = input("ID de l'équipement à vérifier: ")
    
    # Récupérer les infos de l'équipement
    monitoring.cursor.execute("SELECT * FROM equipements WHERE id_equipement=%s", (id_eq,))
    eq = monitoring.cursor.fetchone()  # fetchone() : Récupère UNE ligne (dict|None)
    
    if eq:  # Si l'équipement existe
        print(f"Vérification de {eq['nom']}...")
        ping_res = monitoring.ping_equipement(eq['adresse_ip'])
        print(f"Ping: {ping_res[0]} - {ping_res[1]}ms")
    else:
        print("Équipement introuvable.\n")


def surveillance_automatique_loop(intervalle):
    # global : Mot-clé pour modifier une variable globale
    # Sans global, on créerait une variable locale du même nom
    global surveillance_active
    
    # Boucle tant que la surveillance est active
    while surveillance_active:
        # datetime.now() : Date/heure actuelle
        # .strftime() : Méthode pour formater en string
        # %H:%M:%S : Format heure:minute:seconde
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Surveillance automatique...")
        
        # Appeler la vérification complète
        monitoring.verifier_tous_equipements()
        
        # time.sleep() : Met le thread en pause pendant X secondes
        # intervalle * 60 : Convertit minutes en secondes
        time.sleep(intervalle * 60)


def lancer_surveillance_auto():
    global surveillance_thread, surveillance_active
    
    # Vérifier si déjà actif
    if surveillance_active:
        print("La surveillance est déjà active.\n")
        return  # return sans valeur : sort de la fonction
    
    # Demander l'intervalle
    # int() : Convertit une string en entier
    intervalle = int(input("Intervalle en minutes (ex: 5): "))
    
    # Activer le flag
    surveillance_active = True
    
    # Créer le thread
    # threading.Thread() : Crée un nouveau thread
    # target= : Fonction à exécuter dans le thread
    # args= : Tuple d'arguments à passer à la fonction
    surveillance_thread = threading.Thread(
        target=surveillance_automatique_loop,
        args=(intervalle,)  # Tuple avec l'intervalle
    )
    
    # daemon=True : Le thread se terminera avec le programme principal
    # Sans daemon, le thread empêcherait le programme de se fermer
    surveillance_thread.daemon = True
    
    # start() : Démarre l'exécution du thread
    surveillance_thread.start()
    
    print(f"Surveillance automatique lancée (toutes les {intervalle} min) ✅\n")


def arreter_surveillance_auto():
    global surveillance_active
    
    if not surveillance_active:
        print("Aucune surveillance active.\n")
        return
    
    # Désactiver le flag
    surveillance_active = False
    print("Surveillance automatique arrêtée ✅\n")


# === FONCTIONS DE GESTION DES ALERTES ===

def consulter_alertes():
    # ORDER BY date_creation DESC : Les alertes les plus récentes d'abord
    monitoring.cursor.execute("SELECT * FROM alertes ORDER BY date_creation DESC")
    rows = monitoring.cursor.fetchall()
    
    print("\n=== Alertes ===")
    for row in rows:
        print(f"{row['id_alerte']} - Equip {row['id_equipement']} - "
              f"{row['niveau']} - {row['titre']} - {row['statut']}")
    print()


def alertes_ouvertes():
    monitoring.cursor.execute("SELECT * FROM alertes WHERE statut='Ouverte' ORDER BY date_creation DESC")
    rows = monitoring.cursor.fetchall()
    
    print("\n=== Alertes Ouvertes ===")
    for row in rows:
        print(f"{row['id_alerte']} - {row['niveau']} - {row['titre']}")
    print()


def alertes_par_niveau():
    niveau = input("Niveau (INFO/WARNING/CRITICAL): ").upper()  # str en majuscules
    
    # WHERE niveau=%s : Filtre par niveau
    monitoring.cursor.execute("SELECT * FROM alertes WHERE niveau=%s ORDER BY date_creation DESC", (niveau,))
    rows = monitoring.cursor.fetchall()
    
    print(f"\n=== Alertes {niveau} ===")
    for row in rows:
        print(f"{row['id_alerte']} - {row['titre']} - {row['statut']}")
    print()


def resoudre_alerte():
    # Afficher les alertes pour choisir
    consulter_alertes()
    
    id_alerte = input("ID de l'alerte à résoudre: ")
    resolu_par = input("Votre nom: ")
    
    # NOW() : Fonction MySQL pour la date/heure actuelle
    sql = "UPDATE alertes SET statut='Résolue', date_resolution=NOW(), resolu_par=%s WHERE id_alerte=%s"
    monitoring.cursor.execute(sql, (resolu_par, id_alerte))
    monitoring.db.commit()
    
    print("Alerte résolue ✅\n")


# === FONCTIONS DE RAPPORTS ===

def rapport_disponibilite():
    periode = input("Période (jour/semaine/mois): ").lower()  # .lower() : Convertit en minuscules
    today = datetime.now().date()
    
    # Calculer la date de début selon la période
    if periode == "jour":
        date_debut = today
    elif periode == "semaine":
        # timedelta(days=7) : Représente une durée de 7 jours
        # today - timedelta(days=7) : Date d'il y a 7 jours
        date_debut = today - timedelta(days=7)
    elif periode == "mois":
        date_debut = today - timedelta(days=30)
    else:
        print("Période invalide.\n")
        return  # Sortir de la fonction
    
    # Requête avec JOIN et AVG
    # JOIN : Fusionne deux tables sur id_equipement
    # AVG(s.taux_disponibilite) : Moyenne des taux
    # GROUP BY : Regroupe les lignes par équipement
    monitoring.cursor.execute(
        "SELECT e.nom, AVG(s.taux_disponibilite) as dispo_moy "
        "FROM statistiques_disponibilite s "
        "JOIN equipements e ON s.id_equipement = e.id_equipement "
        "WHERE s.date >= %s "
        "GROUP BY e.nom",
        (date_debut,)
    )
    rows = monitoring.cursor.fetchall()
    
    print(f"\n=== Rapport de disponibilité ({periode}) ===")
    for row in rows:
        # .2f : Format pour afficher 2 décimales (ex: 98.75)
        print(f"{row['nom']}: {row['dispo_moy']:.2f}%")
    print()


def top_equipements_fiables():
    monitoring.cursor.execute(
        "SELECT e.nom, AVG(s.taux_disponibilite) as dispo_moy "
        "FROM statistiques_disponibilite s "
        "JOIN equipements e ON s.id_equipement = e.id_equipement "
        "GROUP BY e.nom "
        "ORDER BY dispo_moy DESC LIMIT 5"  # DESC = Décroissant, LIMIT 5 = Top 5
    )
    rows = monitoring.cursor.fetchall()
    
    print("\n=== Top 5 Équipements Fiables ===")
    # enumerate(rows, 1) : Génère des tuples (index, valeur) en commençant à 1
    for i, row in enumerate(rows, 1):
        print(f"{i}. {row['nom']}: {row['dispo_moy']:.2f}%")
    print()


def top_equipements_problematiques():
    monitoring.cursor.execute(
        "SELECT e.nom, AVG(s.taux_disponibilite) as dispo_moy "
        "FROM statistiques_disponibilite s "
        "JOIN equipements e ON s.id_equipement = e.id_equipement "
        "GROUP BY e.nom "
        "ORDER BY dispo_moy ASC LIMIT 5"  # ASC = Croissant (les pires d'abord)
    )
    rows = monitoring.cursor.fetchall()
    
    print("\n=== Top 5 Équipements Problématiques ===")
    for i, row in enumerate(rows, 1):
        print(f"{i}. {row['nom']}: {row['dispo_moy']:.2f}%")
    print()


def temps_reponse_moyen():
    monitoring.cursor.execute(
        "SELECT e.nom, AVG(s.temps_reponse_moyen) as temps_moy "
        "FROM statistiques_disponibilite s "
        "JOIN equipements e ON s.id_equipement = e.id_equipement "
        "GROUP BY e.nom"
    )
    rows = monitoring.cursor.fetchall()
    
    print("\n=== Temps de réponse moyen ===")
    for row in rows:
        # row['temps_moy'] peut être None si aucune donnée
        # Opérateur ternaire : valeur if condition else autre_valeur
        temps = row['temps_moy'] if row['temps_moy'] else 0
        print(f"{row['nom']}: {temps:.2f}ms")
    print()


def export_csv():
    # Requête avec JOIN pour avoir le nom et l'IP
    monitoring.cursor.execute("""
        SELECT e.nom, e.adresse_ip, a.niveau, a.titre, a.date_creation
        FROM alertes a
        JOIN equipements e ON a.id_equipement = e.id_equipement
        ORDER BY a.date_creation DESC
    """)
    rows = monitoring.cursor.fetchall()
    
    # Générer un nom de fichier unique avec timestamp
    # %Y%m%d_%H%M%S : Format YYYYMMDD_HHMMSS (ex: 20250104_153045)
    filename = f"rapport_alertes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    # with open() : Ouvre un fichier et le ferme automatiquement à la fin
    # 'w' : Mode écriture (write)
    # newline='' : Évite les lignes vides sous Windows
    # encoding='utf-8' : Support des accents français
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        # csv.writer(f) : Crée un objet pour écrire du CSV
        writer = csv.writer(f)
        
        # Écrire la ligne d'en-têtes
        writer.writerow(['Nom', 'IP', 'Niveau', 'Titre', 'Date'])
        
        # Écrire chaque alerte
        for r in rows:
            writer.writerow([r['nom'], r['adresse_ip'], r['niveau'], r['titre'], r['date_creation']])
    
    print(f"Rapport CSV généré: {filename}\n")


def export_json():
    monitoring.cursor.execute("""
        SELECT e.nom, e.adresse_ip, a.niveau, a.titre, a.date_creation
        FROM alertes a
        JOIN equipements e ON a.id_equipement = e.id_equipement
        ORDER BY a.date_creation DESC
    """)
    rows = monitoring.cursor.fetchall()
    
    # Convertir les datetime en string pour JSON
    for r in rows:
        # str() : Convertit n'importe quelle valeur en chaîne de caractères
        r['date_creation'] = str(r['date_creation'])
    
    filename = f"rapport_alertes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # Ouvrir en mode écriture
    with open(filename, 'w', encoding='utf-8') as f:
        # json.dump() : Écrit des données Python en JSON dans un fichier
        # indent=2 : Indentation de 2 espaces (fichier lisible)
        # ensure_ascii=False : Permet les caractères UTF-8 (accents)
        json.dump(rows, f, indent=2, ensure_ascii=False)
    
    print(f"Rapport JSON généré: {filename}\n")


# === FONCTIONS DE STATISTIQUES ===

def taux_disponibilite_global():
    # AVG() : Calcule la moyenne de tous les taux
    monitoring.cursor.execute("SELECT AVG(taux_disponibilite) as taux_global FROM statistiques_disponibilite")
    result = monitoring.cursor.fetchone()
    
    # Gérer le cas où il n'y a pas de données
    taux = result['taux_global'] if result['taux_global'] else 0
    
    print(f"\nTaux de disponibilité global: {taux:.2f}%\n")


def graphique_ascii_7jours():
    today = datetime.now().date()
    # Date d'il y a 6 jours (7 jours incluant aujourd'hui)
    date_debut = today - timedelta(days=6)
    
    # Requête pour les 7 derniers jours
    # GROUP BY date : Regroupe par jour
    monitoring.cursor.execute(
        "SELECT date, AVG(taux_disponibilite) as taux FROM statistiques_disponibilite "
        "WHERE date >= %s GROUP BY date ORDER BY date",
        (date_debut,)
    )
    rows = monitoring.cursor.fetchall()
    
    print("\n=== Disponibilité 7 derniers jours ===")
    for row in rows:
        taux = row['taux'] if row['taux'] else 0
        
        # Calculer le nombre de barres
        # int() : Convertit en entier (tronque les décimales)
        # taux / 5 : 1 barre tous les 5% (100% = 20 barres)
        barres = int(taux / 5)
        
        # '█' * barres : Répète le caractère 'barres' fois
        # Exemple : '█' * 3 = '███'
        print(f"{row['date']} | {'█' * barres} {taux:.1f}%")
    print()


def alertes_par_type():
    # COUNT(*) : Compte le nombre de lignes
    # GROUP BY niveau : Regroupe par niveau (INFO, WARNING, CRITICAL)
    monitoring.cursor.execute("SELECT niveau, COUNT(*) as nb FROM alertes GROUP BY niveau")
    rows = monitoring.cursor.fetchall()
    
    print("\n=== Nombre d'alertes par type ===")
    for row in rows:
        print(f"{row['niveau']}: {row['nb']}")
    print()


def equipements_en_panne():
    # DATE_SUB(NOW(), INTERVAL 10 MINUTE) : Date/heure d'il y a 10 minutes
    monitoring.cursor.execute("""
        SELECT DISTINCT e.nom, e.adresse_ip
        FROM checks c
        JOIN equipements e ON c.id_equipement = e.id_equipement
        WHERE c.resultat = 'CRITICAL'
        AND c.date_check >= DATE_SUB(NOW(), INTERVAL 10 MINUTE)
    """)
    rows = monitoring.cursor.fetchall()
    
    print("\n=== Équipements en panne ===")
    if rows:  # Si la liste n'est pas vide
        for row in rows:
            # ❌ : Emoji croix rouge
            print(f"❌ {row['nom']} ({row['adresse_ip']})")
    else:
        # ✅ : Emoji check vert
        print("✅ Tous les équipements sont OK")
    print()


# === MENU PRINCIPAL ===

def main_menu():
    # while True : Boucle infinie (jusqu'au break)
    while True:
        # Affichage du menu avec caractères spéciaux Unicode pour le cadre
        # ╔═══╗ ║ ╚═══╝ : Caractères pour dessiner des boîtes
        print("╔═══════════════════════════════════════════════╗")
        print("║     SYSTÈME DE MONITORING RÉSEAU              ║")
        print("╠═══════════════════════════════════════════════╣")
        print("║  1. Gestion des équipements                   ║")
        print("║  2. Lancer une surveillance manuelle          ║")
        print("║  3. Consulter les alertes                     ║")
        print("║  4. Générer des rapports                      ║")
        print("║  5. Statistiques de disponibilité             ║")
        print("║  6. Configuration                             ║")
        print("║  7. Quitter                                   ║")
        print("╚═══════════════════════════════════════════════╝")
        
        choix = input("Votre choix: ")

        # === OPTION 1 : GESTION DES ÉQUIPEMENTS ===
        if choix == "1":
            # Sous-menu avec 6 options
            print("\n1. Ajouter\n2. Modifier\n3. Supprimer\n4. Lister\n5. Ajouter port\n6. Activer/Désactiver")
            sous = input("Choix: ")
            
            # elif : "else if" - vérifie une autre condition
            if sous == "1":
                ajouter_equipement()
            elif sous == "2":
                modifier_equipement()
            elif sous == "3":
                supprimer_equipement()
            elif sous == "4":
                lister_equipements()
            elif sous == "5":
                ajouter_port_surveille()
            elif sous == "6":
                activer_desactiver_equipement()
        
        # === OPTION 2 : SURVEILLANCE ===
        elif choix == "2":
            print("\n1. Vérifier tous\n2. Vérifier spécifique\n3. Lancer auto\n4. Arrêter auto")
            sous = input("Choix: ")
            
            if sous == "1":
                print("Surveillance en cours...")
                monitoring.verifier_tous_equipements()
                print("Terminé ✅\n")
            elif sous == "2":
                verifier_equipement_specifique()
            elif sous == "3":
                lancer_surveillance_auto()
            elif sous == "4":
                arreter_surveillance_auto()
        
        # === OPTION 3 : ALERTES ===
        elif choix == "3":
            print("\n1. Toutes\n2. Ouvertes\n3. Par niveau\n4. Résoudre\n5. Historique")
            sous = input("Choix: ")
            
            if sous == "1":
                consulter_alertes()
            elif sous == "2":
                alertes_ouvertes()
            elif sous == "3":
                alertes_par_niveau()
            elif sous == "4":
                resoudre_alerte()
            elif sous == "5":
                consulter_alertes()  # Historique = toutes les alertes
        
        # === OPTION 4 : RAPPORTS ===
        elif choix == "4":
            print("\n1. Disponibilité\n2. Top 5 fiables\n3. Top 5 problèmes\n4. Temps réponse\n5. Export CSV\n6. Export JSON")
            sous = input("Choix: ")
            
            if sous == "1":
                rapport_disponibilite()
            elif sous == "2":
                top_equipements_fiables()
            elif sous == "3":
                top_equipements_problematiques()
            elif sous == "4":
                temps_reponse_moyen()
            elif sous == "5":
                export_csv()
            elif sous == "6":
                export_json()
        
        # === OPTION 5 : STATISTIQUES ===
        elif choix == "5":
            print("\n1. Taux global\n2. Graphique 7j\n3. Alertes par type\n4. Équipements en panne")
            sous = input("Choix: ")
            
            if sous == "1":
                taux_disponibilite_global()
            elif sous == "2":
                graphique_ascii_7jours()
            elif sous == "3":
                alertes_par_type()
            elif sous == "4":
                equipements_en_panne()
        
        # === OPTION 6 : CONFIGURATION ===
        elif choix == "6":
            print("\nConfiguration non implémentée pour le moment.\n")
        
        # === OPTION 7 : QUITTER ===
        elif choix == "7":
            print("Au revoir 👋")
            break  # Sortir de la boucle while = fin du programme
        
        # === CHOIX INVALIDE ===
        else:
            print("Choix invalide.\n")


# === POINT D'ENTRÉE DU PROGRAMME ===
# Ce code s'exécute uniquement si on lance ce fichier directement
# Si on fait "import cli", ce code ne s'exécute pas
if __name__ == "__main__":
    # __name__ : Variable spéciale Python
    # Vaut "__main__" si fichier exécuté directement
    # Vaut "cli" si importé avec "import cli"
    main_menu()
