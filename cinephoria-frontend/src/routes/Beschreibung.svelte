<script>
    import { onMount, getContext } from 'svelte';

    // Zugriff auf die Routenparameter
    const { params } = getContext('svelte-routing'); // Hinzugefügt
    const IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500';
    let movieId = params.id;
    let movieDetails = {};

    // Beim Mounten der Komponente die Filmdetails abrufen
    onMount(async () => {
      try {
        const response = await fetch(
          `https://cinephoria-backend-c53f94f0a255.herokuapp.com/movies/${movieId}`
        );
        movieDetails = await response.json();
      } catch (error) {
        console.error('Fehler beim Laden der Filmdetails:', error);
      }
    });
</script>

{#if movieDetails.title}
  <main>
    <h1>{movieDetails.title}</h1>
    <img src="{IMAGE_BASE_URL}{movieDetails.poster_path}" alt="{movieDetails.title}" />
    <p>{movieDetails.overview}</p>
    <!-- Weitere Details anzeigen -->
  </main>
{:else}
  <p>Lade Filmdetails...</p>
{/if}
