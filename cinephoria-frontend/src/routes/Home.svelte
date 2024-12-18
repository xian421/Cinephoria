<!-- src/routes/Home.svelte -->
<script>
  import { onMount } from 'svelte';
  import { navigate } from 'svelte-routing';
  import { tweened } from 'svelte/motion';
  import { cubicOut } from 'svelte/easing';

  let nowPlayingMovies = [];
  let selectedMovie = null;
  let loading = true;
  let error = "";

  const API_URL = 'https://cinephoria-backend-c53f94f0a255.herokuapp.com/movies/now_playing';
  const IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500';

  // Tweened values for animations
  let headerOpacity = tweened(0, { duration: 1000, easing: cubicOut });
  let taglineOpacity = tweened(0, { duration: 1500, easing: cubicOut, delay: 500 });

  onMount(async () => {
    try {
      const response = await fetch(API_URL);
      const data = await response.json();
      nowPlayingMovies = data.results;
    } catch (err) {
      console.error('Fehler beim Laden der Filme:', err);
      error = "Fehler beim Laden der Filme.";
    } finally {
      loading = false;
      headerOpacity.set(1);
      taglineOpacity.set(1);
    }
  });

  function openModal(movie) {
    selectedMovie = movie;
  }

  function closeModal() {
    selectedMovie = null;
  }

  function navigateToDescription() {
    navigate(`/beschreibung/${selectedMovie.id}`);
    closeModal();
  }

  function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('de-DE', { year: 'numeric', month: 'long', day: 'numeric' });
  }
</script>

