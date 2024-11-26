<script>
    export let movie = {};
  </script>
  
  <h1>{movie.title}</h1>
  <p>{movie.overview}</p>
  <p><strong>Release-Datum:</strong> {movie.release_date}</p>
  <p><strong>Beliebtheit:</strong> {movie.popularity}</p>
  
  <style>
    h1 {
      font-size: 2rem;
      color: #333;
    }
    p {
      font-size: 1rem;
      color: #555;
    }
  </style>
  