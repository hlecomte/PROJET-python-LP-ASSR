# scheduler.py
"""
Module de planification automatique des tâches de monitoring.
Utilise la bibliothèque 'schedule' pour exécuter périodiquement
les vérifications d'équipements et le calcul des statistiques.
"""

import schedule
import time
from monitoring import MonitoringReseau
from config import DB_CONFIG

# Initialisation de l'objet de monitoring avec la configuration de la base de données
monitoring = MonitoringReseau(DB_CONFIG)

def job_surveillance():
    """
    Tâche planifiée pour effectuer la surveillance de tous les équipements réseau.
    Lance une vérification complète de tous les équipements actifs et affiche les résultats.
    Cette fonction est appelée automatiquement par le planificateur.
    """
    print("Lancement de la surveillance...")
    results = monitoring.verifier_tous_equipements()
    for r in results:
        print(r)

def job_statistiques():
    """
    Tâche planifiée pour calculer et enregistrer les statistiques journalières.
    Agrège les données de disponibilité de la journée pour chaque équipement
    et les sauvegarde dans la base de données.
    Cette fonction est appelée automatiquement par le planificateur.
    """
    print("Calcul des statistiques journalières...")
    monitoring.calculer_statistiques_journalieres()
    print("Stats mises à jour ✅")

# Configuration de la planification des tâches
# La surveillance est lancée toutes les 5 minutes
schedule.every(5).minutes.do(job_surveillance)

# Le calcul des statistiques est effectué tous les jours à minuit
schedule.every().day.at("00:00").do(job_statistiques)

# Boucle principale du planificateur
# Vérifie en permanence s'il y a des tâches à exécuter et les lance au moment approprié
while True:
    schedule.run_pending()
    time.sleep(1)