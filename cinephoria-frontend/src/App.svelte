<script>
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
    <Route path="*" component={NotFound} /> <!-- Wildcard für alle ungültigen Routen -->
  </div>
</Router>
