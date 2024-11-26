<script>
    import { onMount } from 'svelte';
    export let params; // Zugriff auf die Routen-Parameter (z. B. ID des Films)
    let movie = null;
  
    onMount(async () => {
      const response = await fetch(
        `https://cinephoria-backend-c53f94f0a255.herokuapp.com/movies/${params.id}`
      );
      movie = await response.json(); // Film-Daten aus Backend laden
    });
  </script>
  
  {#if movie}
    <div class="movie-details">
      <h1>{movie.title}</h1>
      <p>{movie.overview}</p>
      <p><strong>Release-Datum:</strong> {movie.release_date}</p>
      <p><strong>Beliebtheit:</strong> {movie.popularity}</p>
      <p><strong>Bewertung:</strong> {movie.vote_average} / 10 ({movie.vote_count} Stimmen)</p>
    </div>
  {:else}
    <p>Loading...</p>
  {/if}
  
  <style>
    .movie-details {
      max-width: 800px;
      margin: 20px auto;
      padding: 20px;
      border: 1px solid #ccc;
      border-radius: 8px;
      background-color: #f9f9f9;
    }
  
    .movie-details h1 {
      font-size: 2rem;
      color: #333;
    }
  
    .movie-details p {
      font-size: 1rem;
      color: #555;
      margin: 8px 0;
    }
  </style>
  