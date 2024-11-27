<script>
  import { onMount } from 'svelte';
  import { navigate } from 'svelte-routing';

  let nowPlayingMovies = [];
  let groupedMovies = {};

  const daysOfWeekMap = {
    0: "Sonntag",
    1: "Montag",
    2: "Dienstag",
    3: "Mittwoch",
    4: "Donnerstag",
    5: "Freitag",
    6: "Samstag",
  };

  const API_URL = 'https://cinephoria-backend-c53f94f0a255.herokuapp.com/movies/now_playing';
  const IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500';

  function formatDate(dateString) {
    const date = new Date(dateString);
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}.${month}.${year}`;
  }

  function loadMovies(data) {
    const savedMovies = JSON.parse(localStorage.getItem('moviesWithDates'));
    if (savedMovies && savedMovies.length === data.length) {
      return savedMovies;
    } else {
      const updatedMovies = data.map(movie => {
        const randomOffset = Math.floor(Math.random() * 7);
        const date = new Date();
        date.setDate(date.getDate() + randomOffset);
        return {
          ...movie,
          showDate: date.toISOString().split('T')[0],
        };
      });
      localStorage.setItem('moviesWithDates', JSON.stringify(updatedMovies));
      return updatedMovies;
    }
  }

  function groupMoviesByDate(movies) {
    return movies.reduce((acc, movie) => {
      const date = movie.showDate;
      if (!acc[date]) {
        acc[date] = [];
      }
      acc[date].push(movie);
      return acc;
    }, {});
  }

  onMount(async () => {
    try {
      const response = await fetch(API_URL);
      const data = await response.json();
      nowPlayingMovies = loadMovies(data.results);
      groupedMovies = groupMoviesByDate(nowPlayingMovies);
    } catch (error) {
      console.error('Fehler beim Laden der Filme:', error);
    }
  });

  function navigateToDescription(movie) {
    console.log('Navigiere zu Beschreibung mit ID:', movie.id);
    navigate(`/beschreibung/${movie.id}`);
  }
</script>


<main>
  <h1>Aktuelles Kinoprogramm im CINEPHORIA</h1>

  {#each Object.keys(groupedMovies).sort((a, b) => new Date(a) - new Date(b)) as dateKey}
    <section>
      <div class="day-header">
        <h2>
          {daysOfWeekMap[new Date(dateKey).getDay()] || "Unbekannter Tag"}, {formatDate(dateKey)}
        </h2>
      </div>
      <div class="movies-container">
        {#each groupedMovies[dateKey] as movie}
          <article class="movie-card">
            <button
              class="movie-button"
              on:click={() => navigateToDescription(movie)}
              aria-label="Details zu {movie.title} anzeigen"
            >
              <img src="{IMAGE_BASE_URL}{movie.poster_path}" alt="{movie.title}" />
              <div class="movie-details">
                <h3>{movie.title}</h3>
              </div>
            </button>
          </article>
        {/each}
      </div>
    </section>
  {/each}
</main>


<style>
  :global(body) {
    margin: 0;
    font-family: Arial, sans-serif;
    background-color: #eeeded;
  }

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
    overflow-y: hidden; /* Vertikales Scrollen deaktivieren */
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
    flex: 0 0 250px; /* Kleinere Breite für Filme */
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    cursor: pointer;
  }

  .movie-card:hover {
    transform: scale(0.95);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
  }

  .movie-card img {
    width: 100%; /* Breite auf die Kartenbreite beschränkt */
    height: 225px; /* Feste Höhe für einheitliche Darstellung */
    object-fit: cover; /* Verhältnis beibehalten */
    display: block;
  }

  .movie-details {
    padding: 8px;
    text-align: center;
  }

  .movie-details h3 {
    font-size: 0.9rem; /* Kleinere Schriftgröße */
    margin: 0;
    color: #444;
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
</style>
