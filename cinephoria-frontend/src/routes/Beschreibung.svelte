<!-- src/routes/Beschreibung.svelte -->
<script>
  import { onMount } from 'svelte';
  import { navigate } from 'svelte-routing';
  import Swal from 'sweetalert2';
  import { fetchMovieDetails, fetchMovieFSK, fetchShowtimesByMovie, fetchScreens, fetchMovieTrailerUrl } from '../services/api.js';
  import { get } from 'svelte/store';
  import { authStore } from '../stores/authStore'; 
  import "@fortawesome/fontawesome-free/css/all.min.css";

  // Für Animationen des Headers und Tagline
  import { tweened } from 'svelte/motion';
  import { cubicOut } from 'svelte/easing';

  export let id; // ID wird von der Route übergeben

  let moviefsk = {};  
  let movieDetails = {};
  let showtimes = [];
  let screens = {}; // Map von screen_id zu screen_details
  const IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500';
  let isLoading = true;
  let error = null;

  let movie_certification = "";

  // Variablen für das Trailer Popup
  let isTrailerOpen = false;
  let trailerUrl = ''; 

  // Animation für Header und Tagline
  let headerOpacity = tweened(0, { duration: 1000, easing: cubicOut });
  let taglineOpacity = tweened(0, { duration: 1500, easing: cubicOut, delay: 500 });

  onMount(async () => {
    if (!id) {
      console.error('Keine ID gefunden!');
      error = 'Keine ID gefunden!';
      isLoading = false;
      return;
    }
    try {
      const [details, fsk, showtimesData, screensData] = await Promise.all([
        fetchMovieDetails(id),
        fetchMovieFSK(id),
        fetchShowtimesByMovie(id),
        fetchScreens(get(authStore).token)
      ]);

      movieDetails = details;
      moviefsk = fsk;
      try {
        movie_certification = moviefsk.release_dates[0].certification;
        if (movie_certification == '') {
          movie_certification = moviefsk.release_dates[1].certification;
        }
      } catch (error) {
        movie_certification = "Keine Angaben";
        console.error('Fehler beim Laden der FSK:', error);
      }

      showtimes = showtimesData.showtimes;

      screensData.screens.forEach(screen => {
        screens[screen.screen_id] = screen;
      });
      
    } catch (err) {
      console.error('Netzwerkfehler:', err);
      error = 'Netzwerkfehler. Bitte versuche es erneut.';
      Swal.fire({
        title: "Fehler",
        text: error,
        icon: "error",
        confirmButtonText: "OK",
      });
    } finally {
      isLoading = false;
      headerOpacity.set(1);
      taglineOpacity.set(1);
    }
  });

  function navigateToBooking(showtime) {
    console.log('Navigiere zu Buchung mit Showtime ID:', showtime.showtime_id);
    navigate(`/buchung/${showtime.showtime_id}`);
  }

  // Trailer Popup öffnen
  async function openTrailerModal() {
    isTrailerOpen = true;
    try {
      const token = get(authStore).token;
      const url = await fetchMovieTrailerUrl(token, id);
      trailerUrl = url;
    } catch (err) {
      console.error('Fehler beim Abrufen der Trailer-URL:', err);
      Swal.fire({
        title: "Fehler",
        text: err.message || 'Fehler beim Abrufen der Trailer-URL.',
        icon: "error",
        confirmButtonText: "OK",
      });
      closeTrailerModal();
    }
  }

  // Trailer Popup schließen
  function closeTrailerModal() {
    isTrailerOpen = false;
    trailerUrl = '';
  }
</script>

