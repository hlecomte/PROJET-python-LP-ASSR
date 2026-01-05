/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.8.3-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: monitoring_reseau
-- ------------------------------------------------------
-- Server version	11.8.3-MariaDB-0+deb13u1 from Debian

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Current Database: `monitoring_reseau`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `monitoring_reseau` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;

USE `monitoring_reseau`;

--
-- Table structure for table `alertes`
--

DROP TABLE IF EXISTS `alertes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `alertes` (
  `id_alerte` int(11) NOT NULL AUTO_INCREMENT,
  `id_equipement` int(11) DEFAULT NULL,
  `id_check` int(11) DEFAULT NULL,
  `niveau` enum('INFO','WARNING','CRITICAL') NOT NULL,
  `titre` varchar(200) NOT NULL,
  `message` text DEFAULT NULL,
  `date_creation` datetime DEFAULT current_timestamp(),
  `date_resolution` datetime DEFAULT NULL,
  `statut` enum('Ouverte','En cours','Résolue') DEFAULT 'Ouverte',
  `resolu_par` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id_alerte`),
  KEY `id_equipement` (`id_equipement`),
  KEY `id_check` (`id_check`),
  CONSTRAINT `alertes_ibfk_1` FOREIGN KEY (`id_equipement`) REFERENCES `equipements` (`id_equipement`) ON DELETE CASCADE,
  CONSTRAINT `alertes_ibfk_2` FOREIGN KEY (`id_check`) REFERENCES `checks` (`id_check`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alertes`
--

LOCK TABLES `alertes` WRITE;
/*!40000 ALTER TABLE `alertes` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `alertes` VALUES
(1,1,4,'CRITICAL','Port 80 fermé sur SRV-WEB-01','Le port 80 du serveur web est inaccessible. Vérifier le service Apache.','2025-12-17 01:09:58',NULL,'Ouverte',NULL),
(2,1,6,'CRITICAL','Port 443 fermé sur SRV-WEB-01','Le port 443 du serveur web est inaccessible. Vérifier le service et le certificat SSL.','2025-12-17 01:09:58',NULL,'Ouverte',NULL),
(3,3,8,'CRITICAL','Routeur RT-LABO-01 inaccessible','Aucune réponse ICMP. Vérifier la connectivité physique.','2025-12-17 01:09:58',NULL,'Ouverte',NULL),
(4,3,9,'CRITICAL','Port 22 fermé sur RT-LABO-01','Le port SSH du routeur est fermé. Accès administration impossible.','2025-12-17 01:09:58',NULL,'Ouverte',NULL);
/*!40000 ALTER TABLE `alertes` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `checks`
--

DROP TABLE IF EXISTS `checks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `checks` (
  `id_check` int(11) NOT NULL AUTO_INCREMENT,
  `id_equipement` int(11) DEFAULT NULL,
  `date_check` datetime DEFAULT current_timestamp(),
  `type_check` enum('Ping','Port','HTTP','SSH') NOT NULL,
  `resultat` enum('OK','WARNING','CRITICAL','UNKNOWN') NOT NULL,
  `temps_reponse` float DEFAULT NULL,
  `message` text DEFAULT NULL,
  PRIMARY KEY (`id_check`),
  KEY `id_equipement` (`id_equipement`),
  CONSTRAINT `checks_ibfk_1` FOREIGN KEY (`id_equipement`) REFERENCES `equipements` (`id_equipement`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `checks`
--

LOCK TABLES `checks` WRITE;
/*!40000 ALTER TABLE `checks` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `checks` VALUES
(1,1,'2025-12-15 01:09:58','Ping','OK',12.5,'Réponse ICMP normale'),
(2,1,'2025-12-16 01:09:58','Ping','OK',15.2,'Réponse ICMP normale'),
(3,1,'2025-12-17 01:09:58','Ping','OK',13.9,'Réponse ICMP normale'),
(4,1,'2025-12-17 01:09:58','Port','CRITICAL',NULL,'Port 80 fermé Timeout'),
(5,1,'2025-12-16 13:09:58','Port','WARNING',NULL,'Port 443 Latence élevée'),
(6,1,'2025-12-17 01:09:58','Port','CRITICAL',NULL,'Port 443 fermé Timeout'),
(7,3,'2025-12-16 01:09:58','Ping','WARNING',50.2,'Réponse ICMP lente'),
(8,3,'2025-12-17 01:09:58','Ping','CRITICAL',NULL,'Pas de réponse ICMP'),
(9,3,'2025-12-17 01:09:58','Port','CRITICAL',NULL,'Port 22 fermé');
/*!40000 ALTER TABLE `checks` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `equipements`
--

DROP TABLE IF EXISTS `equipements`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `equipements` (
  `id_equipement` int(11) NOT NULL AUTO_INCREMENT,
  `nom` varchar(100) NOT NULL,
  `type` enum('Serveur','Routeur','Switch','Firewall','AP') NOT NULL,
  `adresse_ip` varchar(15) NOT NULL,
  `localisation` varchar(200) DEFAULT NULL,
  `systeme_exploitation` varchar(100) DEFAULT NULL,
  `date_ajout` datetime DEFAULT current_timestamp(),
  `actif` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`id_equipement`),
  UNIQUE KEY `adresse_ip` (`adresse_ip`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `equipements`
--

LOCK TABLES `equipements` WRITE;
/*!40000 ALTER TABLE `equipements` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `equipements` VALUES
(1,'SRV-WEB-01','Serveur','192.168.1.10','Salle serveur Rack A1','Ubuntu 22.04 LTS','2025-12-17 01:09:58',1),
(2,'SRV-BDD-01','Serveur','192.168.1.11','Salle serveur Rack A2','Debian 11','2025-12-17 01:09:58',1),
(3,'RT-LABO-01','Routeur','192.168.1.1','Laboratoire réseau','Cisco IOS 15.2','2025-12-17 01:09:58',1),
(4,'SW-ETAGE1-01','Switch','192.168.1.20','Étage 1 Armoire 3','Cisco Catalyst','2025-12-17 01:09:58',1),
(5,'FW-PERIMETRE','Firewall','192.168.1.254','Salle technique','pfSense 2.6.0','2025-12-17 01:09:58',1),
(6,'AP-BATIMENTB','AP','192.168.1.50','Bâtiment B Couloir','Ubiquiti UniFi','2025-12-17 01:09:58',1),
(7,'SRV-MAIL-01','Serveur','192.168.1.12','Salle serveur Rack A3','CentOS 8','2025-12-17 01:09:58',1),
(8,'SW-ETAGE2-01','Switch','192.168.1.21','Étage 2 Armoire 5','HP ProCurve','2025-12-17 01:09:58',1),
(9,'SRV-FICHIERS-01','Serveur','192.168.1.13','Salle serveur Rack A4','Windows Server 2019','2025-12-17 01:09:58',1),
(10,'RT-BACKUP-01','Routeur','192.168.1.2','Salle backup','Juniper JunOS','2025-12-17 01:09:58',1),
(11,'SRV-DEV-01','Serveur','192.168.1.14','Bureau 10','Ubuntu 20.04 LTS','2025-12-17 01:09:58',1),
(12,'SW-ETAGE3-01','Switch','192.168.1.22','Étage 3 Armoire 2','Dell PowerConnect','2025-12-17 01:09:58',1);
/*!40000 ALTER TABLE `equipements` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `ports_surveilles`
--

DROP TABLE IF EXISTS `ports_surveilles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `ports_surveilles` (
  `id_port` int(11) NOT NULL AUTO_INCREMENT,
  `id_equipement` int(11) DEFAULT NULL,
  `numero_port` int(11) NOT NULL,
  `service` varchar(50) DEFAULT NULL,
  `description` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id_port`),
  KEY `id_equipement` (`id_equipement`),
  CONSTRAINT `ports_surveilles_ibfk_1` FOREIGN KEY (`id_equipement`) REFERENCES `equipements` (`id_equipement`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ports_surveilles`
--

LOCK TABLES `ports_surveilles` WRITE;
/*!40000 ALTER TABLE `ports_surveilles` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `ports_surveilles` VALUES
(1,1,80,'HTTP','Serveur web Apache'),
(2,1,443,'HTTPS','Serveur web sécurisé'),
(3,1,22,'SSH','Accès administration'),
(4,2,3306,'MySQL','Base de données principale'),
(5,2,22,'SSH','Accès administration'),
(6,3,22,'SSH','Configuration routeur'),
(7,3,80,'HTTP','Interface web Cisco'),
(8,4,22,'SSH','Configuration switch'),
(9,5,80,'HTTP','Interface pfSense'),
(10,5,443,'HTTPS','Interface sécurisée pfSense'),
(11,6,25,'SMTP','Serveur de mail'),
(12,6,143,'IMAP','Accès mail'),
(13,7,445,'SMB','Partage de fichiers'),
(14,7,139,'NetBIOS','Partage réseau'),
(15,8,22,'SSH','Configuration routeur'),
(16,9,8080,'HTTP','Serveur de développement TomCat'),
(17,9,22,'SSH','Accès administration');
/*!40000 ALTER TABLE `ports_surveilles` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `statistiques_disponibilite`
--

DROP TABLE IF EXISTS `statistiques_disponibilite`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `statistiques_disponibilite` (
  `id_stat` int(11) NOT NULL AUTO_INCREMENT,
  `id_equipement` int(11) DEFAULT NULL,
  `date` date NOT NULL,
  `nb_checks_total` int(11) DEFAULT 0,
  `nb_checks_ok` int(11) DEFAULT 0,
  `nb_checks_warning` int(11) DEFAULT 0,
  `nb_checks_critical` int(11) DEFAULT 0,
  `taux_disponibilite` float DEFAULT NULL,
  `temps_reponse_moyen` float DEFAULT NULL,
  PRIMARY KEY (`id_stat`),
  UNIQUE KEY `unique_stat` (`id_equipement`,`date`),
  CONSTRAINT `statistiques_disponibilite_ibfk_1` FOREIGN KEY (`id_equipement`) REFERENCES `equipements` (`id_equipement`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `statistiques_disponibilite`
--

LOCK TABLES `statistiques_disponibilite` WRITE;
/*!40000 ALTER TABLE `statistiques_disponibilite` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `statistiques_disponibilite` VALUES
(1,1,'2025-12-16',6,4,1,1,66.67,14.63),
(2,1,'2025-12-17',4,2,0,2,50,14),
(3,2,'2025-12-16',6,6,0,0,100,19.5),
(4,2,'2025-12-17',4,4,0,0,100,20.75),
(5,3,'2025-12-17',4,1,1,2,25,8.3);
/*!40000 ALTER TABLE `statistiques_disponibilite` ENABLE KEYS */;
UNLOCK TABLES;
commit;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2025-12-17  1:13:42
