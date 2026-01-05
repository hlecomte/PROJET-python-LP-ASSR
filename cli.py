# cli.py
import mysql.connector
from datetime import datetime
import csv
from monitoring import MonitoringReseau

# Configuration base de données
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'aaaa',
    'database': 'monitoring_reseau'
}

# Initialisation de l'objet de monitoring
monitoring = MonitoringReseau(DB_CONFIG)

def lister_equipements():
    """
    Affiche la liste de tous les équipements réseau enregistrés dans la base de données.
    Pour chaque équipement, affiche l'ID, le nom, le type, l'adresse IP et le statut actif.
    """
    monitoring.cursor.execute("SELECT * FROM equipements")
    rows = monitoring.cursor.fetchall()
    print("\n=== Équipements ===")
    for row in rows:
        print(f"{row['id_equipement']} - {row['nom']} ({row['type']}) - {row['adresse_ip']} - Actif: {row['actif']}")
    print()

def ajouter_equipement():
    """
    Permet d'ajouter un nouvel équipement réseau à la base de données.
    Demande à l'utilisateur de saisir les informations de l'équipement (nom, type, IP, OS, localisation).
    Insère ensuite les données dans la table 'equipements'.
    """
    nom = input("Nom de l'équipement: ")
    type_eq = input("Type (Serveur/Routeur/Switch/Firewall/AP): ")
    ip = input("Adresse IP: ")
    os_eq = input("Système d'exploitation: ")
    localisation = input("Localisation: ")
    sql = """INSERT INTO equipements (nom, type, adresse_ip, systeme_exploitation, localisation)
             VALUES (%s, %s, %s, %s, %s)"""
    monitoring.cursor.execute(sql, (nom, type_eq, ip, os_eq, localisation))
    monitoring.db.commit()
    print("Équipement ajouté ✅\n")

def modifier_equipement():
    """
    Permet de modifier les informations d'un équipement existant.
    Affiche d'abord la liste des équipements, puis demande l'ID de l'équipement à modifier.
    L'utilisateur peut choisir quels champs mettre à jour (laisser vide pour conserver la valeur actuelle).
    """
    lister_equipements()
    id_eq = input("ID de l'équipement à modifier: ")
    nom = input("Nouveau nom (laisser vide pour ne pas changer): ")
    type_eq = input("Nouveau type (laisser vide pour ne pas changer): ")
    ip = input("Nouvelle IP (laisser vide pour ne pas changer): ")
    os_eq = input("Nouveau OS (laisser vide pour ne pas changer): ")
    loc = input("Nouvelle localisation (laisser vide pour ne pas changer): ")

    # Construction dynamique de la requête UPDATE en fonction des champs renseignés
    updates = []
    params = []

    if nom: updates.append("nom=%s"); params.append(nom)
    if type_eq: updates.append("type=%s"); params.append(type_eq)
    if ip: updates.append("adresse_ip=%s"); params.append(ip)
    if os_eq: updates.append("systeme_exploitation=%s"); params.append(os_eq)
    if loc: updates.append("localisation=%s"); params.append(loc)

    if updates:
        sql = f"UPDATE equipements SET {', '.join(updates)} WHERE id_equipement=%s"
        params.append(id_eq)
        monitoring.cursor.execute(sql, params)
        monitoring.db.commit()
        print("Équipement modifié ✅\n")
    else:
        print("Aucune modification effectuée.\n")

def supprimer_equipement():
    """
    Supprime un équipement de la base de données.
    Affiche d'abord la liste des équipements disponibles, puis demande l'ID de l'équipement à supprimer.
    """
    lister_equipements()
    id_eq = input("ID de l'équipement à supprimer: ")
    sql = "DELETE FROM equipements WHERE id_equipement=%s"
    monitoring.cursor.execute(sql, (id_eq,))
    monitoring.db.commit()
    print("Équipement supprimé ✅\n")

def consulter_alertes():
    """
    Affiche toutes les alertes générées par le système de monitoring.
    Les alertes sont triées par date de création (les plus récentes en premier).
    Pour chaque alerte, affiche l'ID, l'équipement concerné, le niveau, le titre et le statut.
    """
    monitoring.cursor.execute("SELECT * FROM alertes ORDER BY date_creation DESC")
    rows = monitoring.cursor.fetchall()
    print("\n=== Alertes ===")
    for row in rows:
        print(f"{row['id_alerte']} - Equip {row['id_equipement']} - {row['niveau']} - {row['titre']} - Statut: {row['statut']}")
    print()