<div class="background">
  <header class="header-section">
    <h1 class="header-text" style:opacity={$headerOpacity}>CINEPHORIA - Filmbeschreibung</h1>
    <p class="tagline" style:opacity={$taglineOpacity}>Erlebe futuristischen Film-Genuss!</p>
  </header>

  <!-- Modal für Trailer -->
  {#if isTrailerOpen}
    <div class="popup-overlay" on:click={closeTrailerModal}>
      <div class="popup-content" on:click|stopPropagation>
        <button class="close-button" on:click={closeTrailerModal}>×</button>
        <div class="popup-trailer">
          {#if trailerUrl}
            <iframe
              src="{trailerUrl}"
              title="YouTube video player"
              frameborder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowfullscreen
            ></iframe>
          {:else}
            <p>Trailer wird geladen...</p>
          {/if}
        </div>
      </div>
    </div>
  {/if}

  <main>
    {#if isLoading}
      <p class="loading-text">Lade Filmdetails...</p>
    {:else if error}
      <p class="error">{error}</p>
    {:else if movieDetails.title}
      <div class="movie-container">
        <!-- Linke Spalte: Poster -->
        <div class="poster-container">
          <img
            src="{IMAGE_BASE_URL}{movieDetails.poster_path}"
            alt="{movieDetails.title}"
            class="poster"
            on:click={openTrailerModal}
          />
          <div class="poster-overlay">
            <span class="poster-cta">Trailer ansehen!</span>
          </div>
        </div>

        <!-- Mittlere Spalte: Details -->
        <div class="details">
          <div class="title">{movieDetails.title}</div>
          <div class="tagline-text">{movieDetails.tagline}</div>
          <div class="meta">
            <div><i class="fas fa-clock"></i> {movieDetails.runtime}'</div>    
            <div>FSK: {movie_certification}</div> 
            <div>Genre: {movieDetails.genres ? movieDetails.genres.map((genre) => genre.name).join(", ") : 'Keine Angaben'}</div>
          </div>
          <div class="description">{movieDetails.overview}</div>
        </div> 

        <!-- Rechte Spalte: Showtimes -->
        <div class="showtimes">
          {#if showtimes.length > 0}
            <div class="showtimes-container">
              {#each showtimes as showtime}
                <div class="showtime-box" on:click={() => navigateToBooking(showtime)}>
                  <div class="showtime-date">
                    {new Date(showtime.start_time).toLocaleDateString()}
                  </div>
                  <div class="showtime-time">
                    {new Date(showtime.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} Uhr
                  </div>
                  <div class="showtime-screen">
                    {screens[showtime.screen_id]?.name || 'Unbekannt'}
                  </div>
                </div>
              {/each}
              <div class="more-shows">
                <div class="more-shows-text">+13(stimmt net)</div>
                <div class="more-shows-subtext">weitere<br>Vorstellungen</div>
              </div>
            </div>
          {:else}
            <p>Keine Vorstellungen verfügbar.</p>
          {/if}
        </div>
      </div>
    {:else}
      <p>Filmdetails konnten nicht geladen werden.</p>
    {/if}
  </main>
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
  text-align: center;
}

@keyframes glow {
  from {
    text-shadow: 0 0 10px #2ecc71, 0 0 20px #2ecc71;
  }
  to {
    text-shadow: 0 0 20px #2ecc71, 0 0 40px #2ecc71;
  }
}

.loading-text {
  text-align: center;
  margin-top: 5rem;
  font-size: 1.2rem;
  color: #fff;
}

.error {
  color: #e74c3c;
  font-size: 1.2rem;
  margin: 2rem;
  text-align: center;
}

.movie-container {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
  justify-content: center;
  max-width: 1200px;
  margin: 0 auto;
}

.poster-container {
  position: relative;
  cursor: pointer;
}

.poster {
  max-width: 300px;
  border-radius: 8px;
  box-shadow: 0 5px 20px rgba(0,0,0,0.5);
  transition: transform 0.3s ease;
}

.poster:hover {
  transform: scale(1.05);
}

.poster-overlay {
  position: absolute;
  bottom: 0;
  width: 100%;
  background-color: rgba(46,204,113,0.9);
  color: #000;
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

.poster-container:hover .poster-overlay {
  opacity: 1;
  transform: translateY(0);
}

.poster-cta {
  letter-spacing: 1px;
  text-shadow: 0 0 10px #fff;
}

.details {
  flex: 2;
  min-width: 300px;
  background: #111;
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 5px 20px rgba(0,0,0,0.5);
}

.title {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
  color: #2ecc71;
  text-shadow: 0 0 10px #2ecc71;
  text-align: center;
}

.tagline-text {
  font-style: italic;
  color: #888;
  margin-bottom: 1rem;
  text-align: center;
}

.meta {
  margin-bottom: 1.5rem;
  color: #fff;
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
}

.meta i {
  font-size: 20px; 
  color: #2ecc71; 
  margin-right: 2px; 
  vertical-align: middle;
}

.description {
  margin-bottom: 2rem;
  line-height: 1.6;
  color: #ddd;
}

.showtimes {
  flex: 1;
  min-width: 250px;
  max-width: 300px;
}

.showtimes-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.showtime-box {
  background-color: #2ecc71;
  border-radius: 8px;
  padding: 0.5rem;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  color: #000;
  text-align: center;
}

.showtime-box:hover {
  transform: translateY(-5px) scale(1.05);
  box-shadow: 0 4px 8px rgba(0,0,0,0.5);
}

.showtime-date {
  font-weight: bold;
  font-size: 0.9rem;
}

.showtime-time {
  font-weight: bold;
  font-size: 1.6rem;
}

.showtime-screen {
  font-size: 0.7rem;
}

.more-shows {
  display: inline-block; 
  padding: 10px; 
  background-color: #3498db; 
  color: white; 
  clip-path: polygon(0 0, 90% 0, 100% 50%, 90% 100%, 0 100%); 
  font-family: Arial, sans-serif; 
  font-size: 16px; 
  text-align: center;
  transition: transform 0.3s, box-shadow 0.3s;
}

.more-shows:hover {
  transform: translateY(-5px) scale(1.05);
  box-shadow: 0 4px 8px rgba(0,0,0,0.5);
}

.more-shows-text {
  font-size: 24px; 
  font-weight: bold;
}

.more-shows-subtext {
  font-size: 14px;
}

.popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.popup-content {
  background: #111;
  padding: 20px;
  border-radius: 8px;
  max-width: 950px;
  width: 90%;
  text-align: center;
  position: relative;
  box-shadow: 0 5px 20px rgba(0,0,0,0.5);
}

.popup-content p {
  color: #fff;
}

.close-button {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #fff;
}

.close-button:hover {
  color: #e74c3c;
}

.popup-trailer iframe {
  width: 100%; 
  height: 600px;
  border: none;
  border-radius: 8px;
}

@media (max-width: 600px) {
  .popup-trailer iframe {
    height: 200px;
  }
}

@media (max-width: 1000px) {
  .movie-container {
    flex-direction: column;
    align-items: center;
  }

  .showtimes {
    max-width: none;
    width: 100%;
  }
}
</style>
