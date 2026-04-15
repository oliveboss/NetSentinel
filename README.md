# 🛡️ NetSentinel - Système de Détection d'Intrusions Réseau

NetSentinel est un **Système de Détection d'Intrusions (IDS)** léger et performant, conçu pour surveiller le trafic réseau en temps réel et détecter les activités suspectes et malveillantes.

---

##  Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Fonctionnalités](#fonctionnalités)
- [Détections implémentées](#détections-implémentées)
- [Architecture](#architecture)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Configuration](#configuration)
- [Structure du projet](#structure-du-projet)
- [Tests](#tests)
- [Workflows CI/CD](#workflows-cicd)
- [Contribution](#contribution)

---

## 👁️ Vue d'ensemble

Il s'agit d'un logiciel de surveillance réseau qui capture et analyse les paquets réseau pour détecter les patterns d'attaque courants. L'application dispose d'une **interface graphique moderne** (Tkinter) pour visualiser l'activité réseau et les alertes en temps réel.

### Objectifs:
- ✅ Capture en temps réel du trafic réseau
- ✅ Analyse intelligente des paquets
- ✅ Détection d'anomalies et d'attaques
- ✅ Alertes et notifications visuelles
- ✅ Tableau de bord avec statistiques

---

##  Fonctionnalités

### Interface Utilisateur
-  **Tableau de bord** avec statistiques en direct
-  **Panneau d'alertes** pour les événements de sécurité
-  **Vue du trafic** avec détails des connexions
-  **Thème personnalisé** et interface moderne
-  **Statistiques réseau** en temps réel

### Moteur de Détection
-  Analyse multi-critères des paquets
-  Détection par fenêtres temporelles
-  Règles configurables et adaptables
-  Logging  des événements

---

## 🚨 Détections implémentées

### 1. **Port Scan** (`portscan_rule.py`)
Détecte les tentatives de scan de ports sur un hôte.

**Critères:**
- Nombre de ports scanalisés sur un hôte dans une fenêtre de temps
- Seuil configurable: 10 ports en 10 secondes

**Impact:**  Moyen - Reconnaissance du réseau

---

### 2. **SYN Flood** (`syn_flood_rule.py`)
Détecte les attaques par débordement de paquets SYN (attaque DoS).

**Critères:**
- Accumulation de paquets SYN d'une même source
- Seuil configurable: 20 paquets SYN en 5 secondes

**Impact:**  Critique - Attaque par déni de service

---

### 3. **ICMP Scan** (`icmp_scan_rule.py`)
Détecte les tentatives de reconnaissance par ICMP (ping sweep).

**Critères:**
- Plusieurs paquets ICMP vers différentes destinations
- Seuil configurable: 5 paquets en 10 secondes

**Impact:** ⚠️ Moyen - Reconnaissance du réseau

---

### 4. **Ports Interdits** (`forbidden_ports_rule.py`)
Détecte les connexions tentées vers des ports sensibles interdits.

**Ports surveillés par défaut:**
- **22** (SSH)
- **23** (Telnet)
- **3389** (RDP)

**Impact:**  Critique - Tentative d'accès non autorisé

---

##  Architecture

```
NetSentinel/
├── capture/           # Module de capture de paquets
│   └── sniffer.py     # Capteur utilisant Scapy
├── detection/         # Moteur de détection
│   ├── rules_engine.py   # Orchestrateur des règles
│   ├── rules_config.py   # Configuration des seuils
│   └── rules/            # Implémentation des règles
├── controller/        # Logique applicative
│   ├── app_controller.py
│   └── capture_controller.py
├── ui/               # Interface graphique (Tkinter)
│   ├── main_window.py
│   ├── alerts_view.py
│   ├── traffic_view.py
│   ├── stats_panel.py
│   └── widgets/
├── features/        # Extraction de features
│   └── extractor.py
├── config/          # Configuration
│   └── thresholds.py
├── state/           # Gestion d'état
│   └── runtime_state.py
├── utils/           # Utilitaires
│   ├── interfaces.py
│   └── network_monitor.py
└── tests/           # Suite de tests
```

### Flux de données:

```
Paquets réseau → Sniffer → Rules Engine → Détections → UI → Alertes
                                ↓
                            État runtime
                            (Statistics)
```

---

##  Installation

### Pré-requis
- **Python 3.8+**
- **pip** (gestionnaire de paquets Python)
- **Accès administrateur** (pour la capture de paquets)

### Étapes d'installation

1. **Cloner le projet**
   ```bash
   git clone https://github.com/oliveboss/NetSentinel.git
   cd Projet\ en\ info\ netsentinel
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv .venv
   ```

3. **Activer l'environnement (Windows)**
   ```bash
   .venv\Scripts\Activate.ps1
   ```

   **Activer l'environnement (Linux/macOS)**
   ```bash
   source .venv/bin/activate
   ```

4. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

### Dépendances principales

| Paquet | Utilisation |
|--------|------------|
| **scapy** | Capture et analyse de paquets réseau |
| **pillow** | Traitement d'images pour l'UI |
| **psutil** | Monitoring système |
| **tk** | Interface graphique |
| **pytest** | Framework de tests |

---

##  Utilisation

### Lancer l'application

```bash
python main.py
```

### Interface principale

Une fois lancée, l'application affiche:

1. **Panneau de statistiques** - Vue d'ensemble du trafic
2. **Vue du trafic** - Détail des connexions réseau
3. **Panneau d'alertes** - Événements de sécurité détectés
4. **Barre d'état** - Statut du sniffer

### Contrôles de l'interface

- **Démarrer/Arrêter la capture** - Boutons principaux
- **Sélectionner l'interface réseau** - Choisir la carte réseau à monitorer
- **Afficher les détails** - Cliquer sur les éléments pour plus d'informations

---

## ⚙️ Configuration

### Fichier de configuration: `detection/rules_config.py`

```python
# --- PortScan ---
PORTSCAN_TIME_WINDOW = 10      # Fenêtre temporelle (secondes)
PORTSCAN_PORT_THRESHOLD = 10   # Nombre de ports avant alerte

# --- SYN Flood ---
SYNFLOOD_TIME_WINDOW = 5       # Fenêtre temporelle (secondes)
SYNFLOOD_SYN_THRESHOLD = 20    # Nombre de SYN avant alerte

# --- ICMP Scan ---
ICMP_TIME_WINDOW = 10          # Fenêtre temporelle (secondes)
ICMP_THRESHOLD = 5             # Nombre de paquets avant alerte

# --- Ports Interdits ---
FORBIDDEN_PORTS = [22, 23, 3389]  # Ports surveillés
```

### Modification des seuils

Éditer `detection/rules_config.py` pour ajuster la sensibilité des détections:

- ⬆️ **Augmenter les seuils** = Moins d'alertes (moins de faux positifs)
- ⬇️ **Diminuer les seuils** = Plus d'alertes (détection plus sensible)

---

## 📂 Structure du projet

### Modules clés

| Module | Description |
|--------|------------|
| `capture/sniffer.py` | Capture des paquets avec Scapy |
| `detection/rules_engine.py` | Orchestration des règles de détection |
| `controller/app_controller.py` | Logique principale de l'application |
| `ui/main_window.py` | Fenêtre principale Tkinter |
| `state/runtime_state.py` | Gestion de l'état global |
| `utils/interfaces.py` | Énumération des interfaces réseau |

### Arborescence complète

```
Projet en info netsentinel/
├── main.py                      # Point d'entrée
├── requirements.txt             # Dépendances
├── conftest.py                 # Configuration pytest
├── sonar-project.properties     # Configuration SonarQube
├── NetSentinel.spec            # Spec PyInstaller
├── README.md                   # Ce fichier
├── capture/                    # Capture réseau
├── detection/                  # Moteur de détection
├── controller/                 # Contrôleurs
├── ui/                        # Interface graphique
├── features/                  # Extraction features
├── config/                    # Configuration
├── state/                     # Gestion d'état
├── utils/                     # Utilitaires
└── tests/                     # Tests unitaires
```

---

## 🧪 Tests

### Lancer tous les tests

```bash
pytest
```

### Exécuter un test spécifique

```bash
pytest tests/detection/test_rules_engine.py
```

### Avec rapport de couverture

```bash
pytest --cov=. --cov-report=html
```

### Structure des tests

```
tests/
├── capture/          # Tests du sniffer
├── detection/        # Tests des règles
├── controller/       # Tests des contrôleurs
├── ui/              # Tests de l'interface
├── features/        # Tests d'extraction
└── utils/           # Tests des utilitaires
```

**Framework utilisé:** pytest  
**Configuration:** `conftest.py`

---

## 🔄 Workflows CI/CD

### Pipeline GitHub Actions (`.github/workflows/ci.yml`)

Le projet bénéficie d'un pipeline d'intégration continue automatisé:

#### Stages:

1. **Checkout** - Récupération du code
2. **Setup Python** - Configuration de l'environnement
3. **Install Dependencies** - Installation des dépendances
4. **Run Tests** - Exécution de la suite de tests
5. **Code Quality** - Analyse SonarQube
6. **Build Artifact** - Compilation avec PyInstaller

#### Déclenchement:

- ✅ À chaque `push` sur les branches principales
- ✅ À chaque `pull request`
- ✅ Sur demande manuelle (workflow_dispatch)

#### Sorties:

-  Rapport de tests pytest
-  Métriques SonarQube
- Exécutable compilé (build/)

### Configuration SonarQube

Fichier: `sonar-project.properties`

- Analyse statique du code
- Détection de code smell
- Mesure de la couverture de tests
- Évaluation de la qualité globale

---

## 🔐 Sécurité

### Bonnes pratiques implémentées

- ✅ Validation des entrées utilisateur
- ✅ Gestion sécurisée des paquets réseau
- ✅ Isolation des composants
- ✅ Tests de sécurité
- ✅ Monitoring des violations


---

##  Contribution

### Ajouter une nouvelle règle de détection

1. Créer `detection/rules/my_rule.py`
2. Hériter de la classe de base `Rule`
3. Implémenter la méthode `detect(packet)`
4. Ajouter les tests dans `tests/detection/rules/`
5. Intégrer dans `rules_engine.py`

### Process

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/ma-feature`)
3. Commit vos changements (`git commit -am 'Ajout: ma-feature'`)
4. Push vers la branche (`git push origin feature/ma-feature`)
5. Ouvrir une Pull Request



