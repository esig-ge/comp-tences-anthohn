var gestionnaireRecherche = function (evenement) {
    // utiliser plutot la route (url) de la view search_videos
    fetch(`{% url 'search_videos' %}?q=${searchInput.value}`)
        .then(response => response.json()) // Convertit la réponse en JSON
        .then(data => {
            // Vider les anciens résultats
            resultsContainer.innerHTML = '';
            // Afficher la boîte de résultats
            resultsContainer.style.display = 'block';

            // Pour chaque vidéo trouvée...
            data.forEach(video => {
                // Créer un lien HTML simple
                const lienVideo = `<a href="/video/${video.id}/" class="search-result-item">${video.title}</a>`;
                // Ajouter ce lien dans la boîte de résultats
                resultsContainer.innerHTML += lienVideo;
            });
        });
}
//Sélectionner les éléments HTML dont on a besoin
const searchInput = document.getElementById('search-input');
const resultsContainer = document.getElementById('search-results');
//Ecouter l'événement "input" (quand l'utilisateur tape quelque chose)
searchInput.addEventListener("input", gestionnaireRecherche);