def generer_rapport_csv():
    """
    Génère un rapport CSV contenant toutes les alertes avec les informations des équipements associés.
    Le fichier est nommé avec un horodatage pour éviter les écrasements.
    Inclut le nom de l'équipement, son IP, le niveau d'alerte, le titre et la date de création.
    """
    monitoring.cursor.execute("""
        SELECT e.nom, e.adresse_ip, a.niveau, a.titre, a.date_creation
        FROM alertes a
        JOIN equipements e ON a.id_equipement = e.id_equipement
        ORDER BY a.date_creation DESC
    """)
    rows = monitoring.cursor.fetchall()
    filename = f"rapport_alertes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Nom', 'IP', 'Niveau', 'Titre', 'Date'])
        for r in rows:
            writer.writerow([r['nom'], r['adresse_ip'], r['niveau'], r['titre'], r['date_creation']])
    print(f"Rapport CSV généré: {filename}\n")

def afficher_statistiques():
    """
    Affiche les statistiques de disponibilité des équipements réseau.
    Pour chaque équipement, montre la date et le taux de disponibilité en pourcentage.
    Les résultats sont triés par date (les plus récents en premier).
    """
    monitoring.cursor.execute("SELECT * FROM statistiques_disponibilite ORDER BY date DESC")
    rows = monitoring.cursor.fetchall()
    print("\n=== Statistiques ===")
    for r in rows:
        print(f"Equip {r['id_equipement']} - Date: {r['date']} - Disponibilité: {r['taux_disponibilite']}%")
    print()

def config():
    """
    Section dédiée à la configuration du système de monitoring.
    Actuellement, cette fonctionnalité n'est pas encore implémentée.
    """
    print("\n=== Configuration ===")
    print("Pour l'instant, pas de configuration dynamique implémentée.\n")

def lancer_surveillance():
    """
    Lance manuellement une vérification de tous les équipements réseau.
    Appelle la méthode de monitoring pour vérifier l'état de chaque équipement
    et générer des alertes si nécessaire.
    """
    print("Lancement de la surveillance manuelle...")
    monitoring.verifier_tous_equipements()
    print("Surveillance terminée ✅\n")

def main_menu():
    """
    Affiche le menu principal de l'application et gère la navigation.
    Propose plusieurs options : gestion des équipements, surveillance, consultation des alertes,
    génération de rapports, statistiques, configuration et sortie du programme.
    Boucle jusqu'à ce que l'utilisateur choisisse de quitter.
    """
    while True:
        print("╔════════════════════════════════════════════════╗")
        print("║     SYSTÈME DE MONITORING RÉSEAU              ║")
        print("╠════════════════════════════════════════════════╣")
        print("║  1. Gestion des équipements                    ║")
        print("║  2. Lancer une surveillance manuelle           ║")
        print("║  3. Consulter les alertes                      ║")
        print("║  4. Générer des rapports                       ║")
        print("║  5. Statistiques de disponibilité              ║")
        print("║  6. Configuration                              ║")
        print("║  7. Quitter                                    ║")
        print("╚════════════════════════════════════════════════╝")
        choix = input("Votre choix: ")

        if choix == "1":
            print("\n1. Ajouter\n2. Modifier\n3. Supprimer\n4. Lister")
            sous = input("Choix: ")
            if sous == "1": ajouter_equipement()
            elif sous == "2": modifier_equipement()
            elif sous == "3": supprimer_equipement()
            elif sous == "4": lister_equipements()
        elif choix == "2":
            lancer_surveillance()
        elif choix == "3":
            consulter_alertes()
        elif choix == "4":
            generer_rapport_csv()
        elif choix == "5":
            afficher_statistiques()
        elif choix == "6":
            config()
        elif choix == "7":
            print("Au revoir 👋")
            break
        else:
            print("Choix invalide.\n")

# Point d'entrée du programme
if __name__ == "__main__":
    main_menu()