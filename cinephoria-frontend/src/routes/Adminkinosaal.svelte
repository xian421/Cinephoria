<script>
    import { onMount } from "svelte";
  
    let screens = [];

    const getTokenFromCookies = () => {
    const cookies = document.cookie.split("; ").reduce((acc, cookie) => {
      const [key, value] = cookie.split("=");
      acc[key] = value;
      return acc;
    }, {});
    return cookies.token || '';
  };

  
  onMount(async () => {
    const token = getTokenFromCookies();
    try {
      const response = await fetch("https://cinephoria-backend-c53f94f0a255.herokuapp.com/screens", {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await response.json();
      if (response.ok) {
        screens = data.screens;
      } else {
        console.error("Fehler beim Laden der Kinosäle:", data.error);
      }
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
            <h3 class="card-name">{screen.name}</h3> <!-- Name bleibt im Bild -->
        </div>        
        <div class="card-overlay">
          <div class="card-info">
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
    grid-template-columns: repeat(2, 1fr); /* Zwei Karten nebeneinander */
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
    text-align: center; /* Zentriert den Text */
}

.card img {
    width: 100%;
    height: 200px;
    object-fit: cover;
}

.card-name {
    position: absolute;
    bottom: 10px; /* Am unteren Rand des Bildes */
    left: 50%;
    transform: translateX(-50%);
    font-size: 1.5rem;
    font-weight: bold;
    color: white; /* Sichtbarer Text auf dunklem Hintergrund */
    text-shadow: 0px 0px 10px rgba(0, 0, 0, 0.8); /* Schatten für bessere Lesbarkeit */
    background: rgba(0, 0, 0, 0.5); /* Halbtransparenter Hintergrund */
    padding: 5px 10px;
    border-radius: 8px;
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
  
.card-info p {
    margin: 5px 0;
    font-size: 1rem;
}

.image-container {
    position: relative; /* Macht das Element relativ für das absolute Positionieren */
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