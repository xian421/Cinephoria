<script>
  import { onMount } from 'svelte';

  let nowPlayingMovies = [];
  let selectedMovie = null;

  onMount(async () => {
    const response = await fetch(
      'https://cinephoria-backend-c53f94f0a255.herokuapp.com/movies/now_playing'
    );
    nowPlayingMovies = (await response.json()).results;
  });

  function openModal(movie) {
    selectedMovie = movie;
  }

  function closeModal() {
    selectedMovie = null;
  }

  const currentYear = new Date().getFullYear();
</script>



<h1>Aktuelles Kinoprogramm im CINEPHORIA</h1>

<div class="movies">
  {#each nowPlayingMovies as movie}
    <div class="movie-card" on:click={() => openModal(movie)}>
      <img src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`} alt={movie.title} />
      <div class="movie-details">
        <h2>{movie.title}</h2>
      </div>
    </div>
  {/each}
</div>

{#if selectedMovie}
  <div class="modal" on:click={closeModal}>
    <div class="modal-content" on:click|stopPropagation>
      <button class="close" on:click={closeModal}>&times;</button>
      <div class="modal-header">
        <!-- Poster-Bild -->
        <img
          class="poster"
          src={`https://image.tmdb.org/t/p/w500${selectedMovie.poster_path}`}
          alt={selectedMovie.title}
        />
        <!-- Film-Details -->
        <div class="info">
          <h2>{selectedMovie.title}</h2>
          <p><strong>Originaltitel:</strong> {selectedMovie.original_title}</p>
          <p><strong>Sprache:</strong> {selectedMovie.original_language.toUpperCase()}</p>
          <p><strong>Release-Datum:</strong> {selectedMovie.release_date}</p>
          <p><strong>Beliebtheit:</strong> {selectedMovie.popularity}</p>
          <p><strong>Bewertung:</strong> {selectedMovie.vote_average} / 10 ({selectedMovie.vote_count} Stimmen)</p>
          <!-- Neuer Button -->
          <button class="more-info">Weitere Informationen</button>
        </div>
      </div>
      <div class="modal-body">
        <p>{selectedMovie.overview}</p>
      </div>
    </div>
  </div>
{/if}


<style>
  /* Allgemeine Styles */
  body {
    margin: 0;
    font-family: Arial, sans-serif;
    background-color: #f8f8f8;
  }

  header {
    width: 100%;
    padding: 10px;
    background-color: #333;
    color: white;
    text-align: center;
    font-size: 1.5rem;
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
    cursor: pointer;
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

  /* Modal */
  .modal {
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

  .modal-content {
    background: white;
    padding: 20px;
    border-radius: 8px;
    width: 90%;
    max-width: 800px; /* Breiteres Modal */
    max-height: 90%;
    overflow-y: auto;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  }

  .modal-header {
    display: flex;
    gap: 20px;
    align-items: center;
  }

  .poster {
    width: 30%; /* Verkleinertes Bild */
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  }

  .info {
    flex-grow: 1;
    text-align: left;
  }

  .modal-body {
    margin-top: 20px;
    color: #555;
  }

  .modal-body p {
    font-size: 1rem;
  }

  .close {
    position: absolute;
    top: 10px;
    right: 10px;
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: #333;
  }

  .close:hover {
    color: #ff0000;

    footer {
      background-color: #333;
      color: white;
      text-align: center;
      padding: 1.5rem 1rem;
      font-size: 0.9rem;
    }

    footer a {
      color: #4CAF50;
      text-decoration: none;
      margin: 0 0.5rem;
    }

    footer a:hover {
      text-decoration: underline;
    }

    .footer-links {
      margin-bottom: 1rem;
    }

    .footer-links a {
      display: inline-block;
      margin: 0 1rem;
    }
  }
</style>

<footer>
  <div class="footer-links">
    <a href="/impressum">Impressum</a>
    <a href="/datenschutz">Datenschutzerklärung</a>
    <a href="/kontakt">Kontakt</a>
  </div>
  <p>© {currentYear} Cinephoria. Alle Rechte vorbehalten.</p>
</footer>
