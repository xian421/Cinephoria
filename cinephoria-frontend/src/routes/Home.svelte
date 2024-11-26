<script>
  import { onMount } from 'svelte';

  let nowPlayingMovies = [];

  onMount(async () => {
      const response = await fetch('https://cinephoria-backend-c53f94f0a255.herokuapp.com/movies/now_playing');
      nowPlayingMovies = (await response.json()).results;
  });
</script>
<header>
  Cinephoria. Das ist ein Header
</header>



<h1>Aktuelles Kinoprogramm im CINEPHORIA</h1>
<div class="movies">
  {#each nowPlayingMovies as movie}
      <div class="movie-card">
          <img src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`} alt={movie.title} />
          <div class="movie-details">
              <h2>{movie.title}</h2>
              <p>{movie.overview}</p>
          </div>
      </div>
  {/each}
</div>

<style>
  body {
      margin: 0;
      font-family: Arial, sans-serif;
      background-color: #f8f8f8;
  }

  h1 {
      text-align: center;
      margin: 20px 0;
      font-size: 2rem;
      color: #333;
  }

  .movies {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 16px;
      padding: 20px;
      max-width: 1200px;
      margin: 0 auto;
  }

  .movie-card {
      background-color: #fff;
      border-radius: 8px;
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
      overflow: hidden;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
  }

  .movie-card:hover {
      transform: scale(1.05);
      box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
  }

  .movie-card img {
      width: 100%;
      height: auto;
      display: block;
  }

  .movie-details {
      padding: 16px;
      text-align: center;
  }

  .movie-details h2 {
      font-size: 1.2rem;
      margin-bottom: 8px;
      color: #444;
  }

  .movie-details p {
      font-size: 0.9rem;
      color: #666;
      display: none; /* Optional: Verstecken, wenn Übersicht nicht benötigt wird */
  }

  header {
    width: 100%;
    padding: 10px;
    background-color: #333;
    color: white;
    text-align: center;
    font-size: 1.5rem;
    font-family: Arial, sans-serif;
  }
</style>
