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
    height: 50px;
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
</Router>
