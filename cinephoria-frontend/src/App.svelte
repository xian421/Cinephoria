<script>
  import { onMount } from 'svelte';

  let movies = [];

  onMount(async () => {
    const response = await fetch('https://cinephoria-backend-c53f94f0a255.herokuapp.com/movies');
    movies = await response.json();
  });
</script>

<h1>Aktuelle Filme</h1>
<ul>
  {#each movies as movie}
    <li>{movie.title} - {movie.release_date}</li>
  {/each}
</ul>
