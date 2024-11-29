<!-- adminseats.svelte -->
<script>
    export let screenId; // screenId wird von der Route übergeben
  
    import { onMount } from "svelte";
    import { navigate } from "svelte-routing";
  
    let isAdmin = false;
    let seats = [];
    let error = "";
  
    const getTokenFromCookies = () => {
      const cookies = document.cookie.split("; ").reduce((acc, cookie) => {
        const [key, value] = cookie.split("=");
        acc[key] = value;
        return acc;
      }, {});
      return cookies.token || '';
    };
  
    const fetchSeats = async () => {
      const token = getTokenFromCookies();
  
      if (!token) {
        console.error("Kein Token gefunden.");
        navigate("/");
        return;
      }
  
      try {
        const response = await fetch(`https://cinephoria-backend-c53f94f0a255.herokuapp.com/seats?screen_id=${screenId}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
  
        if (!response.ok) {
          if (response.status === 401) {
            error = "Du bist nicht autorisiert.";
          } else {
            error = "Fehler beim Abrufen der Sitze.";
          }
          return;
        }
  
        const data = await response.json();
        seats = data.seats;
      } catch (err) {
        error = "Verbindungsfehler. Bitte überprüfe deine Internetverbindung.";
      }
    };
  
    const checkAdminStatus = () => {
      const token = getTokenFromCookies();
      if (token) {
        try {
          const payload = JSON.parse(atob(token.split(".")[1]));
          isAdmin = payload.role === "admin";
        } catch (error) {
          console.error("Fehler beim Überprüfen des Tokens:", error);
          isAdmin = false;
        }
      } else {
        isAdmin = false;
      }
    };
  
    onMount(() => {
      checkAdminStatus();
      if (isAdmin) {
        fetchSeats();
      } else {
        navigate("/"); // Weiterleitung zur Startseite
      }
    });
  </script>
  
  <main>
    {#if isAdmin}
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
    {:else}
      <p>Du hast keinen Zugriff auf diese Seite.</p>
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
  