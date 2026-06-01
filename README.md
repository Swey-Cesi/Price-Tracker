# Price Tracker

## 📖 English

### Description
Price Tracker is a web application that monitors product prices and sends notifications when prices change. It combines web scraping, scheduled tasks, and a notification system to keep you informed about price updates.

### Features
- 🕷️ **Web Scraping**: Automatically scrape product prices from websites
- ⏰ **Scheduled Tasks**: Monitor prices at regular intervals
- 🔔 **Notifications**: Get alerts when prices change
- 📊 **Database**: Store and track price history
- 🌐 **Web Interface**: User-friendly dashboard to manage tracked products

### Project Structure
```
price-tracker/
├── app/
│   ├── main.py           # Flask application entry point
│   ├── database.py       # Database configuration and models
│   ├── scraper.py        # Web scraping logic
│   ├── scheduler.py      # Scheduled tasks management
│   ├── notifier.py       # Notification system
│   └── static/
│       └── index.html    # Web interface
├── data/                 # Database and data files
├── Dockerfile           # Docker container configuration
├── docker-compose.yml   # Docker Compose configuration
├── requirements.txt     # Python dependencies
├── .env.exemple        # Environment variables template
└── .gitignore          # Git ignore rules
```

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd price-tracker
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.exemple .env
# Edit .env with your configuration
```

5. **Run the application**
```bash
python app/main.py
```

### Docker Setup

```bash
docker-compose up -d
```

### Configuration
Create a `.env` file based on `.env.exemple` with your settings:
- Database connection details
- Scraping targets and intervals
- Notification preferences

---

## 📖 Français

### Description
Price Tracker est une application web qui surveille les prix des produits et envoie des notifications en cas de changement de prix. Elle combine le web scraping, les tâches planifiées et un système de notification pour vous tenir informé des mises à jour de prix.

### Fonctionnalités
- 🕷️ **Web Scraping**: Extraire automatiquement les prix des produits depuis les sites web
- ⏰ **Tâches planifiées**: Surveiller les prix à intervalles réguliers
- 🔔 **Notifications**: Recevoir des alertes en cas de changement de prix
- 📊 **Base de données**: Stocker et suivre l'historique des prix
- 🌐 **Interface web**: Tableau de bord convivial pour gérer les produits suivis

### Structure du projet
```
price-tracker/
├── app/
│   ├── main.py           # Point d'entrée de l'application Flask
│   ├── database.py       # Configuration et modèles de la base de données
│   ├── scraper.py        # Logique de web scraping
│   ├── scheduler.py      # Gestion des tâches planifiées
│   ├── notifier.py       # Système de notification
│   └── static/
│       └── index.html    # Interface web
├── data/                 # Fichiers de base de données et de données
├── Dockerfile           # Configuration du conteneur Docker
├── docker-compose.yml   # Configuration Docker Compose
├── requirements.txt     # Dépendances Python
├── .env.exemple        # Modèle de variables d'environnement
└── .gitignore          # Règles d'ignore Git
```

### Installation

1. **Cloner le dépôt**
```bash
git clone <repository-url>
cd price-tracker
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement**
```bash
cp .env.exemple .env
# Modifier .env avec votre configuration
```

5. **Lancer l'application**
```bash
python app/main.py
```

### Configuration Docker

```bash
docker-compose up -d
```

### Configuration
Créez un fichier `.env` basé sur `.env.exemple` avec vos paramètres:
- Détails de connexion à la base de données
- Cibles et intervalles de scraping
- Préférences de notification

---

## License
MIT

## Support
For issues and questions, please open an issue on the repository.