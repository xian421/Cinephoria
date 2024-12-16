<!-- src/routes/Beschreibung.svelte -->
<!-- src/routes/Beschreibung.svelte -->
<script>
  import { onMount } from 'svelte';
  import { navigate } from 'svelte-routing';
  import Swal from 'sweetalert2';
  import { fetchMovieDetails, fetchMovieFSK, fetchShowtimesByMovie, fetchScreens, fetchMovieTrailerUrl } from '../services/api.js';
  import { get } from 'svelte/store';
  import { authStore } from '../stores/authStore'; 
  import "@fortawesome/fontawesome-free/css/all.min.css";

  export let id; // ID wird von der Route übergeben

  let moviefsk = {};  
  let movieDetails = {};
  let showtimes = [];
  let screens = {}; // Map von screen_id zu screen_details
  const IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500';
  let isLoading = true;
  let error = null;

  // Variablen für das Showtime Popup
  let isOpen = false;
  let selectedShowtime = null;
  let movie_certification = "";

  // Neue Variablen für das Trailer Popup
  let isTrailerOpen = false;
  let trailerUrl = ''; // Wird dynamisch gesetzt

  onMount(async () => {
    if (!id) {
      console.error('Keine ID gefunden!');
      error = 'Keine ID gefunden!';
      isLoading = false;
      return;
    }
    try {
      // Abrufen der Filmdetails und FSK gleichzeitig
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

      // Erstelle eine Map von screen_id zu screen_details für einfaches Nachschlagen
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
    }
  });

  // Funktion zur Navigation zur Buchungsseite oder weiteren Details
  function navigateToBooking(showtime) {
    console.log('Navigiere zu Buchung mit Showtime ID:', showtime.showtime_id);
    navigate(`/buchung/${showtime.showtime_id}`);
  }

  // Funktion zum Öffnen des Showtimes Popups
  function openShowtimePopup(showtime) {
    selectedShowtime = showtime;
    isOpen = true;
  }

  // Funktion zum Schließen des Showtimes Popups
  function closeShowtimePopup() {
    isOpen = false;
    selectedShowtime = null;
  }

  // Funktion zum Öffnen des Trailer Popups
  async function openTrailerModal() {
    isTrailerOpen = true;
    try {
      const token = get(authStore).token; // Falls dein Backend Authentifizierung benötigt
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

  // Funktion zum Schließen des Trailer Popups
  function closeTrailerModal() {
    isTrailerOpen = false;
    trailerUrl = '';
  }
</script>

<style>
  .movie-container {
    display: flex;
    gap: 2rem;
    padding: 2rem;
    font-family: Arial, sans-serif;
    flex-wrap: wrap;
  }

  .poster {
    max-width: 300px;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    cursor: pointer; /* Cursor als Pointer anzeigen */
  }

  .details {
    flex: 2;
    min-width: 300px;
  }

  .title {
    font-size: 2rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
  }

  .tagline {
    font-style: italic;
    color: #888;
    margin-bottom: 1rem;
  }

  .meta {
    margin-bottom: 1.5rem;
    color: #555;
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    align-items: center;
  }

  .meta i {
    font-size: 20px; /* Größe des Icons */
    color: #555; /* Farbe des Icons */
    margin-right: 2px; /* Abstand zwischen Icon und Text */
    vertical-align: middle; /* Mittige Ausrichtung mit dem Text */
  }

  .description {
    margin-bottom: 2rem;
    line-height: 1.6;
  }

  .highlight {
    font-weight: bold;
    color: red;
  }

  .error {
    color: red;
    font-size: 1.2rem;
    margin: 2rem;
    text-align: center;
  }

  /* Neue Klasse für Showtimes */
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
    background-color: #7acde1;
    border-radius: 8px;
    padding: 0.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .showtime-box:hover {
    transform: translateY(-5px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  }

  .showtime-date {
    color: black;
    font-weight: bold;
    font-size: 0.9rem;
  }

  .showtime-time {
    color: #1321bc;
    font-weight: bold;
    font-size: 1.6rem;
  }

  .showtime-screen {
    color: #555;
    font-size: 0.7rem;
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
    background: white;
    padding: 20px;
    border-radius: 8px;
    max-width: 950px;
    height: 600px;
    width: 90%;
    text-align: center;
    position: relative;
  }

  .popup-showtime-details h2 {
    margin-bottom: 1rem;
    font-size: 1.5rem;
    color: #333;
  }

  .popup-showtime-details p {
    margin: 0.5rem 0;
    font-size: 1rem;
    color: #555;
  }

  .book-button {
    margin-top: 1rem;
    padding: 0.5rem 1rem;
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  .book-button:hover {
    background-color: #2980b9;
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

  /* Zusätzliche Stile für das Trailer Modal */
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

  /* Responsive Anpassungen */
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

<!-- Popup für Showtimes -->
{#if isOpen && selectedShowtime}
  <div class="popup-overlay" on:click={closeShowtimePopup}>
    <div class="popup-content" on:click|stopPropagation>
      <button class="close-button" on:click={closeShowtimePopup}>×</button>
      <div class="popup-showtime-details">
        <h2>Showtime Details</h2>
        <p><strong>Datum:</strong> {new Date(selectedShowtime.start_time).toLocaleDateString()}</p>
        <p><strong>Startzeit:</strong> {new Date(selectedShowtime.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
        {#if selectedShowtime.end_time}
          <p><strong>Endzeit:</strong> {new Date(selectedShowtime.end_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
        {/if}
        <p><strong>Kinosaal:</strong> {screens[selectedShowtime.screen_id]?.name || 'Unbekannt'}</p>
        <button on:click={() => navigateToBooking(selectedShowtime)} class="book-button">Tickets buchen</button>
      </div>
    </div>
  </div>
{/if}

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
    <p>Lade Filmdetails...</p>
  {:else if error}
    <p class="error">{error}</p>
  {:else if movieDetails.title}
    <div class="movie-container">
      <!-- Linke Spalte: Poster -->
      <div>
        <img
          src="{IMAGE_BASE_URL}{movieDetails.poster_path}"
          alt="{movieDetails.title}"
          class="poster"
          on:click={openTrailerModal}
        />
      </div>

      <!-- Mittlere Spalte: Details -->
      <div class="details">
        <div class="title">{movieDetails.title}</div>
        <div class="tagline">{movieDetails.tagline}</div>
        <div class="meta" style="gap: 0px;">
          <i class="fas fa-clock"></i> {movieDetails.runtime}'    
          <span style="margin-left: 5px;"> FSK:{movie_certification}</span> 
          <span style="margin-left: 5px;">Genre: {movieDetails.genres ? movieDetails.genres.map((genre) => genre.name).join(", ") : 'Keine Angaben'}</span>
        </div>
        
        <div class="description">{movieDetails.overview}</div>
  <!--
         Produktionsfirmen
        <div>
          <h3>Produktionsfirmen:</h3>
          <ul>
            {#each movieDetails.production_companies as company}
              <li>{company.name}</li>
            {/each}
          </ul>
        </div>

        <div>
          <h3>Veröffentlichung:</h3>
          <p>{movieDetails.release_date}</p>
        </div>

        <div>
          <h3>Bewertung:</h3>
          <p>
            <span class="highlight">{movieDetails.vote_average.toFixed(1)}</span> 
            von {movieDetails.vote_count} Stimmen
          </p>
        </div>-->
      </div> 

      <!-- Rechte Spalte: Showtimes -->
      <div class="showtimes">
        {#if showtimes.length > 0}
          <div class="showtimes-container">
            {#each showtimes as showtime}
              <div class="showtime-box" on:click={() => openShowtimePopup(showtime)}>
                <div class="showtime-date">
                  {new Date(showtime.start_time).toLocaleDateString()}
                </div>
                <div class="showtime-time">
                  {new Date(showtime.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}Uhr
                </div>
                <div class="showtime-screen">
                  {screens[showtime.screen_id]?.name || 'Unbekannt'}
                </div>
              </div>
            {/each}
            <div style="display: inline-block; padding: 10px; background-color: #65797e; color: white; clip-path: polygon(0 0, 90% 0, 100% 50%, 90% 100%, 0 100%); font-family: Arial, sans-serif; font-size: 16px; text-align: center;">
              <div style="font-size: 24px; font-weight: bold;">+13(stimmt net)</div>
              <div style="font-size: 14px;">weitere<br>Vorstellungen</div>
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