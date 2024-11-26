<script>
  import { Router, Route } from "svelte-routing";
  import Home from "./routes/Home.svelte";
  import NowPlaying from "./routes/Nowplaying.svelte";
  import Upcoming from "./routes/Upcoming.svelte";
  import NotFound from "./routes/Notfound.svelte";
  import Test from "./routes/Test.svelte";
  import Beschreibung from './routes/Beschreibung.svelte';

  export let url = ""; // Für SSR

  let currentPath = ""; // Aktuelle Route

  const handleRouteChange = () => {
    currentPath = window.location.pathname;
  };

  if (typeof window !== "undefined") {
    window.addEventListener("popstate", handleRouteChange);
    handleRouteChange();
  }

  const navigate = (path) => {
    if (currentPath !== path) {
      currentPath = path;
      window.history.pushState({}, "", path);
      window.dispatchEvent(new PopStateEvent("popstate"));
    }
  };

  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: "smooth"
    });
  };
</script>

<style>
  nav {
    display: flex;
    align-items: center;
    justify-content: space-around; /* Gleichmäßige Verteilung */
    background: #f2f2f2;
    padding: 1rem;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    position: sticky;
    top: 0;
    z-index: 1000;
  }

  .logo {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    text-decoration: none;
    color: white;
    font-size: 1.2rem;
    font-weight: bold;
  }

  .logo:hover {
    transform: scale(1.1); /* Vergrößerung des Logos beim Hover */
  }

  .logo img {
    height: 60px;
    width: auto;
    object-fit: contain;
  }

  button {
    font-size: 1.2rem;
    font-weight: bold;
    color: rgb(0, 0, 0);
    background: #f2f2f2; /* Grundfarbe der Buttons */
    border: none;
    border-radius: 12px;
    padding: 1rem 2rem;
    
    cursor: pointer;
    transition: all 0.3s ease;
    min-width: 120px; /* Einheitliche Breite */
    text-align: center;
  }

  button:hover {
    background: #4e5d5a; /* Hover-Farbe */
    transform: scale(1.1); /* Leichte Vergrößerung beim Hover */
  }

  button.active {
    background: #5686a6; /* Farbe für aktiven Button */
    color: white;
    transform: scale(1.05); /* Leichte Vergrößerung für aktiven Zustand */
  }



  footer {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: #2e3b4e;
    padding: 2rem 1rem;
    border-radius: 12px;
    box-shadow: 0 -4px 6px rgba(0, 0, 0, 0.3);
    margin-top: 2rem;
  }

  .footer-buttons {
    display: flex;
    gap: 1.5rem;
    margin-bottom: 1.5rem;
  }

  .footer-buttons button {
    font-size: 1rem;
    font-weight: bold;
    color: white;
    background: #6c7a89; /* Grundfarbe der Buttons */
    border: none;
    border-radius: 12px;
    padding: 0.8rem 1.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    cursor: pointer;
    transition: all 0.3s ease;
  }

  .footer-buttons button:hover {
    background: #1abc9c; /* Hover-Farbe */
    transform: scale(1.1); /* Leichte Vergrößerung beim Hover */
  }

  .social-icons {
    display: flex;
    gap: 1.5rem;
    margin-bottom: 1.5rem;
  }

  .social-icons a {
    text-decoration: none;
    color: white;
    font-size: 1.5rem;
    display: flex;
    justify-content: center;
    align-items: center;
    background: #6c7a89;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    transition: all 0.3s ease;
  }

  .social-icons a:hover {
    background: #1abc9c;
    transform: scale(1.1);
  }

  .scroll-to-top {
    font-size: 1rem;
    font-weight: bold;
    color: white;
    background: #3498db;
    border: none;
    border-radius: 50px;
    padding: 0.8rem 1.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    cursor: pointer;
    transition: all 0.3s ease;
    margin-top: 1.5rem;
  }

  .scroll-to-top:hover {
    background: #1abc9c;
    transform: scale(1.1);
  }

  .footer-text {
    color: #c0c0c0;
    font-size: 0.9rem;
    text-align: center;
  }




</style>




<Router {url}>
  <!-- Navbar -->
  <nav>
    <!-- Logo-Bereich -->
    <a href="/" class="logo" on:click={() => navigate('/')}>
      <img src="/Logo.png" alt="Logo" />
    </a>

    <!-- Menü-Buttons -->
    <button
      class="{currentPath === '/' ? 'active' : ''}"
      on:click={() => navigate('/')}
    >
      Home
    </button>
    <button
      class="{currentPath === '/nowplaying' ? 'active' : ''}"
      on:click={() => navigate('/nowplaying')}
    >
      NowPlaying
    </button>
    <button
      class="{currentPath === '/upcoming' ? 'active' : ''}"
      on:click={() => navigate('/upcoming')}
    >
      Upcoming
    </button>
    <button
      class="{currentPath === '/test' ? 'active' : ''}"
      on:click={() => navigate('/test')}
    >
      Test
    </button>
  </nav>

  <!-- Routes -->
  <div>
    <Route path="/" component={Home} />
    <Route path="/nowplaying" component={NowPlaying} />
    <Route path="/upcoming" component={Upcoming} />
    <Route path="*" component={NotFound} />
    <Route path="/test" component={Test} />
    <Route path="/beschreibung/:id" component={Beschreibung} />
  </div>
  
  <footer>
    <!-- Interaktive Buttons -->
    <div class="footer-buttons">
      <button on:click={() => alert("Kontaktformular öffnet sich hier!")}>
        Kontakt
      </button>
      <button on:click={() => alert("Impressum anzeigen!")}>
        Impressum
      </button>
      <button on:click={() => alert("Datenschutz anzeigen!")}>
        Datenschutz
      </button>
    </div>
  
    <!-- Social-Media-Icons -->
    <div class="social-icons">
      <a href="https://facebook.com" target="_blank" aria-label="Facebook">
        <i class="fab fa-facebook-f"></i>
      </a>
      <a href="https://twitter.com" target="_blank" aria-label="Twitter">
        <i class="fab fa-twitter"></i>
      </a>
      <a href="https://instagram.com" target="_blank" aria-label="Instagram">
        <i class="fab fa-instagram"></i>
      </a>
      <a href="https://linkedin.com" target="_blank" aria-label="LinkedIn">
        <i class="fab fa-linkedin-in"></i>
      </a>
    </div>
  
    <!-- Scroll-to-Top Button -->
    <button class="scroll-to-top" on:click={scrollToTop}>
      Nach oben
    </button>
  
    <!-- Footer Text -->
    <p class="footer-text">
      © 2024 Meine App. Alle Rechte vorbehalten.
    </p>
  </footer>
  
</Router>

