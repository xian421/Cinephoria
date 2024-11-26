<script>
    import { onMount } from 'svelte';
  
    let nowPlayingMovies = [];
  
    onMount(async () => {
      const response = await fetch('https://cinephoria-backend-c53f94f0a255.herokuapp.com/movies/now_playing');
      nowPlayingMovies = (await response.json()).results;
    });
  </script>
  
  <h1>Now Playing</h1>
  <div class="movies">
    {#each nowPlayingMovies as movie}
      <div class="movie-card">
        <img src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`} alt={movie.title} />
        <h2>{movie.title}</h2>
        <p>{movie.overview}</p>
      </div>
    {/each}
  </div>
  
  <style>
    .movies {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 16px;
    }
    .movie-card {
      padding: 16px;
      border: 1px solid #ccc;
      border-radius: 8px;
      text-align: center;
    }
    .movie-card img {
      width: 100%;
      border-radius: 8px;
    }
  </style>
   