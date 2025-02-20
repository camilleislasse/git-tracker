document.addEventListener("DOMContentLoaded", function () {
    // Charger le dernier projet depuis le localStorage si disponible
    const lastProject = localStorage.getItem("last_project");

    if (lastProject) {
        fetchLogs(lastProject);
    }

    document.querySelectorAll(".view-logs").forEach(button => {
        button.addEventListener("click", function () {
            let projectName = this.dataset.name;

            // Sauvegarder le dernier projet dans localStorage
            localStorage.setItem("last_project", projectName);

            // Charger les logs du projet
            fetchLogs(projectName);
        });
    });

    function fetchLogs(projectName) {
        fetch(`/logs/${encodeURIComponent(projectName)}`)
            .then(response => response.text())
            .then(html => {
                document.getElementById("logs-container").innerHTML = html;
            })
            .catch(error => console.error("Erreur lors du chargement des logs :", error));
    }
});

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".start-tracking, .stop-tracking").forEach(button => {
        button.addEventListener("click", function () {
            let projectName = this.dataset.name;
            let action = this.classList.contains("start-tracking") ? "start_tracking" : "stop_tracking";

            fetch(`/${action}/${projectName}`)
                .then(response => response.text())
                .then(data => {
                    location.reload(); // Recharge la page pour mettre à jour l'affichage
                })
                .catch(error => console.error("Erreur:", error));
        });
    });
});
document.addEventListener("DOMContentLoaded", function () {
    document.body.addEventListener("click", function (event) {
        if (event.target.classList.contains("editable-time")) {
            let badge = event.target;
            let currentValue = badge.innerText.trim();
            let updateUrl = badge.dataset.url; // Récupère l'URL depuis l'attribut

            let input = document.createElement("input");
            input.type = "number";
            input.value = currentValue;
            input.classList.add("form-control", "d-inline-block");
            input.style.width = "80px";

            badge.replaceWith(input);
            input.focus();

            input.addEventListener("blur", function () {
                let newValue = input.value.trim();

                if (newValue !== "" && newValue !== currentValue) {
                    badge.innerText = newValue;

                    // Conversion de la valeur en minutes en secondes
                    let timeInSeconds = newValue * 60;

                    // Envoi de la donnée en secondes au serveur
                    fetch(updateUrl, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            project_name: badge.dataset.project,
                            branch: badge.dataset.branch,
                            new_time: timeInSeconds  // Envoie les secondes au lieu des minutes
                        })
                    })
                        .then(response => response.json())
                        .then(data => console.log("Réponse serveur :", data))
                        .catch(error => console.error("Erreur :", error));

                    console.log("Données envoyées :", {
                        project_name: badge.dataset.project,
                        branch: badge.dataset.branch,
                        new_time: timeInSeconds
                    });
                }

                input.replaceWith(badge);
            });

            input.addEventListener("keypress", function (event) {
                if (event.key === "Enter") {
                    input.blur();
                }
            });
        }
    });
});
