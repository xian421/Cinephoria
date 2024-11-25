<script>
  import { onMount } from 'svelte';

  let movies = [];
  let error = null;

  onMount(async () => {
    try {
      const response = await fetch('https://cinephoria-backend-c53f94f0a255.herokuapp.com/movies');
      if (!response.ok) {
        throw new Error('Failed to fetch movies');
      }
      movies = await response.json();
    } catch (err) {
      error = err.message;
    }
  });
</script>

<style>
  .movies-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    padding: 1rem;
  }

  .movie-card {
    border: 1px solid #ccc;
    border-radius: 8px;
    padding: 1rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    text-align: center;
    background: #f9f9f9;
  }

  .movie-title {
    font-size: 1.2rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
    color: #333;
  }

  .release-date {
    color: #777;
    font-size: 0.9rem;
  }

  .error-message {
    color: red;
    text-align: center;
    margin-top: 2rem;
  }
</style>

<h1>🎥 Aktuelle Filme</h1>

{#if error}
  <p class="error-message">{error}</p>
{:else if movies.length === 0}
  <p class="error-message">Keine Filme verfügbar. Bitte später erneut versuchen.</p>
{:else}
  <div class="movies-container">
    {#each movies as movie}
      <div class="movie-card">
        <div class="movie-title">{movie.title}</div>
        <div class="release-date">📅 {movie.release_date}</div>
      </div>
    {/each}
  </div>
{/if}
