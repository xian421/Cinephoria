<script>
  export let movieDetails = {}; // Movie-Details aus der API
  const IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500";
</script>

<style>
  .movie-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 2rem;
  }

  .movie-header {
    display: flex;
    gap: 2rem;
    align-items: flex-start;
  }

  .movie-poster {
    max-width: 300px;
    border-radius: 10px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
  }

  .movie-details {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .movie-title {
    font-size: 2.5rem;
    font-weight: bold;
    color: #2c3e50;
  }

  .movie-meta {
    color: #7f8c8d;
    font-size: 1.2rem;
  }

  .movie-overview {
    line-height: 1.5;
    font-size: 1rem;
  }

  .movie-extras {
    margin-top: 1.5rem;
  }

  .production-companies {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    margin-top: 1rem;
  }

  .company-logo {
    max-height: 40px;
    border-radius: 5px;
  }

  .schedule {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 1rem;
    margin-top: 2rem;
  }

  .schedule-item {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 1rem;
    border: 1px solid #ddd;
    border-radius: 8px;
    background: #f5f5f5;
    font-weight: bold;
    transition: background 0.3s ease;
  }

  .schedule-item:hover {
    background: #ecf0f1;
  }
</style>

<div class="movie-container">
  <div class="movie-header">
    <img
      class="movie-poster"
      src="{IMAGE_BASE_URL}{movieDetails.poster_path}"
      alt="{movieDetails.title}"
    />
    <div class="movie-details">
      <div class="movie-title">{movieDetails.title}</div>
      <div class="movie-meta">
        Dauer: {movieDetails.runtime} Minuten | FSK: {movieDetails.vote_average} | Genres:{" "}
        {movieDetails.genres.map((genre) => genre.name).join(", ")}
      </div>
      <div class="movie-overview">{movieDetails.overview}</div>
      <div class="movie-extras">
        <div><strong>Veröffentlichung:</strong> {movieDetails.release_date}</div>
        <div><strong>Bewertung:</strong> {movieDetails.vote_average} von {movieDetails.vote_count} Stimmen</div>
        <div>
          <strong>Produktionsfirmen:</strong>
          <div class="production-companies">
            {#each movieDetails.production_companies as company}
              {#if company.logo_path}
                <img
                  class="company-logo"
                  src="{IMAGE_BASE_URL}{company.logo_path}"
                  alt="{company.name}"
                  title="{company.name}"
                />
              {:else}
                <span>{company.name}</span>
              {/if}
            {/each}
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="schedule">
    {#each ["14:45", "15:10", "17:25", "17:50", "20:00", "20:25"] as time}
      <div class="schedule-item">{time}</div>
    {/each}
  </div>
</div>
