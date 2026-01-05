# 🖥️ Système de Monitoring Réseau

> Projet de supervision d'infrastructure réseau développé en Python avec MySQL  
> Formation LP ASSR - 2025

## 📋 Table des matières

- [Description](#-description)
- [Fonctionnalités](#-fonctionnalités)
- [Prérequis](#-prérequis)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Utilisation](#-utilisation)
- [Structure du projet](#-structure-du-projet)
- [Architecture](#-architecture)
- [Exemples](#-exemples)
- [Dépannage](#-dépannage)
- [Améliorations futures](#-améliorations-futures)

## 📖 Description

Ce système permet de surveiller automatiquement l'état des équipements réseau (serveurs, routeurs, switches, firewalls, points d'accès WiFi) et de générer des alertes en cas de problème.

### Objectifs pédagogiques

- **Python** : Programmation orientée objet, gestion de base de données
- **MySQL** : Requêtes complexes, jointures, agrégations
- **Réseau** : Protocoles ICMP (ping), TCP (scan de ports)
- **Automatisation** : Tâches planifiées, threading
- **Documentation** : Code commenté, README, rapports

## ✨ Fonctionnalités

### 🔍 Surveillance
- ✅ Ping ICMP avec mesure du temps de réponse
- ✅ Scan de ports TCP pour vérifier les services
- ✅ Détection automatique des pannes
- ✅ Génération d'alertes multi-niveaux (INFO/WARNING/CRITICAL)
- ✅ Surveillance manuelle ou automatique (24/7)

### 🚨 Alertes
- Filtrage par niveau de criticité
- Résolution manuelle avec traçabilité
- Historique complet des incidents
- Statuts : Ouverte / En cours / Résolue

### 📊 Rapports & Statistiques
- Rapport de disponibilité (jour/semaine/mois)
- Top 5 équipements fiables/problématiques
- Temps de réponse moyen par équipement
- Export CSV et JSON
- Graphique ASCII de disponibilité (7 jours)
- Taux de disponibilité global
- Liste des équipements actuellement en panne

## 🛠️ Prérequis

### Logiciels nécessaires

```bash
# Python 3.8 ou supérieur
python --version  # Doit afficher Python 3.8+

# MySQL 8.0 ou supérieur
mysql --version  # Doit afficher MySQL 8.0+

# pip (gestionnaire de paquets Python)
pip --version
```

### Connaissances recommandées

- Bases de Python (variables, fonctions, classes)
- SQL (SELECT, INSERT, UPDATE, DELETE, JOIN)
- Notions de réseau (IP, ports, ping)
- Ligne de commande (terminal/CMD)

## 📦 Installation

### 1. Cloner ou télécharger le projet

```bash
git clone https://github.com/hlecomte/PROJET-python-LP-ASSR
cd PROJET-python-LP-ASSR
```

Ou télécharger le ZIP et extraire.

### 2. Créer un environnement virtuel (recommandé)

```bash
# Créer l'environnement
python -m venv venv

# Activer l'environnement
# Windows :
venv\Scripts\activate

# Linux/Mac :
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

Cela installe :
- `mysql-connector-python` : Connexion MySQL
- `python-dotenv` : Gestion des variables d'environnement
- `schedule` : Planification de tâches

### 4. Créer la base de données

```bash
# Se connecter à MySQL
mysql -u root -p

# Dans le prompt MySQL :
source create_tables.sql

# Ou directement depuis le terminal :
mysql -u root -p < create_tables.sql
```

Cela crée :
- Base de données `monitoring_reseau`
- 5 tables : `equipements`, `ports_surveilles`, `checks`, `alertes`, `statistiques_disponibilite`

### 5. Insérer les données de test (optionnel)

```bash
mysql -u root -p monitoring_reseau < insert_test_data.sql
```

Cela ajoute :
- 12 équipements de test
- Ports surveillés configurés
- Alertes historiques
- Checks simulés sur 7 jours
- Statistiques pré-calculées

## ⚙️ Configuration

### 1. Créer le fichier `.env`

```bash
# Copier l'exemple
cp .env.example .env

# Ou créer manuellement
nano .env  # Linux/Mac
notepad .env  # Windows
```

### 2. Remplir les variables

```bash
# .env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=votre_mot_de_passe_mysql
DB_NAME=monitoring_reseau

INTERVALLE_SURVEILLANCE=5
HEURE_STATISTIQUES=00:00

SEUIL_WARNING=100
SEUIL_CRITICAL=500
```

⚠️ **Important** : Ne JAMAIS commiter le fichier `.env` sur Git !

### 3. Vérifier la configuration

```ps
python test_monitoring.py
```

Si tout est OK, vous verrez :
```
✅ Connexion réussie
✅ Test ping OK
✅ Test scan port OK
...
```

## 🚀 Utilisation

### Mode interactif (CLI)

Pour utiliser l'interface en ligne de commande :

```ps
python cli.py
```

Vous verrez le menu principal :

```
╔═══════════════════════════════════════════════╗
║     SYSTÈME DE MONITORING RÉSEAU              ║
╠═══════════════════════════════════════════════╣
║  1. Gestion des équipements                   ║
║  2. Lancer une surveillance manuelle          ║
║  3. Consulter les alertes                     ║
║  4. Générer des rapports                      ║
║  5. Statistiques de disponibilité             ║
║  6. Configuration                             ║
║  7. Quitter                                   ║
╚═══════════════════════════════════════════════╝
```

### Mode automatique (Scheduler)

Pour lancer la surveillance automatique 24/7 :

```ps
python scheduler.py
```

Le scheduler va :
- Vérifier tous les équipements toutes les 5 minutes (configurable)
- Calculer les statistiques tous les jours à minuit

Pour arrêter : `Ctrl+C`



## 📁 Structure du projet

```
monitoring-reseau/
│
├── .env                      # Variables d'environnement (mot de passe)
├── .gitignore               # Fichiers à ignorer par Git
├── requirements.txt         # Dépendances Python
├── README.md                # Ce fichier
│
├── config.py                # Configuration centralisée
├── monitoring.py            # Classe principale de surveillance
├── cli.py                   # Interface utilisateur (menu)
├── scheduler.py             # Surveillance automatique 24/7
│
├── test_monitoring.py       # Tests unitaires
├── create_tables.sql        # Script de création des tables
├── insert_test_data.sql     # Données de test
│
└── rapports/                # Dossier des rapports générés
    ├── rapport_alertes_20250104_153045.csv
    └── rapport_alertes_20250104_153045.json
```

## 🏗️ Architecture

### Diagramme de classes

```
┌─────────────────────┐
│  MonitoringReseau   │
├─────────────────────┤
│ - db                │
│ - cursor            │
├─────────────────────┤
│ + ping_equipement() │
│ + scan_port()       │
│ + verifier_tous()   │
│ + generer_alerte()  │
│ + calculer_stats()  │
└─────────────────────┘
```

### Schéma de base de données

```sql
equipements
├── id_equipement (PK)
├── nom
├── type
├── adresse_ip
├── systeme_exploitation
├── localisation
└── actif

ports_surveilles
├── id_port (PK)
├── id_equipement (FK)
├── numero_port
└── service

checks
├── id_check (PK)
├── id_equipement (FK)
├── date_check
├── type_check
├── resultat
├── temps_reponse
└── message

alertes
├── id_alerte (PK)
├── id_equipement (FK)
├── niveau
├── titre
├── message
├── date_creation
├── date_resolution
├── statut
└── resolu_par

statistiques_disponibilite
├── id_stat (PK)
├── id_equipement (FK)
├── date
├── nb_checks_total
├── nb_checks_ok
├── taux_disponibilite
└── temps_reponse_moyen
```

## 💡 Exemples

### Ajouter un équipement

```python
# Via CLI :
Menu > 1 > 1
Nom: SRV-WEB-01
Type: Serveur
IP: 192.168.1.100
OS: Ubuntu 22.04
Localisation: Datacenter A
```

### Ajouter un port surveillé

```python
Menu > 1 > 5
ID équipement: 1
Port: 80
Service: HTTP
Description: Serveur web Apache
```

### Lancer une surveillance manuelle

```python
Menu > 2 > 1
# Vérifie tous les équipements immédiatement
```

### Voir les alertes critiques

```python
Menu > 3 > 3
Niveau: CRITICAL
# Affiche uniquement les alertes CRITICAL
```

### Générer un rapport CSV

```python
Menu > 4 > 5
# Crée rapport_alertes_YYYYMMDD_HHMMSS.csv
```

## 🐛 Dépannage

### Erreur : `Access denied for user 'root'@'localhost'`

**Cause** : Mauvais mot de passe MySQL dans `.env`

**Solution** :
```bash
# Vérifier le mot de passe
nano .env

# Tester la connexion MySQL
mysql -u root -p
```

### Erreur : `ModuleNotFoundError: No module named 'mysql'`

**Cause** : Dépendances non installées

**Solution** :
```bash
pip install -r requirements.txt
```

### Erreur : `Table 'monitoring_reseau.equipements' doesn't exist`

**Cause** : Base de données non créée

**Solution** :
```bash
mysql -u root -p < create_tables.sql
```

### Le ping ne fonctionne pas sous Linux

**Cause** : Droits insuffisants pour ICMP

**Solution** :
```bash
# Exécuter avec sudo
sudo python cli.py

# Ou modifier les permissions
sudo setcap cap_net_raw+ep /usr/bin/python3
```

### La commande ping n'est pas reconnue

**Cause** : Différence Windows/Linux dans la commande ping

**Solution** : Modifier `monitoring.py` ligne 107 :
```python
# Windows : ping -n 1
# Linux/Mac : ping -c 1
["ping", "-c", "1", ip_address]  # Pour Linux/Mac
```

## 🔮 Améliorations futures

### Fonctionnalités bonus (+20 points)

1. **Notifications par email** (SMTP)
   - Envoyer un email automatique pour les alertes CRITICAL
   - Utiliser `smtplib` de Python

2. **Dashboard web** (Flask + HTML/CSS)
   - Interface graphique moderne
   - Affichage temps réel avec WebSocket
   - Statut visuel (vert/orange/rouge)

3. **Analyse de logs réseau**
   - Parser des logs syslog, Apache, etc.
   - Détecter des patterns suspects
   - Intégration avec fail2ban

4. **Scan de vulnérabilités**
   - Vérifier les versions de services
   - Détecter les ports dangereux ouverts
   - CVE lookup automatique

5. **Graphiques avancés** (Matplotlib/Plotly)
   - Courbes d'évolution du temps de réponse
   - Heatmaps de disponibilité
   - Tableaux de bord interactifs

6. **API REST** (Flask-RESTful)
   - Endpoints pour consulter les données
   - Authentification JWT
   - Documentation Swagger

7. **Tests de performance**
   - Mesure de bande passante (iperf)
   - Tests de latence avancés
   - Monitoring de la gigue



### Améliorations techniques

- [ ] Validation des entrées utilisateur (regex pour IP)
- [ ] Pool de connexions MySQL (performance)
- [ ] Logs dans des fichiers avec rotation
- [ ] Tests unitaires complets (pytest)
- [ ] CI/CD avec GitHub Actions
- [ ] Conteneurisation Docker
- [ ] Support SNMP pour équipements réseau
- [ ] Multi-threading pour surveillance parallèle
- [ ] WebSocket pour notifications temps réel
- [ ] Internationalisation (i18n) français/anglais

## 📄 Licence

Usage éducatif uniquement - Projet LP ASSR 2025

## 👨‍💻 Auteur

Projet réalisé dans le cadre de la formation **Licence Professionnelle Administration et Sécurité des Systèmes et des Réseaux (ASSR)**.


