<!-- src/routes/NowPlaying.svelte -->
<script>
  import { onMount } from 'svelte';
  import { navigate } from 'svelte-routing';
  import Swal from 'sweetalert2';
  import { fetchNowPlayingMovies, fetchShowtimesPublic } from '../services/api.js';
  import { tweened } from 'svelte/motion';
  import { cubicOut } from 'svelte/easing';

  // State-Variablen
  let nowPlayingMovies = [];
  let showtimes = [];
  let groupedMovies = {};

  // Variablen für Lade- und Fehlerzustände
  let loading = true;
  let error = "";
  let isOpen = false;
  let selectedMovie = null;

  // Animationen für Header und Tagline
  let headerOpacity = tweened(0, { duration: 1000, easing: cubicOut });
  let taglineOpacity = tweened(0, { duration: 1500, easing: cubicOut, delay: 500 });

  // Mapping für Wochentage
  const daysOfWeekMap = {
    0: "Sonntag",
    1: "Montag",
    2: "Dienstag",
    3: "Mittwoch",
    4: "Donnerstag",
    5: "Freitag",
    6: "Samstag",
  };

  const IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500';

  // Funktion zur Datumsformatierung
  function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('de-DE', { year: 'numeric', month: 'long', day: 'numeric' });
  }

  // Gruppiert Showtimes den entsprechenden Filmen zu
  function groupMoviesWithShowtimes(movies, showtimes) {
    const showtimesMap = showtimes.reduce((acc, showtime) => {
      if (!acc[showtime.movie_id]) {
        acc[showtime.movie_id] = [];
      }
      acc[showtime.movie_id].push(showtime);
      return acc;
    }, {});

    return movies.map(movie => ({
      ...movie,
      showtimes: showtimesMap[movie.id] || []
    }));
  }

  // Gruppiert Filme mit Showtimes nach Datum
  function groupMoviesByDate(moviesWithShowtimes) {
    const grouped = {};

    moviesWithShowtimes.forEach(movie => {
      movie.showtimes.forEach(showtime => {
        const date = showtime.start_time.split('T')[0];
        if (!grouped[date]) {
          grouped[date] = [];
        }
        grouped[date].push({
          ...movie,
          showtime
        });
      });
    });

    // Sortiere die Showtimes innerhalb jedes Datums nach der Startzeit
    for (const date in grouped) {
      grouped[date].sort((a, b) => new Date(a.showtime.start_time) - new Date(b.showtime.start_time));
    }

    return grouped;
  }

  // Daten beim Mounten der Komponente laden
  onMount(async () => {
    try {
      // Lade jetzt laufende Filme und Showtimes gleichzeitig
      const [moviesData, showtimesData] = await Promise.all([
        fetchNowPlayingMovies(),
        fetchShowtimesPublic()
      ]);

      nowPlayingMovies = moviesData.results;
      showtimes = showtimesData.showtimes;

      // Gruppiere Filme mit ihren Showtimes
      const moviesWithShowtimes = groupMoviesWithShowtimes(nowPlayingMovies, showtimes);

      // Gruppiere die Filme nach Datum
      groupedMovies = groupMoviesByDate(moviesWithShowtimes);
    } catch (err) {
      console.error('Fehler beim Laden der Filme oder Showtimes:', err);
      error = "Es gab ein Problem beim Laden der Daten. Bitte versuche es später erneut.";
      Swal.fire({
        title: "Fehler",
        text: error,
        icon: "error",
        confirmButtonText: "OK",
      });
    } finally {
      loading = false;
      headerOpacity.set(1);
      taglineOpacity.set(1);
    }
  });

  // Navigation zur Film-Beschreibung
  function navigateToDescription(movie) {
    console.log('Navigiere zu Beschreibung mit ID:', movie.id);
    navigate(`/beschreibung/${movie.id}`);
  }

  // Öffnen des Popups
  function openPopup(movie) {
    selectedMovie = movie;
    isOpen = true;
  }

  // Schließen des Popups
  function onClose() {
    isOpen = false;
    selectedMovie = null;
  }
</script>

