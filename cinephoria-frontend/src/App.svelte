<script>
  let movies = [];

  async function fetchMovies() {
      const response = await fetch('https://cinephoria-backend-c53f94f0a255.herokuapp.com/movies');
      movies = await response.json();
  }

  fetchMovies();
</script>

<style>
  ul {
      list-style: none;
      padding: 0;
  }

  li {
      margin: 10px 0;
  }
</style>

<h1>Filmliste</h1>
<ul>
  {#each movies as movie}
      <li>{movie.title}</li>
  {/each}
</ul>
