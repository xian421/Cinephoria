<script>
    import { onMount } from "svelte";
  
    let seats = []; // Sitze aus dem Backend
    let screenId = 1; // Standard screen_id
    let error = ""; // Fehlermeldungen
  
    // Funktion zum Abrufen der Sitze
    async function fetchSeats() {
      try {
        const response = await fetch(`http://127.0.0.1:5000/seats?screen_id=${screenId}`, {
          headers: {
            Authorization: `Bearer ${document.cookie.split("=")[1]}`, // Token aus Cookie
          },
        });
  
        if (!response.ok) {
          throw new Error("Fehler beim Abrufen der Sitze");
        }
        const data = await response.json();
        seats = data.seats;
      } catch (err) {
        error = err.message;
      }
    }
  
    // Daten beim Laden der Seite abrufen
    onMount(fetchSeats);
  </script>
  
  <!-- Anzeige -->
  <main>
    <h1>Kinositze für Screen {screenId}</h1>
    {#if error}
      <p class="error">{error}</p>
    {:else if seats.length === 0}
      <p>Lade Sitze...</p>
    {:else}
      <div class="seat-grid">
        {#each seats as seat}
          <div class="seat-card {seat.type}">
            <p>Reihe: {seat.row}</p>
            <p>Sitz: {seat.number}</p>
            <p>Typ: {seat.type}</p>
          </div>
        {/each}
      </div>
    {/if}
  </main>
  
  <style>
    main {
      padding: 20px;
      font-family: Arial, sans-serif;
      text-align: center;
    }
  
    .seat-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
      gap: 20px;
      margin-top: 20px;
    }
  
    .seat-card {
      padding: 15px;
      border: 1px solid #ddd;
      border-radius: 8px;
      text-align: center;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      transition: transform 0.2s, box-shadow 0.2s;
    }
  
    .seat-card:hover {
      transform: scale(1.05);
      box-shadow: 0 6px 10px rgba(0, 0, 0, 0.15);
    }
  
    .seat-card.standard {
      background-color: #f0f8ff;
    }
  
    .seat-card.vip {
      background-color: #ffd700;
    }
  
    .seat-card.disabled {
      background-color: #d3d3d3;
      color: #888;
    }
  
    .error {
      color: red;
      font-weight: bold;
    }
  </style>
  