<!-- Container mit einem futuristischen, animierten Hintergrund -->
<div class="background">
  <!-- Animierter, glühender Header -->
  <header class="header-section">
    <h1 class="header-text" style:opacity={$headerOpacity}>CINEPHORIA - Aktuell im Kino</h1>
    <p class="tagline" style:opacity={$taglineOpacity}>Erlebe die neuesten Filme in deiner Nähe!</p>
  </header>

  {#if loading}
    <div class="loading-screen">
      <div class="neon-loader"></div>
      <p>Lade aktuelle Filme...</p>
    </div>
  {:else if error}
    <p class="error">{error}</p>
  {:else}
    <div class="movies-grid">
      {#each Object.keys(groupedMovies).sort((a, b) => new Date(a) - new Date(b)) as dateKey}
        <section>
          <div class="day-header">
            <h2>
              {daysOfWeekMap[new Date(dateKey).getDay()] || "Unbekannter Tag"}, {formatDate(dateKey)}
            </h2>
          </div>
          <div class="movies-container">
            {#each groupedMovies[dateKey] as { showtime, ...movie }}
              <article class="movie-card">
                <button
                  class="movie-button"
                  on:click={() => navigateToDescription(movie)}
                  aria-label="Details zu {movie.title} anzeigen"
                >
                  <div class="movie-image-container">
                    <img src="{IMAGE_BASE_URL}{movie.poster_path}" alt={movie.title} />
                    <div class="image-overlay"></div>
                    <div class="cta-overlay">
                      <span class="cta-text">Tickets</span>
                    </div>
                  </div>
                </button>
                <div class="movie-info">
                  <h2 class="movie-title">{movie.title}</h2>
                  
                  {#if showtime}
                    <p class="showtime">
                      Startzeit: {new Date(showtime.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  {/if}
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
              </article>
            {/each}
          </div>
        </section>
      {/each}
    </div>
  {/if}
</div>

<!-- Popup für Filmdetails -->
{#if isOpen && selectedMovie}
  <div class="popup-overlay" on:click={onClose}>
    <div class="popup-content" on:click|stopPropagation>
      <button class="close-button" on:click={onClose}>×</button>
      <div class="popup-movie-details">
        <img src={`https://image.tmdb.org/t/p/w500${selectedMovie.poster_path}`} alt={selectedMovie.title} />
        <h2>{selectedMovie.title}</h2>
        <p>Release Datum: {formatDate(selectedMovie.release_date)}</p>
        <p>Sprache: {selectedMovie.original_language.toUpperCase()}</p>
        <p>Bewertung: {selectedMovie.vote_average.toFixed(1)}</p>
        <button class="view-details" on:click={() => navigateToDescription(selectedMovie)}>Weitere Details</button>
      </div>
    </div>
  </div>
{/if}

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
    background: linear-gradient(135deg, #000428, #004e92);
    overflow: hidden;
  }

  /* Animierter, glühender Header */
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
    white-space: nowrap;
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

  /* Loader-Stil */
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

  /* Grid und Kartenstil */
  .movies-grid {
    display: flex;
    flex-direction: column;
    gap: 2rem;
  }

  section {
    margin: 20px 0;
    padding: 10px 20px;
    background: rgba(0, 0, 0, 0.5);
    border-radius: 12px;
  }

  .day-header {
    margin-bottom: 10px;
    text-align: center;
  }

  .day-header h2 {
    font-size: 1.5rem;
    color: #2ecc71;
    text-shadow: 0 0 10px #2ecc71;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .movies-container {
    display: flex;
    gap: 16px;
    overflow-x: auto;
    overflow-y: hidden;
    padding-bottom: 10px;
    scrollbar-width: thin;
    white-space: nowrap;
  }

  .movies-container::-webkit-scrollbar {
    height: 8px;
  }

  .movies-container::-webkit-scrollbar-thumb {
    background-color: #3498db;
    border-radius: 8px;
  }

  .movie-card {
    flex: 0 0 220px;
    background: #111;
    border-radius: 12px;
    box-shadow: 0 5px 20px rgba(0,0,0,0.5);
    overflow: hidden;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    position: relative;
    display: flex;
    flex-direction: column;
    cursor: pointer;
  }

  .movie-card:hover {
    transform: translateY(-10px) scale(1.02);
    box-shadow: 0 15px 40px rgba(0,0,0,0.7);
  }

  .movie-button {
    background: none;
    border: none;
    padding: 0;
    margin: 0;
    width: 100%;
    text-align: left;
    cursor: pointer;
    position: relative;
  }

  .movie-image-container {
    position: relative;
    overflow: hidden;
    width: 100%;
    height: 330px;
  }

  .movie-image {
    width: 100%;
    height: 100%;
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
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .movie-info {
    padding: 1rem;
    text-align: center;
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    background: rgba(0, 0, 0, 0.7);
  }

  .movie-title {
    font-size: 1.3rem;
    color: #2ecc71;
    margin: 0.5rem 0;
    text-shadow: 0 0 5px #2ecc71;
    word-wrap: break-word;
    word-break: break-word;
    white-space: normal;
    overflow: hidden;
    text-align: center;
  }

  .release-date, .showtime {
    font-size: 1rem;
    color: #3498db;
    margin: 0.3rem 0;
    font-weight: bold;
  }

  .badge-container {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    margin-top: auto;
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

  .lang-badge {
    background-color: #3498db;
  }

  .error {
    color: #e74c3c;
    text-align: center;
    font-weight: bold;
    margin-top: 20px;
  }

  /* Popup Styles */
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
    border-radius: 12px;
    max-width: 500px;
    width: 90%;
    text-align: center;
    position: relative;
    color: #fff;
    box-shadow: 0 5px 15px rgba(0,0,0,0.5);
    animation: fadeIn 0.5s ease;
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: scale(0.9); }
    to { opacity: 1; transform: scale(1); }
  }

  .popup-movie-details img {
    width: 100%;
    border-radius: 8px;
    margin-bottom: 10px;
  }

  .popup-movie-details h2 {
    margin: 10px 0;
    font-size: 1.8rem;
    color: #2ecc71;
    text-shadow: 0 0 10px #2ecc71;
  }

  .popup-movie-details p {
    margin: 5px 0;
    font-size: 1rem;
    color: #fff;
  }

  .view-details {
    margin-top: 15px;
    padding: 0.5rem 1rem;
    background-color: #3498db;
    border: none;
    border-radius: 8px;
    color: #fff;
    font-weight: bold;
    cursor: pointer;
    transition: background-color 0.3s;
  }

  .view-details:hover {
    background-color: #2980b9;
  }

  .close-button {
    position: absolute;
    top: 10px;
    right: 15px;
    background: none;
    border: none;
    font-size: 2rem;
    cursor: pointer;
    color: #fff;
    transition: color 0.3s;
  }

  .close-button:hover {
    color: #e74c3c;
  }

  /* Responsive Anpassungen */
  @media (max-width: 768px) {
    .header-text {
      font-size: 2.5rem;
    }

    .tagline {
      font-size: 1.2rem;
    }

    .movie-card {
      flex: 0 0 180px;
    }

    .movie-info {
      padding: 0.8rem;
    }

    .movie-title {
      font-size: 1.1rem;
    }

    .release-date, .showtime {
      font-size: 0.9rem;
    }

    .cta-text {
      font-size: 0.9rem;
    }

    .popup-content {
      max-width: 90%;
    }
  }
</style>
