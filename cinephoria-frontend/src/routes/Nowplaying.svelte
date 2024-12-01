<!-- src/routes/NowPlaying.svelte -->
<script>
  import { onMount } from 'svelte';
  import { navigate } from 'svelte-routing';
  import Swal from 'sweetalert2';
  import { fetchNowPlayingMovies, fetchShowtimesPublic } from '../services/api.js';

  // State-Variablen
  let nowPlayingMovies = [];
  let showtimes = [];
  let groupedMovies = {};

  // Variablen für Lade- und Fehlerzustände
  let loading = true;
  let error = "";
  let isOpen = false;
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
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}.${month}.${year}`;
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
    } catch (error) {
      console.error('Fehler beim Laden der Filme oder Showtimes:', error);
      error = "Es gab ein Problem beim Laden der Daten. Bitte versuche es später erneut.";
      Swal.fire({
        title: "Fehler",
        text: error,
        icon: "error",
        confirmButtonText: "OK",
      });
    } finally {
      loading = false;
    }
  });

  // Navigation zur Film-Beschreibung
  function navigateToDescription(movie) {
    console.log('Navigiere zu Beschreibung mit ID:', movie.id);
    navigate(`/beschreibung/${movie.id}`);
  }
</script>

<!-- Popup für Filmdetails -->
{#if isOpen && movie}
  <div class="popup-overlay" on:click={onClose}>
    <div class="popup-content" on:click|stopPropagation>
      <button class="close-button" on:click={onClose}>×</button>
      <div class="popup-movie-details">
        <img src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`} alt={movie.title} />
        <h2>{movie.title}</h2>
        <p>Datum: {movie.showDate}</p>
      </div>
    </div>
  </div>
{/if}

<main>
  {#if loading}
    <p>Lade Daten...</p>
  {:else if error}
    <p class="error">{error}</p>
  {:else}
    <h1>Aktuelles Kinoprogramm im CINEPHORIA</h1>

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
                  <img src="{IMAGE_BASE_URL}{movie.poster_path}" alt="{movie.title}" />
                  <div class="movie-hover-overlay">
                    <span class="movie-title">{movie.title}</span>
                    <span class="showtime-info">
                      {new Date(showtime.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                </div>
              </button>
            </article>
          {/each}
        </div>
      </section>
    {/each}
  {/if}
</main>

<style>
  /* Bestehende Stile */

  h1 {
    text-align: center;
    margin: 20px 0;
    font-size: 2rem;
    color: #333;
  }

  section {
    margin: 20px 0;
    padding: 10px 20px;
  }

  .day-header {
    margin-bottom: 10px;
  }

  h2 {
    font-size: 1.5rem;
    color: #444;
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
    flex: 0 0 200px;
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    cursor: pointer;
    position: relative; /* Für die Positionierung des Hover-Overlays */
  }

  .movie-card:hover {
    transform: scale(0.95);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
  }

  .movie-image-container {
    position: relative;
    width: 100%;
    aspect-ratio: 2 / 3;
    overflow: hidden;
  }

  .movie-image-container img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: opacity 0.3s linear;
  }

  .movie-image-container:hover img {
    opacity: 0.7;
  }

  .movie-hover-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background-color: rgba(0, 0, 0, 0.6);
    opacity: 0;
    transition: opacity 0.3s linear;
    padding: 10px;
    box-sizing: border-box;
  }

  .movie-hover-overlay::after {
    content: "Tickets";
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    background-color: rgba(52, 152, 219, 0.9);
    color: white;
    text-align: center;
    font-size: 1rem;
    font-weight: bold;
    padding: 5px 0;
    box-sizing: border-box;
    opacity: 0;
    transform: translateY(100%);
    transition: opacity 0.3s, transform 0.3s;
  }

  .movie-image-container:hover .movie-hover-overlay::after {
    opacity: 1;
    transform: translateY(0);
  }

  .movie-image-container:hover .movie-hover-overlay {
    opacity: 1;
  }

  .movie-title {
    color: #fff;
    font-size: 1rem;
    font-weight: bold;
    text-align: center;
    white-space: normal; /* Zeilenumbruch erlauben */
    overflow: visible; /* Text vollständig anzeigen */
    line-height: 1.2; /* Abstände zwischen Zeilen */
  }

  .showtime-info {
    color: #fff;
    font-size: 0.9rem;
    margin-top: 5px;
    text-align: center;
    background-color: rgba(0, 0, 0, 0.6);
    padding: 2px 5px;
    border-radius: 4px;
    margin-top: 5px;
  }

  .movie-button {
    background: none;
    border: none;
    padding: 0;
    margin: 0;
    width: 100%;
    text-align: left;
    cursor: pointer;
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
    background: white;
    padding: 20px;
    border-radius: 8px;
    max-width: 400px;
    width: 90%;
    text-align: center;
    position: relative;
  }

  .popup-movie-details img {
    width: 100%;
    border-radius: 8px;
    margin-bottom: 10px;
  }

  .popup-movie-details h2 {
    margin: 10px 0;
    font-size: 1.5rem;
    color: #333;
  }

  .popup-movie-details p {
    margin: 5px 0;
    font-size: 1rem;
    color: #555;
  }

  .close-button {
    position: absolute;
    top: 10px;
    right: 10px;
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: #333;
  }

  .close-button:hover {
    color: red;
  }

  /* Zusätzliche Stile für die Fehleranzeige */
  .error {
    color: red;
    text-align: center;
    font-weight: bold;
    margin-top: 20px;
  }
</style>
