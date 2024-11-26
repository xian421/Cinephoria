<script>
  import { Router, Link, Route } from "svelte-routing";
  import Home from "./routes/Home.svelte";
  import NowPlaying from "./routes/Nowplaying.svelte";
  import Upcoming from "./routes/Upcoming.svelte";
  import NotFound from "./routes/Notfound.svelte";
  import Test from "./routes/Test.svelte";
  import Beschreibung from './Beschreibung.svelte';

  export let url = ""; // Für SSR

  let menuOpen = false; // Zustand für das ausklappbare Menü
  let currentPath = ""; // Aktuelle Route

  const handleRouteChange = () => {
    currentPath = window.location.pathname;
  };

  if (typeof window !== "undefined") {
    window.addEventListener("popstate", handleRouteChange);
    handleRouteChange();
  }
</script>

<style>
  nav {
    display: flex;
    align-items: center; 
    justify-content: space-between;
    background: #f3f3f3; /* Hellgrauer Hintergrund passend zum Logo */
    color: white;
    padding: 0.5rem 2rem;
    height: 60px; /* Passt die Höhe an das Logo an */
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    position: sticky;
    top: 0;
    z-index: 1000;
    border-radius: 12px; /* Rundet die Ecken mit einem Radius von 12px */
}


  .logo {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    text-decoration: none;
    transition: transform 0.3s ease; /* Transition für den Hover-Effekt */
  }

  .logo img {
    height: 70px; /* Höhe des Logos */
    width: auto; /* Automatische Breite, um das Seitenverhältnis zu wahren */
    object-fit: contain;
  }

  .logo:hover {
    transform: scale(1.1); /* Vergrößerung des Logos beim Hover */
  }

  .menu-button {
    background: none;
    border: none;
    color: #ffffff;
    font-size: 1.8rem;
    cursor: pointer;
    display: none;
  }

  .menu-links {
    display: flex;
    gap: 12rem; /* Abstand zwischen den Links */
    flex: 3;
    justify-content: center;
  }

  .menu-links a {
    text-decoration: none;
    font-size: 1.4rem; /* Größere Schriftgröße */
    font-weight: bold;
    text-align: center;
    background: #d6d6d6; /* Leicht dunkler als der Navbar-Hintergrund */
    color: #222222; /* Neue Schriftfarbe */
    padding: 1rem 1.5rem; /* Buttons größer gemacht */
    border-radius: 8px; /* Leicht abgerundete Kästchen */
    transition: all 0.3s ease;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2); /* Schatten für die Kästchen */
  }

  .menu-links a:hover {
    background: #bcbcbc; /* Heller Hover-Effekt */
    color: #000000; /* Farbe bei Hover */
    transform: scale(1.05); /* Leichte Vergrößerung beim Hover */
  }

  .menu-links a.active {
    background: #4b4a4a; /* Aktiver Zustand */
    color: #ffffff; /* Weiße Schrift bei Aktiv */
    font-weight: bold;
    transform: scale(1.05);
  }

  @media (max-width: 768px) {
    .menu-button {
      display: block;
    }

    .menu-links {
      display: none;
      flex-direction: column;
      width: 100%;
      position: absolute;
      top: 60px; /* Unterhalb der Navbar */
      left: 0;
      background: #494848;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }

    .menu-links.open {
      display: flex;
    }

    .menu-links a {
      padding: 1.5rem; /* Buttons im mobilen Modus */
      width: 100%; /* Ganze Breite nutzen */
    }
  }
</style>

<Router {url}>
  <nav>
    <!-- Logo-Bereich -->
    <a href="/" class="logo">
      <img src="/Logo.png" alt="Logo" />
    </a>

    <!-- Hamburger-Menü für kleine Bildschirme -->
    <button class="menu-button" on:click={() => (menuOpen = !menuOpen)}>
      ☰
    </button>

    <!-- Menü-Links -->
    <div class="menu-links {menuOpen ? 'open' : ''}">
      <Link
        to="/"
        class="{currentPath === '/' ? 'active' : ''}"
      >
        Home
      </Link>
      <Link
        to="/nowplaying"
        class="{currentPath === '/nowplaying' ? 'active' : ''}"
      >
        NowPlaying
      </Link>
      <Link
        to="/upcoming"
        class="{currentPath === '/upcoming' ? 'active' : ''}"
      >
        Upcoming
      </Link>
      <Link
        to="/test"
        class="{currentPath === '/test' ? 'active' : ''}"
      >
        Test
      </Link>
    </div>
  </nav>

  <div>
    <Route path="/" component={Home} />
    <Route path="/nowplaying" component={NowPlaying} />
    <Route path="/upcoming" component={Upcoming} />
    <Route path="*" component={NotFound} />
    <Route path="/test" component={Test} />
    <Route path="/beschreibung/:id" component={Beschreibung} />
  </div>
</Router>
