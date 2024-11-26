<script>
  import { onMount } from 'svelte';

  let nowPlayingMovies = [];
  let upcomingMovies = [];

  onMount(async () => {
    // Aktuelle Filme laden
    const nowPlayingResponse = await fetch('https://cinephoria-backend-c53f94f0a255.herokuapp.com/movies/now_playing');
    nowPlayingMovies = (await nowPlayingResponse.json()).results;

    // Kommende Filme laden
    const upcomingResponse = await fetch('https://cinephoria-backend-c53f94f0a255.herokuapp.com/movies/upcoming');
    upcomingMovies = (await upcomingResponse.json()).results;
  });
</script>

<h1>Jetzt im Kino</h1>
<div class="movies">
  {#each nowPlayingMovies as movie}
    <div class="movie-card">
      <img src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`} alt={movie.title} />
      <h2>{movie.title}</h2>
      <p>{movie.overview}</p>
      <p><strong>Bewertung:</strong> {movie.vote_average} / 10</p>
      <p><strong>Release:</strong> {movie.release_date}</p>
    </div>
  {/each}
</div>

<h1>Kommende Filme</h1>
<div class="movies">
  {#each upcomingMovies as movie}
    <div class="movie-card">
      <img src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`} alt={movie.title} />
      <h2>{movie.title}</h2>
      <p>{movie.overview}</p>
      <p><strong>Bewertung:</strong> {movie.vote_average} / 10</p>
      <p><strong>Release:</strong> {movie.release_date}</p>
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
    border: 1px solid #ccc;
    border-radius: 8px;
    padding: 16px;
    text-align: center;
  }
  .movie-card img {
    width: 100%;
    border-radius: 8px;
  }
</style>
