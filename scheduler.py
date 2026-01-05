# scheduler.py

# === IMPORTS ===
# schedule : Bibliothèque tierce pour planifier des tâches périodiques
# Installation : pip install schedule
# Documentation : https://schedule.readthedocs.io/
import schedule

# time : Module Python standard pour les délais et mesures de temps
import time

# Importer notre classe de monitoring
from monitoring import MonitoringReseau
# === CHARGEMENT DES VARIABLES D’ENVIRONNEMENT ===
from dotenv import load_dotenv
import os

load_dotenv()  # Charge le fichier .env
# === CONFIGURATION DEPUIS LE .env ===

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

INTERVALLE_SURVEILLANCE = int(os.getenv("INTERVALLE_SURVEILLANCE", 5))
HEURE_STATS = os.getenv("HEURE_STATISTIQUES", "00:00")

SEUIL_WARNING = int(os.getenv("SEUIL_WARNING", 100))
SEUIL_CRITICAL = int(os.getenv("SEUIL_CRITICAL", 500))


# Importer la configuration depuis config.py
# DB_CONFIG : dict avec les paramètres MySQL
# INTERVALLE_SURVEILLANCE : int (minutes entre chaque vérification)
# HEURE_STATS : str (heure du calcul des stats au format "HH:MM")

# === INITIALISATION ===
# Créer l'instance de monitoring une seule fois
# Type : MonitoringReseau
# Réutilisée par toutes les fonctions de ce module
monitoring = MonitoringReseau(DB_CONFIG)


# === FONCTIONS DE TÂCHES ===

def job_surveillance():
    # time.strftime() : Fonction qui formate la date/heure actuelle
    # %Y-%m-%d : Format YYYY-MM-DD (ex: 2025-01-04)
    # %H:%M:%S : Format HH:MM:SS (ex: 15:30:45)
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Lancement de la surveillance...")
    
    # try/except : Structure pour gérer les erreurs
    try:
        # Appeler la méthode de vérification
        # results : list[tuple] avec (nom, ip, (statut, temps, message))
        results = monitoring.verifier_tous_equipements()
        
        # len() : Fonction qui retourne la longueur d'une liste
        print(f"  → {len(results)} équipements vérifiés")
        
        # Parcourir chaque résultat pour l'afficher
        # Déballage de tuple : nom, ip, (statut, temps, msg) = ...
        for nom, ip, (statut, temps, msg) in results:
            # if/else : Affichage différent selon le statut
            if statut == "OK":
                # ✅ : Emoji check vert pour succès
                print(f"  ✅ {nom} ({ip}): {statut} - {temps}ms")
            else:
                # ❌ : Emoji croix rouge pour échec
                print(f"  ❌ {nom} ({ip}): {statut} - {msg}")
    
    # Exception : Classe de base de toutes les erreurs Python
    except Exception as e:
        # e : Variable contenant l'objet exception
        # str(e) : Convertit l'exception en message lisible
        # ⚠️ : Emoji avertissement
        print(f"  ⚠️  Erreur lors de la surveillance: {e}")
    
    # Ligne vide pour séparer visuellement les exécutions
    print()


def job_statistiques():
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Calcul des statistiques journalières...")
    
    try:
        # Appeler la méthode de calcul
        monitoring.calculer_statistiques_journalieres()
        print("  ✅ Statistiques mises à jour")
    
    except Exception as e:
        print(f"  ⚠️  Erreur lors du calcul: {e}")
    
    print()


# === PLANIFICATION DES TÂCHES ===

# schedule.every(X).minutes.do(fonction) : Exécute 'fonction' toutes les X minutes
# INTERVALLE_SURVEILLANCE : int depuis config.py (ex: 5)
# .do(job_surveillance) : La fonction à appeler (sans les parenthèses !)
schedule.every(INTERVALLE_SURVEILLANCE).minutes.do(job_surveillance)

# schedule.every().day.at("HH:MM").do(fonction) : Exécute tous les jours à cette heure
# HEURE_STATS : str depuis config.py (ex: "00:00")
schedule.every().day.at(HEURE_STATS).do(job_statistiques)

# Exemple d'autres planifications possibles (commentées) :
# schedule.every().hour.do(job_statistiques)  # Toutes les heures
# schedule.every().monday.at("08:00").do(...)  # Tous les lundis à 8h
# schedule.every(10).seconds.do(...)  # Toutes les 10 secondes


# === AFFICHAGE DES INFORMATIONS AU DÉMARRAGE ===

print("╔════════════════════════════════════════════════╗")
print("║   SCHEDULER DE MONITORING DÉMARRÉ             ║")
print("╠════════════════════════════════════════════════╣")
print(f"║  Surveillance: toutes les {INTERVALLE_SURVEILLANCE} minutes          ║")
print(f"║  Statistiques: tous les jours à {HEURE_STATS}        ║")
print("║                                                ║")
print("║  Appuyez sur Ctrl+C pour arrêter              ║")
print("╚════════════════════════════════════════════════╝")
print()

# === SURVEILLANCE INITIALE ===
# Lancer une vérification immédiatement au démarrage
# (sans attendre le premier intervalle)
print("🚀 Surveillance initiale au démarrage...")
job_surveillance()


# === BOUCLE PRINCIPALE ===
# Cette boucle tourne en permanence pour vérifier si une tâche doit s'exécuter

# try/except/KeyboardInterrupt : Pour gérer Ctrl+C proprement
try:
    # while True : Boucle infinie (jusqu'à interruption)
    while True:
        # schedule.run_pending() : Vérifie si une tâche planifiée doit être exécutée
        # Si oui : Lance la fonction associée
        # Si non : Ne fait rien
        # Cette fonction doit être appelée régulièrement
        schedule.run_pending()
        
        # time.sleep(1) : Met le programme en pause pendant 1 seconde
        # Pourquoi ?
        # 1. Évite de consommer 100% du CPU avec une boucle vide
        # 2. Vérifie toutes les secondes si une tâche doit s'exécuter
        # Note : Pas besoin de vérifier plus souvent (tâches en minutes/heures)
        time.sleep(1)

# KeyboardInterrupt : Exception levée quand l'utilisateur fait Ctrl+C
except KeyboardInterrupt:
    # Message de sortie propre
    print("\n\n⛔ Arrêt du scheduler...")
    print("Au revoir ! 👋\n")