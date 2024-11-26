<!-- <script>
  import { Router, Link, Route } from "svelte-routing";
  import Home from "./routes/Home.svelte";
  import NowPlaying from "./routes/Nowplaying.svelte";
  import Upcoming from "./routes/Upcoming.svelte";
  import NotFound from "./routes/Notfound.svelte"; // NotFound-Seite importieren

  export let url = ""; // Für SSR
</script>

<Router {url}>
  <nav>
    <Link to="/">Home</Link>
    <Link to="/nowplaying">NowPlaying</Link>
    <Link to="/upcoming">Upcoming</Link>
  </nav>

  <div>
    <Route path="/" component={Home} />
    <Route path="/nowplaying" component={NowPlaying} />
    <Route path="/upcoming" component={Upcoming} />
    <Route path="*" component={NotFound} /> 
  </div>
</Router> -->


<script>
  export let name = "Cinephoria";
</script>

<style>
  main {
    text-align: center;
    font-family: Arial, sans-serif;
    margin: 0 auto;
    max-width: 800px;
    padding: 20px;
  }

  h1 {
    font-size: 3rem;
    margin-bottom: 20px;
    color: #ff5733; /* Eine auffällige Farbe */
  }

  p {
    font-size: 1.2rem;
    margin-bottom: 30px;
    color: #555;
  }

  .button-container {
    display: flex;
    justify-content: center;
    gap: 15px;
  }

  a {
    text-decoration: none;
    background-color: #ff5733;
    color: white;
    padding: 10px 20px;
    border-radius: 5px;
    font-size: 1rem;
    transition: background-color 0.3s ease;
  }

  a:hover {
    background-color: #c43d27; /* Dunklerer Hover-Effekt */
  }

  img {
    max-width: 100%;
    height: auto;
    margin-top: 20px;
    border-radius: 10px;
  }
</style>

<main>
  <h1>Welcome to {name}!</h1>
  <p>Discover current and upcoming movies.</p>
  <div class="button-container">
    <a href="/nowplaying">Now Playing</a>
    <a href="/upcoming">Upcoming</a>
  </div>
  <img src="/img/Logo.jpg" alt="Cinephoria banner" />
</main>
