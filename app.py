import os
import time
import json
import threading
from datetime import datetime
import subprocess
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from datetime import timedelta

# Initialisation de l'application Flask
app = Flask(__name__)
active_threads = {}
tracking_start_time = {}

app.secret_key = "your_secret_key"

# Chemins des fichiers de configuration et de logs
CONFIG_FILE = "config/config.json"

# Charger les logs d'un projet
def load_logs(project_name):
    log_file = os.path.join('logs', f"{project_name}_log.json")
    if os.path.exists(log_file):
        with open(log_file, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []
    return []

# Sauvegarder les logs d'un projet
def save_logs(project_name, logs):
    log_file = os.path.join('logs', f"{project_name}_log.json")
    with open(log_file, "w") as file:
        json.dump(logs, file, indent=4)

# Charger la configuration des projets
def load_config():
    """Charge la configuration des projets à partir du fichier JSON"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            try:
                data = json.load(file)
                if "projects" not in data:
                    data["projects"] = []
                return data
            except json.JSONDecodeError:
                pass
    default_config = {"projects": []}
    save_config(default_config)
    return default_config

# Sauvegarder la configuration dans un fichier JSON
def save_config(data):
    """Sauvegarde la configuration dans un fichier JSON"""
    with open(CONFIG_FILE, "w") as file:
        json.dump(data, file, indent=4)

config = load_config()

# Fonction pour obtenir la branche courante d'un projet Git
def get_current_branch(project_path):
    """Retourne la branche Git courante d'un projet"""
    try:
        result = subprocess.run(
            ["git", "-C", project_path, "rev-parse", "--abbrev-ref", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        app.logger.error(f"Erreur lors de la récupération de la branche : {e.stderr}")
        return "Erreur"

def log_branch(project):
    """Enregistre les changements de branche Git d’un projet."""
    project_name = project["name"]
    log_file = os.path.join('logs', f"{project_name}_log.json")
    os.makedirs('logs', exist_ok=True)

    last_branch = get_current_branch(project["path"])
    start_time = time.time()

    while project_name in active_threads:  # Vérifie si le thread doit s'arrêter
        branch = get_current_branch(project["path"])
        current_time = time.time()

        if branch != last_branch:
            elapsed = int(current_time - start_time)
            branch_logs = load_logs(project_name)

            found = False
            for log in branch_logs:
                if log["branch"] == last_branch:
                    log["time_spent"] += elapsed
                    found = True
                    break

            if not found:
                branch_logs.append({
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "branch": last_branch,
                    "time_spent": elapsed
                })

            save_logs(project_name, branch_logs)

            start_time = current_time
            last_branch = branch

        time.sleep(1)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        project_name = request.form["project_name"]
        project_path = request.form["project_path"]

        # Vérification du chemin du projet
        if not os.path.exists(project_path):
            flash("Le chemin du projet est invalide.", "danger")
            return redirect(url_for("index"))

        new_project = {"name": project_name, "path": project_path}
        config["projects"].append(new_project)
        save_config(config)

        # Créer un fichier de log vide si nécessaire
        log_file = os.path.join('logs', f"{project_name}_log.json")
        if not os.path.exists(log_file):
            with open(log_file, 'w') as file:
                json.dump([], file)

        # Démarrer un thread pour le projet
        if project_name not in active_threads:
            thread = threading.Thread(target=log_branch, args=(new_project,), daemon=True)
            thread.start()
            active_threads[project_name] = thread  # Enregistrer le thread
            tracking_start_time[project_name] = time.time()  # Enregistrer l'heure de début

        flash(f"Projet '{project_name}' ajouté avec succès.", "success")  # Message de succès
        return redirect(url_for("index"))

    return render_template("index.html", projects=config["projects"], active_threads=active_threads)

# Supprimer un projet et ses logs associés
@app.route("/remove_project/<name>")
def remove_project(name):
    global config

    # Supprimer le fichier de log du projet
    log_file = f"logs/{name}_log.json"
    if os.path.exists(log_file):
        os.remove(log_file)

    # Supprimer le projet de la configuration
    config["projects"] = [p for p in config["projects"] if p["name"] != name]

    # Sauvegarder la configuration mise à jour
    save_config(config)
    return redirect(url_for("index"))


@app.route("/logs/<name>")
def get_logs(name):
    project = next((p for p in config["projects"] if p["name"] == name), None)

    if project is None:
        return render_template("logs.html", logs=[], project_name=None, project_path=None)

    # Si le projet est trouvé, on charge les logs
    log_file = f"logs/{name}_log.json"
    logs = []

    if os.path.exists(log_file):
        with open(log_file, "r") as file:
            logs = json.load(file)

    return render_template("logs.html", logs=logs, project_name=name, project_path=project["path"])

@app.route("/delete_log", methods=["POST"])
def delete_log():
    project_path = request.form.get("project_path")
    project_name = request.form.get("project_name")
    date = request.form.get("date")
    branch = request.form.get("branch")
    logs = load_logs(project_name)
    current_branch = get_current_branch(project_path)

    if project_name in active_threads:
        # Si un thread est actif, on empêche la suppression du log de la branche suivie
        if branch.strip().lower() == current_branch.strip().lower():
            flash("Impossible de supprimer le log de la branche actuelle. Veuillez d'abord changer de branche ou arreter le tracking du projet", "danger")
            return redirect(url_for("index"))

    logs = [log for log in logs if not (log["date"] == date and log["branch"] == branch)]

    save_logs(project_name, logs)

    flash("Log supprimé avec succès.", "success")
    return redirect(url_for("index"))

@app.route("/start_tracking/<name>")
def start_tracking(name):
    """Démarre le suivi d'un projet"""
    project = next((p for p in config["projects"] if p["name"] == name), None)
    if not project:
        flash(f"Projet '{name}' non trouvé", "danger")
        return redirect(url_for("index"))

    if name not in active_threads:
        # Enregistrer l'heure de démarrage
        tracking_start_time[name] = time.time()

        thread = threading.Thread(target=log_branch, args=(project,), daemon=True)
        thread.start()
        active_threads[name] = thread  # Enregistrer le thread

        flash(f"Suivi du projet '{name}' démarré.", "success")
        return redirect(url_for("get_logs", name=name))  # Redirige vers les logs du projet
    else:
        flash(f"⚠Suivi du projet '{name}' est déjà en cours.", "warning")
        return redirect(url_for("get_logs", name=name))  # Redirige vers les logs du projet

@app.route("/update_time", methods=["POST"])
def update_time():
    # Récupérer les données envoyées en JSON
    data = request.get_json()

    project_name = data.get("project_name")
    branch = data.get("branch")
    new_time = data.get("new_time")

    # Vérifier que le temps est fourni
    if not new_time:
        return jsonify({"error": "Le temps est manquant."}), 400

    # Convertir new_time en entier
    try:
        new_time = int(new_time)  # Convertir en entier
    except ValueError:
        return jsonify({"error": "Le temps doit être un nombre entier."}), 400

    # Charger les logs existants
    logs = load_logs(project_name)

    # Mettre à jour le temps pour la branche correspondante
    for log in logs:
        if log["branch"] == branch:
            log["time_spent"] = new_time  # Mettre à jour le temps passé
            break

    # Sauvegarder les logs après mise à jour
    save_logs(project_name, logs)

    # Retourner une réponse JSON
    return jsonify({"success": True, "new_time": new_time})


@app.route("/stop_tracking/<name>")
def stop_tracking(name):
    """Arrête le suivi d'un projet et met à jour le temps de la branche en cours"""
    if name in active_threads:
        # Récupérer le temps écoulé depuis le démarrage du suivi
        start_time = tracking_start_time.pop(name, None)
        if start_time:
            elapsed_time = int(time.time() - start_time)  # Temps écoulé en secondes

            # Ajouter le temps au log du projet
            project = next((p for p in config["projects"] if p["name"] == name), None)
            if project:
                log_file = os.path.join('logs', f"{name}_log.json")
                if os.path.exists(log_file):
                    with open(log_file, "r") as file:
                        logs = json.load(file)

                    # Identifier la branche courante
                    current_branch = get_current_branch(project["path"])

                    found = False
                    for log in logs:
                        # Vérifier si un log existe pour la branche en cours
                        if log["branch"] == current_branch:
                            log["time_spent"] += elapsed_time  # Ajouter le temps écoulé à la branche actuelle
                            found = True
                            break

                    # Si aucun log pour la branche actuelle, créer une nouvelle entrée
                    if not found:
                        logs.append({
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "branch": current_branch,
                            "time_spent": elapsed_time
                        })

                    # Sauvegarder les logs mis à jour
                    with open(log_file, "w") as file:
                        json.dump(logs, file, indent=4)

        # Supprimer le thread de suivi
        del active_threads[name]  # Supprimer le thread de la liste

        flash(f"Suivi du projet '{name}' arrêté et le temps de la branche a été mis à jour.", "success")
        return redirect(url_for("get_logs", name=name))  # Redirige vers les logs du projet
    else:
        flash(f"Le projet '{name}' n'était pas en cours de suivi.", "warning")
        return redirect(url_for("get_logs", name=name))  # Redirige vers les logs du projet



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
