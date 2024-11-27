<script>
  export let id; // ID wird von der Route übergeben
  console.log('Geladene ID:', id); // Debugging

  import { onMount } from 'svelte';
  let movieDetails = {};
  const IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500';

  onMount(async () => {
    if (!id) {
      console.error('Keine ID gefunden!');
      return;
    }
    try {
      const response = await fetch(
        `https://cinephoria-backend-c53f94f0a255.herokuapp.com/movies/${id}`
      );
      if (response.ok) {
        movieDetails = await response.json();
      } else {
        console.error('Fehler beim Laden der Filmdetails:', response.statusText);
      }
    } catch (error) {
      console.error('Netzwerkfehler:', error);
    }
  });
</script>

{#if movieDetails.title}
  <main>
    <h1>{movieDetails.title}</h1>
    <img src="{IMAGE_BASE_URL}{movieDetails.poster_path}" alt="{movieDetails.title}" />
    <p>{movieDetails.overview}</p>
  </main>
{:else}
  <p>Lade Filmdetails...</p>
{/if}
