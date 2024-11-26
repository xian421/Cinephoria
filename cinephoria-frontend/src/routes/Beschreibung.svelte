<script>
    export let params;
    let movie = null;
  
    onMount(async () => {
      const response = await fetch(
        `https://cinephoria-backend-c53f94f0a255.herokuapp.com/movies/${params.id}`
      );
      movie = await response.json();
    });
  </script>
  
  {#if movie}
    <h1>{movie.title}</h1>
    <p>{movie.overview}</p>
  {:else}
    <p>Loading...</p>
  {/if}
  