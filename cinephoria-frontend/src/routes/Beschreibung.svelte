<!-- <script>
  export let id; // ID wird von der Route übergeben
  console.log('Geladene ID:', id); // Debugging

  import { onMount } from 'svelte';
  let movieDetails = {};
  const IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500';

  onMount(async () => {
    if (!id) {
      console.error('Keine ID gefunden!');
      return;
    }
    try {
      const response = await fetch(
        `https://cinephoria-backend-c53f94f0a255.herokuapp.com/movies/${id}`
      );
      if (response.ok) {
        movieDetails = await response.json();
      } else {
        console.error('Fehler beim Laden der Filmdetails:', response.statusText);
      }
    } catch (error) {
      console.error('Netzwerkfehler:', error);
    }
  });
</script>

{#if movieDetails.title}
  <main>
    <h1>{movieDetails.title}</h1>
    <img src="{IMAGE_BASE_URL}{movieDetails.poster_path}" alt="{movieDetails.title}" />
    <p>{movieDetails.overview}</p>
  </main>
{:else}
  <p>Lade Filmdetails...</p>
{/if} -->


<script>
 // export let film = {}; // Film-Daten, die von der Route übergeben werden

  const film = {
  poster: "https://link-zu-deinem-poster.jpg",
  title: "Vaiana 2",
  runtime: 100,
  rating: "0",
  genre: "Animation",
  description:
    "Vaiana 2 enthält Sequenzen mit Blitzlicht, die sich auf photosensitive Menschen oder Menschen mit photosensitiver Epilepsie auswirken könnten.",
  showtimes: ["14:45", "15:10", "17:25", "17:50", "20:00", "20:25"],
};

</script>

<style>
  .film-container {
    display: flex;
    gap: 2rem;
    padding: 2rem;
  }

  .film-poster {
    max-width: 300px;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  }

  .film-details {
    flex: 1;
  }

  .film-title {
    font-size: 2rem;
    font-weight: bold;
    margin-bottom: 1rem;
  }

  .film-meta {
    margin-bottom: 1.5rem;
    color: #555;
  }

  .film-description {
    margin-bottom: 2rem;
    line-height: 1.6;
  }

  .schedule {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 1rem;
  }

  .schedule-button {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 0.8rem;
    border-radius: 8px;
    background: #f0f0f0;
    font-size: 1rem;
    font-weight: bold;
    cursor: pointer;
    transition: background 0.3s ease;
  }

  .schedule-button:hover {
    background: #d4d4d4;
  }

  .highlight {
    font-weight: bold;
    color: red;
  }
</style>

<div class="film-container">
  <!-- Linke Spalte: Poster -->
  <div>
    <img src="{film.poster}" alt="{film.title}" class="film-poster" />
  </div>

  <!-- Rechte Spalte: Details -->
  <div class="film-details">
    <div class="film-title">{film.title}</div>
    <div class="film-meta">
      <span>Dauer: {film.runtime} Minuten</span> | <span>FSK: {film.rating}</span> | <span>Genre: {film.genre}</span>
    </div>
    <div class="film-description">
      {film.description}
    </div>

    <!-- Zeitplan -->
    <div class="schedule">
      {#each film.showtimes as time}
        <div class="schedule-button">{time}</div>
      {/each}
    </div>
  </div>
</div>
