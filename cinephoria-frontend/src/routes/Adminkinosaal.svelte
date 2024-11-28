<script>
    import { onMount } from "svelte";
  
    let screens = [];
  
    onMount(async () => {
      try {
        const response = await fetch("https://cinephoria-backend-c53f94f0a255.herokuapp.com/screens");
        const data = await response.json();
        screens = data.screens;
      } catch (error) {
        console.error("Fehler beim Laden der Kinosäle:", error);
      }
    });
  </script>
  
  <div class="admin-page">
    {#each screens as screen}
      <div class="card">
        <div class="image-container">
            <img src="/cinema-hall.webp" alt="Kinosaal" />
          </div>          
        <div class="card-overlay">
          <div class="card-info">
            <h3>{screen.name}</h3>
            <p>Kapazität: {screen.capacity}</p>
            <p>Typ: {screen.type || "Standard"}</p>
            <p>Erstellt: {new Date(screen.created_at).toLocaleDateString()}</p>
          </div>
        </div>
      </div>
    {/each}
  </div>
  

<style>
  .admin-page {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); /* Responsive Grid */
    gap: 20px;
    padding: 20px;
  }
  
  .card {
    position: relative;
    background: #333; /* Fallback-Farbe */
    border-radius: 12px;
    overflow: hidden;
    color: white;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  }
  
  .card img {
    width: 100%;
    height: 200px;
    object-fit: cover;
  }
  
  .card-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5); /* Halbtransparentes Overlay */
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 20px;
    opacity: 0;
    transition: opacity 0.3s ease-in-out;
  }
  
  .card:hover .card-overlay {
    opacity: 1;
  }
  
  .card-info {
    text-align: center;
  }
  
  .card-info h3 {
    margin: 0;
    font-size: 1.5rem;
  }
  
  .card-info p {
    margin: 5px 0;
    font-size: 1rem;
  }

  .image-container {
  width: 100%;
  aspect-ratio: 16 / 9; /* Seitenverhältnis von 16:9 */
  overflow: hidden;
}

.image-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

</style>