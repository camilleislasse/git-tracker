# Utilisation de l'image Python officielle comme base
FROM python:3.9-slim

# Mettre à jour les dépôts et installer git
RUN apt-get update -y && \
    apt-get install -y git

# Supprimer les caches d'apt
RUN rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

ENV FLASK_ENV=development

# Copier le fichier des dépendances
COPY requirements.txt /app/

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application dans le conteneur
COPY . /app/

# Exposer le port 5000 pour l'application Flask
EXPOSE 5000

# Commande pour démarrer l'application Flask
CMD ["python", "app.py"]
