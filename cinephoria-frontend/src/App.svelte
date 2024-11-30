<!-- src/App.svelte -->
<script>
  import { login, validateToken, fetchCinemas } from './services/api.js';
  import { Router, Route, navigate } from "svelte-routing";
  import { onMount } from 'svelte';
  import Swal from 'sweetalert2';

  // Import von Komponenten
  import Home from "./routes/Home.svelte";
  import NowPlaying from "./routes/Nowplaying.svelte";
  import Upcoming from "./routes/Upcoming.svelte";
  import NotFound from "./routes/Notfound.svelte";
  import Test from "./routes/Test.svelte";
  import Beschreibung from './routes/Beschreibung.svelte';
  import Sitzplan from './routes/Sitzplan.svelte';
  import Register from './routes/Register.svelte';
  import Forgotpassword from "./routes/Forgotpassword.svelte";
  import Adminkinosaal from "./routes/Adminkinosaal.svelte";
  import Adminseats from "./routes/Adminseats.svelte";
  import Unauthorized from "./routes/Unauthorized.svelte";

  // Import von Svelte Stores
  import { authStore, setAuth, updateAuth } from './stores/authStore.js';

  // Import der ProtectedRoute Komponente
  import ProtectedRoute from './components/ProtectedRoute.svelte';
  import Navbar from './components/Navbar.svelte';
  import Footer from './components/Footer.svelte';

  // Exportierte Eigenschaften
  export let url = ""; // Für Server-Side Rendering (SSR)

  // Konstanten
  const KONTAKT_URL = 'https://cinephoria-backend-c53f94f0a255.herokuapp.com/cinemas';

  // State-Variablen
  let currentPath = "";
  let email = "";
  let password = "";
  let kontakt = [];
  let firstCinema = {};

  // Reaktive Zuweisung der Store-Werte
  $: isLoggedIn = $authStore.isLoggedIn;
  $: isAdmin = $authStore.isAdmin;
  $: userFirstName = $authStore.userFirstName;
  $: userLastName = $authStore.userLastName;
  $: initials = $authStore.initials;
  $: token = $authStore.token;

  // Ladezustand
  let isLoading = true;

  // Navigationsfunktionen
  const handleRouteChange = () => {
      currentPath = window.location.pathname;
  };

  // Event-Listener für Popstate (Browser-Zurück-Button)
  if (typeof window !== "undefined") {
      window.addEventListener("popstate", handleRouteChange);
      handleRouteChange();
  }

  const scrollToTop = () => {
      window.scrollTo({
          top: 0,
          behavior: "smooth"
      });
  };

  // Dropdown-Funktionen
  let isLoginOpen = false;
  let isProfileDropdownOpen = false;

  const toggleLoginDropdown = () => {
      isLoginOpen = !isLoginOpen;
  };

  const toggleProfileMenu = () => {
      isProfileDropdownOpen = !isProfileDropdownOpen;
  };

  // Authentifizierungsfunktionen
  const handleLogin = async () => {
      if (!email || !password) {
          Swal.fire({
              title: "Fehler",
              text: "Bitte E-Mail und Passwort eingeben!",
              icon: "error",
              confirmButtonText: "OK",
          });
          return;
      }

      try {
          const data = await login(email, password);
          console.log('Login Response:', data);  // Debugging-Log

          if (data.token) {
              email = "";
              password = "";
              localStorage.setItem('token', data.token);
              updateAuth(current => ({
                  isLoggedIn: true,
                  userFirstName: data.first_name,
                  userLastName: data.last_name,
                  initials: data.initials,
                  isAdmin: data.role.toLowerCase() === 'admin',
                  token: data.token, // Token im Store speichern
              }));

              Swal.fire({
                  title: "Erfolgreich eingeloggt!",
                  text: "Willkommen zurück!",
                  icon: "success",
                  timer: 1500,
                  showConfirmButton: false,
              });
          } else {
              Swal.fire({
                  title: "Fehler",
                  text: data.error || "Unbekannter Fehler",
                  icon: "error",
                  confirmButtonText: "OK",
              });
          }
      } catch (error) {
          console.error("Fehler beim Login:", error);
          Swal.fire({
              title: "Fehler",
              text: error.message || "Ein Fehler ist aufgetreten. Bitte versuche es erneut.",
              icon: "error",
              confirmButtonText: "OK",
          });
      }
  };

  const logout = () => {
      localStorage.removeItem('token');
      setAuth({
          isLoggedIn: false,
          userFirstName: '',
          userLastName: '',
          initials: '',
          isAdmin: false,
          token: null,
      });

      Swal.fire({
          title: "Abgemeldet",
          text: "Du wurdest erfolgreich abgemeldet.",
          icon: "success",
          timer: 1500,
          showConfirmButton: false,
      });

      navigate('/');
  };

  // Lifecycle-Methode
  onMount(async () => {
      try {
          const data = await fetchCinemas();
          kontakt = data.cinemas;

          if (kontakt && kontakt.length > 0) {
              firstCinema = kontakt[0];
          }
      } catch (error) {
          console.error('Fehler beim Laden des Kontakts: ', error);
      }

      const token = localStorage.getItem('token');
      if (token) {
          try {
              const data = await validateToken(token);
              console.log('Validate Token Response:', data);

              // Da validateToken keine isValid zurückgibt, setze den Auth-Zustand direkt
              updateAuth(current => ({
                  isLoggedIn: true,
                  userFirstName: data.first_name,
                  userLastName: data.last_name,
                  initials: data.initials,
                  isAdmin: data.role.toLowerCase() === 'admin',
                  token: token,
              }));
          } catch (error) {
              console.error("Fehler beim Validieren des Tokens:", error);
              localStorage.removeItem('token');
              setAuth({
                  isLoggedIn: false,
                  userFirstName: '',
                  userLastName: '',
                  initials: '',
                  isAdmin: false,
                  token: null,
              });
          }
      }

      isLoading = false;
  });
</script>

{#if isLoading}
  <p>Loading...</p>
{:else}
  <Router {url}>
      <Navbar 
          currentPath={currentPath} 
          toggleLoginDropdown={toggleLoginDropdown} 
          toggleProfileMenu={toggleProfileMenu} 
          logout={logout} 
          isLoginOpen={isLoginOpen} 
          isProfileDropdownOpen={isProfileDropdownOpen} 
          bind:email={email} 
          bind:password={password} 
          handleLogin={handleLogin} 
          initials={initials} 
          isLoggedIn={isLoggedIn}
      />

      <!-- Routen -->
      <div>
          <Route path="/" component={Home} />
          <Route path="/nowplaying" component={NowPlaying} />
          <Route path="/upcoming" component={Upcoming} />
          <Route path="*" component={NotFound} />
          <Route path="/test" component={Test} />
          <Route path="/sitzplan" component={Sitzplan} />
          <Route path="/register" component={Register} />
          <Route path="/forgot-password" component={Forgotpassword} />

          <!-- Geschützte Admin-Routen mit ProtectedRoute -->
          <Route path="/adminkinosaal" let:params>
              <ProtectedRoute admin={true}>
                  <Adminkinosaal />
              </ProtectedRoute>
          </Route>
          <Route path="/adminseats/:screenId" let:params>
              <ProtectedRoute admin={true}>
                  <Adminseats />
              </ProtectedRoute>
          </Route>

          <Route path="/beschreibung/:id" component={Beschreibung} />
          <Route path="/unauthorized" component={Unauthorized} />
          <!-- Weitere Routen -->
      </div>

      <Footer firstCinema={firstCinema} />
  </Router>
{/if}
