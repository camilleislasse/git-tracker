
# Application Flask pour suivre les branches Git

Cette application permet de suivre les branches Git actives dans différents projets. Elle utilise Flask pour créer une interface web simple, où vous pouvez ajouter, supprimer et suivre le temps passé sur chaque branche de vos projets Git.


# Installation avec Docker

## Exécution rapide

1. **Cloner le projet** :
```sh
git clone https://github.com/votre-repository.git
cd votre-repository
```

2. **Démarrer l’application** :
```sh
docker-compose up -d
```

3. **Accéder à l'application** :  
   [http://localhost:5000](http://localhost:5000)

## Arrêter l’application
```sh
docker-compose down
```  

# Installation manuelle

## Prérequis

- Python 3.x installé sur votre machine
- `pip` (le gestionnaire de paquets Python)

## Installation

1. **Clonez ce repository sur votre machine** :

   Ouvrez un terminal et exécutez la commande suivante pour cloner le projet :

   ```bash
   git clone https://github.com/votre_utilisateur/votre_repository.git
   cd votre_repository
   ```

2. **Installez les dépendances Python** :

   Ce projet nécessite quelques bibliothèques Python. Vous pouvez les installer en exécutant la commande suivante :

   ```bash
   pip install -r requirements.txt
   ```

3. **Exécutez l'application Flask** :

   Une fois les dépendances installées, vous pouvez démarrer l'application avec cette commande :

   ```bash
   python app.py
   ```

4. **Accédez à l'application dans votre navigateur** :

   Ouvrez votre navigateur web et allez à l'adresse suivante :

   ```
   http://localhost:5000
   ```

   Vous devriez voir l'interface de l'application.

## Fonctionnalités

- **Ajouter un projet** : Vous pouvez ajouter un projet en entrant son nom et le chemin vers le dossier contenant le dépôt Git.
- **Suivre les branches** : L'application suit la branche Git active dans chaque projet et enregistre le temps passé sur chaque branche.
- **Voir les logs** : Vous pouvez consulter les logs de chaque projet pour voir combien de temps vous avez passé sur chaque branche.

## Dépannage

- Si vous avez une erreur concernant **Git**, assurez-vous que **Git** est installé sur votre machine et que les projets que vous ajoutez sont bien des dépôts Git.
- Si l'application ne se lance pas, vérifiez que Python et pip sont bien installés en exécutant les commandes suivantes :

   ```bash
   python --version
   pip --version
   ```

## Suppression d'un projet

- Si vous souhaitez supprimer un projet de l'application, cliquez sur "Supprimer" à côté du projet dans l'interface web.

## Remarques

- Cette application fonctionne sur **localhost** (votre machine locale).
- Si vous souhaitez la déployer sur un serveur, vous devrez peut-être configurer des options supplémentaires dans Flask.
