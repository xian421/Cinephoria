<!-- <script>
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
</style> -->

<script>
  import { wrap } from 'svelte-spa-router/wrap';
  import Router from 'svelte-spa-router';

  // Seiten importieren
  import Home from './routes/Home.svelte';
  import NowPlaying from './routes/NowPlaying1.svelte';
  import Upcoming from './routes/Upcoming1.svelte';
  import NotFound from './routes/NotFound1.svelte';

  // Routen definieren  
  const routes = {
    '/': Home,
    '/now-playing': NowPlaying,
    '/upcoming': Upcoming,
    '*': NotFound, // Wildcard für 404-Seiten
  };
</script>

<nav>
  <a href="/">Home</a>
  <a href="/now-playing">Now Playing</a>
  <a href="/upcoming">Upcoming</a>
</nav>

<main>
  <Router {routes} />
</main>

<style>
  nav {
    display: flex;
    gap: 16px;
    padding: 16px;
    background: #333;
  }
  nav a {
    color: white;
    text-decoration: none;
    font-weight: bold;
  }
  nav a:hover {
    text-decoration: underline;
  }
  main {
    padding: 16px;
  }
</style>
