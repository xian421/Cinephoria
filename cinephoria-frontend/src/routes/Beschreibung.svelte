<script>
  export let id; // ID wird von der Route übergeben
  import { onMount } from 'svelte';
  import "@fortawesome/fontawesome-free/css/all.min.css";


  let movieDetails = {};
  const IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500';
  let isLoading = true;
  let error = null;

  onMount(async () => {
    if (!id) {
      console.error('Keine ID gefunden!');
      error = 'Keine ID gefunden!';
      isLoading = false;
      return;
    }
    try {
      const response = await fetch(
        `https://cinephoria-backend-c53f94f0a255.herokuapp.com/movies/${id}`
      );
      if (response.ok) {
        movieDetails = await response.json();
        
        const responsefsk = await fetch (
        `https://cinephoria-backend-c53f94f0a255.herokuapp.com/movie/${id}/release_dates`
        );
        if (responsefsk.ok){
          moviefsk = await responsefsk.json();
        } else {
          console.error('Fehler beim Laden der Filmdetails:', response.statusText);
          error = 'Fehler beim Laden der Filmdetails.';
        }
      }
    } catch (err) {
      console.error('Netzwerkfehler:', err);
      error = 'Netzwerkfehler. Bitte versuche es erneut.';
    } finally {
      isLoading = false;
    }
  });
</script>

<style>
  .movie-container {
    display: flex;
    gap: 2rem;
    padding: 2rem;
    font-family: Arial, sans-serif;
  }

  .poster {
    max-width: 300px;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  }

  .details {
    flex: 1;
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
  }

  .description {
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

  .error {
    color: red;
    font-size: 1.2rem;
    margin: 2rem;
  }

  .meta i {
  font-size: 20px; /* Größe des Icons */
  color: #555; /* Farbe des Icons */
  margin-right: 5px; /* Abstand zwischen Icon und Text */
  vertical-align: middle; /* Mittige Ausrichtung mit dem Text */
}

</style>

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
      />
    </div>

    <!-- Rechte Spalte: Details -->
    <div class="details">
      <div class="title">{movieDetails.title}</div>
      <div class="tagline">{movieDetails.tagline}</div>
      <div class="meta">
        <i class="fas fa-clock"></i> {movieDetails.runtime} '
        <span>FSK: {moviesfsk.certification}</span> | 
        <span>Genre: {movieDetails.genres ? movieDetails.genres.map((genre) => genre.name).join(", ") : 'Keine Angaben'}</span>
      </div>
      
      <div class="description">{movieDetails.overview}</div>

      <!-- Produktionsfirmen -->
      <div>
        <h3>Produktionsfirmen:</h3>
        <ul>
          {#each movieDetails.production_companies as company}
            <li>{company.name}</li>
          {/each}
        </ul>
      </div>

      <!-- Erscheinungsdatum -->
      <div>
        <h3>Veröffentlichung:</h3>
        <p>{movieDetails.release_date}</p>
      </div>

      <!-- Bewertungen -->
      <div>
        <h3>Bewertung:</h3>
        <p>
          <span class="highlight">{movieDetails.vote_average.toFixed(1)}</span> 
          von {movieDetails.vote_count} Stimmen
        </p>
      </div>
    </div>
  </div>
{:else}
  <p>Filmdetails konnten nicht geladen werden.</p>
{/if}