<!-- Container mit dem Hintergrund -->
<div class="background">
  <!-- Animierter Header -->
  <header class="header-section">
    <h1 class="header-text" style:opacity={$headerOpacity}>CINEPHORIA - Jetzt im Kino</h1>
    <p class="tagline" style:opacity={$taglineOpacity}>Tauche ein in die Welt der Blockbuster!</p>
  </header>

  {#if loading}
    <div class="loading-screen">
      <div class="neon-loader"></div>
      <p>Lade aktuelle Filme...</p>
    </div>
  {:else if error}
    <p class="error">{error}</p>
  {:else}
    <main>
      <!-- Filmliste -->
      <section class="movies-grid">
        {#each nowPlayingMovies as movie}
          <article class="movie-card">
            <div class="movie-image-container">
              <img src="{IMAGE_BASE_URL}{movie.poster_path}" alt="{movie.title}" class="movie-image" />
              <div class="image-overlay"></div>
              <div class="cta-overlay">
                <span class="cta-text">Jetzt im Kino!</span>
              </div>
            </div>
            <div class="movie-info">
              <h2 class="movie-title">{movie.title}</h2>
              <p class="movie-overview">{movie.overview}</p>
              <button class="more-info-button" on:click={() => openModal(movie)}>Mehr Infos</button>
            </div>
          </article>
        {/each}
      </section>
    </main>
  {/if}

  <!-- Modal -->
  {#if selectedMovie}
    <div
      class="modal"
      on:click={closeModal}
      tabindex="0"
      role="button"
      aria-label="Modal schließen"
      on:keydown={(event) => {
        if (event.key === 'Enter' || event.key === ' ') {
          closeModal();
        }
      }}
    >
      <div class="modal-content" role="dialog" aria-modal="true" on:click|stopPropagation>
        <button class="close" on:click={closeModal} aria-label="Modal schließen">
          &times;
        </button>
        <div class="modal-header">
          <img
            class="poster"
            src="{IMAGE_BASE_URL}{selectedMovie.poster_path}"
            alt="{selectedMovie.title}"
          />
          <div class="info">
            <h2>{selectedMovie.title}</h2>
            <p><strong>Originaltitel:</strong> {selectedMovie.original_title}</p>
            <p><strong>Sprache:</strong> {selectedMovie.original_language.toUpperCase()}</p>
            <p><strong>Release-Datum:</strong> {selectedMovie.release_date}</p>
            <p><strong>Beliebtheit:</strong> {selectedMovie.popularity}</p>
            <p><strong>Bewertung:</strong> {selectedMovie.vote_average} / 10 ({selectedMovie.vote_count} Stimmen)</p>
            <button class="more-info" on:click={navigateToDescription}>
              Weitere Informationen
            </button>
          </div>
        </div>
        <div class="modal-body">
          <p>{selectedMovie.overview}</p>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
  @import url('https://use.fontawesome.com/releases/v5.15.4/css/all.css');

  /* Globales Box-Sizing */
  * {
    box-sizing: border-box;
  }

  /* Entferne Standard-Margen und -Paddings */
  html, body {
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
    font-family: 'Roboto', sans-serif;
    background: #000;
    color: #fff;
    overflow-x: hidden; /* Verhindert horizontales Scrollen */
  }

  /* Hintergrundbereich */
  .background {
  position: relative;
  min-height: 100vh;
  padding: 2rem; /* Entferne oder passe das Padding an */
  background: linear-gradient(135deg, #000428, #004e92);
  overflow: hidden;
  /* padding-top: 120px; Entfernen */
  box-sizing: border-box;
}

  /* Header-Stil */
  .header-section {
    text-align: center;
    margin-bottom: 3rem;
  }

  .header-text {
    font-size: 3rem;
    margin: 0;
    color: #2ecc71;
    text-shadow: 0 0 20px #2ecc71, 0 0 40px #2ecc71;
    animation: glow 2s infinite alternate;
  }

  .tagline {
    font-size: 1.5rem;
    color: #fff;
    margin-top: 1rem;
    text-shadow: 0 0 10px #fff;
  }

  /* Glow-Animation */
  @keyframes glow {
    from {
      text-shadow: 0 0 10px #2ecc71, 0 0 20px #2ecc71;
    }
    to {
      text-shadow: 0 0 20px #2ecc71, 0 0 40px #2ecc71;
    }
  }

  /* Ladebildschirm */
  .loading-screen {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #fff;
    margin-top: 5rem;
  }

  .neon-loader {
    width: 50px;
    height: 50px;
    border: 5px solid #2ecc71;
    border-top: 5px solid transparent;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 1rem;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  /* Fehlernachricht */
  .error {
    color: #e74c3c;
    text-align: center;
    font-weight: bold;
    margin-top: 20px;
  }

  /* Hauptinhalt */
  main {
    padding: 0 2rem; /* Seitliche Abstände */
  }

  /* Filmliste */
  .movies-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 2rem;
    width: 100%;
    margin: 0; /* Entferne Standard-Margin */
    padding: 0; /* Entferne Standard-Padding */
  }

  /* Einzelne Filmkarte */
  .movie-card {
    background: #111;
    border-radius: 12px;
    box-shadow: 0 5px 20px rgba(0,0,0,0.5);
    overflow: hidden;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    position: relative;
    display: flex;
    flex-direction: column;
    max-width: 100%; /* Verhindert Überlaufen */
  }

  .movie-card:hover {
    transform: translateY(-10px) scale(1.02);
    box-shadow: 0 15px 40px rgba(0,0,0,0.7);
  }

  /* Bildcontainer */
  .movie-image-container {
    position: relative;
    overflow: hidden;
    width: 100%;
  }

  .movie-image {
    width: 100%;
    display: block;
    object-fit: cover;
    transition: transform 0.3s;
  }

  .movie-card:hover .movie-image {
    transform: scale(1.1);
  }

  /* Bildüberlagerung */
  .image-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right:0;
    bottom:0;
    background: linear-gradient(to bottom, transparent, rgba(0,0,0,0.8));
    opacity:0;
    transition: opacity 0.3s;
    z-index:1;
  }

  .movie-card:hover .image-overlay {
    opacity:1;
  }

  /* Call-to-Action Überlagerung */
  .cta-overlay {
    position: absolute;
    bottom:0;
    width:100%;
    background-color: rgba(52,152,219,0.9);
    color:#fff;
    text-align:center;
    font-size:1rem;
    font-weight:bold;
    padding:0.5rem 0;
    box-sizing:border-box;
    opacity:0;
    transform: translateY(100%);
    transition: opacity 0.3s, transform 0.3s;
    z-index:2;
  }

  .movie-card:hover .cta-overlay {
    opacity:1;
    transform: translateY(0);
  }

  .cta-text {
    letter-spacing:1px;
    text-shadow:0 0 10px #fff;
  }

  /* Film-Informationen */
  .movie-info {
    padding:1rem;
    text-align:center;
    display:flex;
    flex-direction:column;
    justify-content:flex-start;
    flex:1;
  }

  .movie-title {
    font-size:1.3rem;
    color:#2ecc71;
    margin:0.5rem 0;
    text-shadow:0 0 5px #2ecc71;
  }

  .movie-overview {
    font-size:0.9rem;
    color:#ddd;
    margin:0.5rem 0;
    line-height:1.3;
    position:relative;
    max-height:80px;
    overflow:hidden;
  }

  .movie-overview::after {
    content:'';
    position:absolute;
    bottom:0;
    right:0;
    width:30%;
    height:1.5em;
    background:linear-gradient(to right, transparent, #111);
  }

  .more-info-button {
    background:#2ecc71;
    color:#000;
    padding:0.5rem 1rem;
    border:none;
    border-radius:8px;
    font-weight:bold;
    cursor:pointer;
    margin-top:auto;
    transition: background-color 0.3s;
  }

  .more-info-button:hover {
    background:#34d399;
  }

  /* Modal */
  .modal {
    position:fixed;
    top:0;
    left:0;
    width:100%;
    height:100%;
    background-color: rgba(0,0,0,0.8);
    display:flex;
    justify-content:center;
    align-items:center;
    z-index:2000;
  }

  .modal-content {
    background:#111;
    color:#fff;
    padding:20px;
    border-radius:12px;
    width:90%;
    max-width:800px;
    max-height:90%;
    overflow-y:auto;
    box-shadow:0 0 20px #2ecc71;
    position:relative;
  }

  .modal-header {
    display:flex;
    gap:20px;
    align-items:flex-start;
    flex-wrap:wrap;
  }

  .poster {
    width:30%;
    border-radius:8px;
    box-shadow:0 0 10px #2ecc71;
  }

  .info h2 {
    color:#2ecc71;
    text-shadow:0 0 5px #2ecc71;
    margin-bottom:10px;
  }

  .info p {
    margin-bottom:8px;
  }

  .more-info {
    background:#2ecc71;
    color:#000;
    padding:0.6rem 1rem;
    border:none;
    border-radius:8px;
    font-weight:bold;
    cursor:pointer;
    transition: background-color 0.3s ease;
    margin-top:10px;
  }

  .more-info:hover {
    background:#34d399;
  }

  .modal-body {
    margin-top:20px;
    color:#fff;
  }

  .close {
    position:absolute;
    top:10px;
    right:10px;
    background:none;
    border:none;
    font-size:1.5rem;
    cursor:pointer;
    color:#fff;
    transition: color 0.3s ease;
  }

  .close:hover {
    color:#2ecc71;
  }

  /* Sicherstellen, dass Bilder nicht überlaufen */
  img {
    max-width:100%;
    height:auto;
    display:block;
  }
</style>
