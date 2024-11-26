<script>
  import { onMount } from 'svelte';
  import { Link } from 'svelte-routing'; // Import für Navigation

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
    <div class="movie-card">
      <!-- Modal für schnelle Details -->
      <div on:click={() => openModal(movie)}>
        <img src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`} alt={movie.title} />
        <div class="movie-details">
          <h2>{movie.title}</h2>
        </div>
      </div>

      <!-- Link zur separaten Detailseite -->
      <Link to={`/beschreibung/${movie.id}`} class="details-link">Zur Detailseite</Link>
    </div>
  {/each}
</div>

{#if selectedMovie}
  <div class="modal" on:click={closeModal}>
    <div class="modal-content" on:click|stopPropagation>
      <button class="close" on:click={closeModal}>&times;</button>
      <div class="modal-header">
        <img
          class="poster"
          src={`https://image.tmdb.org/t/p/w500${selectedMovie.poster_path}`}
          alt={selectedMovie.title}
        />
        <div class="info">
          <h2>{selectedMovie.title}</h2>
          <p><strong>Originaltitel:</strong> {selectedMovie.original_title}</p>
          <p><strong>Sprache:</strong> {selectedMovie.original_language.toUpperCase()}</p>
          <p><strong>Release-Datum:</strong> {selectedMovie.release_date}</p>
          <p><strong>Beliebtheit:</strong> {selectedMovie.popularity}</p>
          <p><strong>Bewertung:</strong> {selectedMovie.vote_average} / 10 ({selectedMovie.vote_count} Stimmen)</p>
        </div>
      </div>
      <div class="modal-body">
        <p>{selectedMovie.overview}</p>
      </div>
    </div>
  </div>
{/if}

<style>
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
    text-align: center;
    cursor: pointer;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }

  .movie-card:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
  }

  .movie-card img {
    width: 100%;
    height: auto;
  }

  .details-link {
    display: block;
    margin-top: 8px;
    font-size: 0.9rem;
    color: #007bff;
    text-decoration: none;
    font-weight: bold;
  }

  .details-link:hover {
    text-decoration: underline;
  }

  /* Modal-Styles bleiben unverändert */
</style>

<footer>
  <div class="footer-links">
    <a href="/impressum">Impressum</a>
    <a href="/datenschutz">Datenschutzerklärung</a>
    <a href="/kontakt">Kontakt</a>
  </div>
  <p>© {currentYear} Cinephoria. Alle Rechte vorbehalten.</p>
</footer>
