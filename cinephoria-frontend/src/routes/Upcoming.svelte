<script>
  import { onMount } from 'svelte';
  import { tweened } from 'svelte/motion';
  import { cubicOut } from 'svelte/easing';

  let upcomingMovies = [];
  let loading = true;
  let error = "";
  let headerOpacity = tweened(0, { duration: 1000, easing: cubicOut });
  let taglineOpacity = tweened(0, { duration: 1500, easing: cubicOut, delay: 500 });

  onMount(async () => {
    try {
      const response = await fetch('https://cinephoria-backend-c53f94f0a255.herokuapp.com/movies/upcoming');
      const data = await response.json();
      upcomingMovies = data.results;
    } catch (err) {
      console.error(err);
      error = "Fehler beim Laden der kommenden Filme.";
    } finally {
      loading = false;
      headerOpacity.set(1);
      taglineOpacity.set(1);
    }
  });

  function calcDaysUntilRelease(releaseDateStr) {
    const today = new Date();
    const releaseDate = new Date(releaseDateStr);
    const diffTime = releaseDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays > 0 ? diffDays : 0;
  }

  function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('de-DE', { year: 'numeric', month: 'long', day: 'numeric' });
  }
</script>

<!-- Container mit einem verrückten, futuristischen Hintergrund -->
<div class="background">
<!-- Ein animierter, glühender Header -->
<header class="header-section">
  <h1 class="header-text" style:opacity={$headerOpacity}>CINEPHORIA - Demnächst im Kino</h1>
  <p class="tagline" style:opacity={$taglineOpacity}>Bereite dich auf ein cineastisches Feuerwerk vor!</p>
</header>

{#if loading}
  <div class="loading-screen">
    <div class="neon-loader"></div>
    <p>Lade kommende Highlights...</p>
  </div>
{:else if error}
  <p class="error">{error}</p>
{:else}
  <div class="movies-grid">
    {#each upcomingMovies as movie}
      <div class="movie-card">
        <div class="movie-image-container">
          <img src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`} alt={movie.title} class="movie-image" />
          <div class="image-overlay"></div>
          <div class="cta-overlay">
            <span class="cta-text">Bald im Kino!</span>
          </div>
        </div>
        <div class="movie-info">
          <h2 class="movie-title">{movie.title}</h2>
          <p class="release-date">Release: {formatDate(movie.release_date)}</p>
          {#if calcDaysUntilRelease(movie.release_date) > 0}
            <p class="countdown">Nur noch <span>{calcDaysUntilRelease(movie.release_date)}</span> Tage!</p>
          {:else}
            <p class="countdown">Schon verfügbar!</p>
          {/if}
          <p class="movie-overview">{movie.overview}</p>
          <div class="badge-container">
            {#if movie.vote_average}
              <div class="rating-badge">
                <i class="fas fa-star"></i> {movie.vote_average.toFixed(1)}
              </div>
            {/if}
            {#if movie.original_language}
              <div class="lang-badge">{movie.original_language.toUpperCase()}</div>
            {/if}
          </div>
        </div>
      </div>
    {/each}
  </div>
{/if}
</div>

<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
@import url('https://use.fontawesome.com/releases/v5.15.4/css/all.css');

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  background: #000;
  color: #fff;
  font-family: 'Roboto', sans-serif;
}

.background {
  position: relative;
  min-height: 100vh;
  padding: 2rem;

  overflow: hidden;
}

/* Einige schwebende Partikel / Sterne */


.header-section {
  text-align: center;
  margin-bottom: 3rem;
  margin-top: 4rem;
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

@keyframes glow {
  from {
    text-shadow: 0 0 10px #2ecc71, 0 0 20px #2ecc71;
  }
  to {
    text-shadow: 0 0 20px #2ecc71, 0 0 40px #2ecc71;
  }
}

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

.movies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 2rem;
}

.movie-card {
  background: #111;
  border-radius: 12px;
  box-shadow: 0 5px 20px rgba(0,0,0,0.5);
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  position: relative;
  display: flex;
  flex-direction: column;
}

.movie-card:hover {
  transform: translateY(-10px) scale(1.02);
  box-shadow: 0 15px 40px rgba(0,0,0,0.7);
}

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

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to bottom, transparent, rgba(0,0,0,0.8));
  opacity: 0;
  transition: opacity 0.3s;
  z-index: 1;
}

.movie-card:hover .image-overlay {
  opacity: 1;
}

.cta-overlay {
  position: absolute;
  bottom: 0;
  width: 100%;
  background-color: rgba(52,152,219,0.9);
  color: #fff;
  text-align: center;
  font-size: 1rem;
  font-weight: bold;
  padding: 0.5rem 0;
  box-sizing: border-box;
  opacity: 0;
  transform: translateY(100%);
  transition: opacity 0.3s, transform 0.3s;
  z-index: 2;
}

.movie-card:hover .cta-overlay {
  opacity: 1;
  transform: translateY(0);
}

.cta-text {
  letter-spacing: 1px;
  text-shadow: 0 0 10px #fff;
}

.movie-info {
  padding: 1rem;
  text-align: center;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}

.movie-title {
  font-size: 1.3rem;
  color: #2ecc71;
  margin: 0.5rem 0;
  text-shadow: 0 0 5px #2ecc71;
}

.release-date {
  font-size: 1rem;
  color: #3498db;
  margin: 0.5rem 0;
  font-weight: bold;
}

.countdown {
  font-size: 1rem;
  color: #fff;
  margin: 0.5rem 0;
}

.countdown span {
  color: #e74c3c;
  font-weight: bold;
  font-size: 1.1rem;
  text-shadow: 0 0 5px #e74c3c;
}

.movie-overview {
  font-size: 0.9rem;
  color: #ddd;
  margin: 0.5rem 0;
  line-height: 1.3;
  max-height: 100px;
  overflow: hidden;
  position: relative;
}

.movie-overview::after {
  content: '';
  position: absolute;
  bottom: 0;
  right: 0;
  width: 30%;
  height: 1.5em;
  background: linear-gradient(to right, transparent, #111);
}

.badge-container {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-top: auto; /* Schiebt Badges nach unten im Container */
}

.rating-badge, .lang-badge {
  padding: 0.2rem 0.5rem;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: bold;
  background: rgba(0,0,0,0.5);
  backdrop-filter: blur(2px);
  color: #fff;
}

.rating-badge i {
  color: #f1c40f;
}

.error {
  color: #e74c3c;
  text-align: center;
  font-weight: bold;
  margin-top: 20px;
}
</style>
