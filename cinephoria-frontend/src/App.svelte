<!-- Front end: App.svelte -->
<script>
  // Import von Abhängigkeiten
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
  import { authStore } from './stores/authStore.js'; // Pfad ggf. anpassen

  // Exportierte Eigenschaften
  export let url = ""; // Für Server-Side Rendering (SSR)

  // Konstanten
  const KONTAKT_URL = 'https://cinephoria-backend-c53f94f0a255.herokuapp.com/cinemas';

  // State-Variablen
  let currentPath = ""; // Aktuelle Route

  // Login-Formular
  let email = "";
  let password = "";

  // Kontaktinformationen
  let kontakt = [];
  let firstCinema = {};

  // Abonnieren des Stores
  let isLoggedIn;
  let isAdmin;
  let userFirstName;
  let userLastName;
  let initials;

  authStore.subscribe(value => {
      isLoggedIn = value.isLoggedIn;
      isAdmin = value.isAdmin;
      userFirstName = value.userFirstName;
      userLastName = value.userLastName;
      initials = value.initials;
  });

  // Navigationsfunktionen
  const handleRouteChange = () => {
      currentPath = window.location.pathname;
  };

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
          const response = await fetch("https://cinephoria-backend-c53f94f0a255.herokuapp.com/login", {
              method: "POST",
              headers: {
                  "Content-Type": "application/json",
              },
              body: JSON.stringify({ email, password }),
          });

          const data = await response.json();
          console.log('Login Response:', data);  // Debugging-Log


          if (response.ok) {
              // Login erfolgreich
              email = "";
              password = "";

              // Speichere das Token in localStorage
              localStorage.setItem('token', data.token);

              // Setze Benutzerdaten im Store
              authStore.update(current => ({
                  ...current,
                  isLoggedIn: true,
                  userFirstName: data.first_name,
                  userLastName: data.last_name,
                  initials: data.initials,
                  isAdmin: data.role === 'admin', // Setze Admin-Status basierend auf der Rolle
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
                  text: data.error,
                  icon: "error",
                  confirmButtonText: "OK",
              });
          }
      } catch (error) {
          console.error("Fehler beim Login:", error);
          Swal.fire({
              title: "Fehler",
              text: "Ein Fehler ist aufgetreten. Bitte versuche es erneut.",
              icon: "error",
              confirmButtonText: "OK",
          });
      }
  };

  const logout = () => {
      // Token aus localStorage entfernen
      localStorage.removeItem('token');

      // Benutzer-Status zurücksetzen
      authStore.set({
          isLoggedIn: false,
          userFirstName: '',
          userLastName: '',
          initials: '',
          isAdmin: false,
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
      // Kontaktinformationen laden
      try {
          const responseKontakt = await fetch(KONTAKT_URL);
          const data = await responseKontakt.json();
          kontakt = data.cinemas;

          if (kontakt && kontakt.length > 0) {
              firstCinema = kontakt[0];
          }
      } catch (error) {
          console.error('Fehler beim Laden des Kontakts: ', error);
      }

      // Überprüfen des Authentifizierungsstatus beim Laden der App
      const token = localStorage.getItem('token');
      if (token) {
          try {
              const response = await fetch("https://cinephoria-backend-c53f94f0a255.herokuapp.com/validate-token", {
                  method: "POST",
                  headers: {
                      "Content-Type": "application/json",
                      "Authorization": `Bearer ${token}`
                  },
              });

              const data = await response.json();
              console.log('Validate Token Response:', data);

              if (response.ok) {
                  // Token ist gültig, aktualisiere den Store mit den Benutzerdaten
                  authStore.update(current => ({
                      ...current,
                      isLoggedIn: true,
                      userFirstName: data.first_name,
                      userLastName: data.last_name,
                      initials: data.initials,
                      isAdmin: data.role === 'admin',
                  }));
              } else {
                  // Ungültiges Token, entferne es aus localStorage
                  localStorage.removeItem('token');
                  authStore.set({
                      isLoggedIn: false,
                      userFirstName: '',
                      userLastName: '',
                      initials: '',
                      isAdmin: false,
                  });
              }
          } catch (error) {
              console.error("Fehler beim Validieren des Tokens:", error);
              localStorage.removeItem('token');
              authStore.set({
                  isLoggedIn: false,
                  userFirstName: '',
                  userLastName: '',
                  initials: '',
                  isAdmin: false,
              });
          }
      }
  });
</script>


<style>
  /* Navbar-Stile */
  nav {
    display: flex;
    align-items: center;
    justify-content: space-around;
    background: #ffffff;
    padding: 1rem;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    position: sticky;
    top: 0;
    z-index: 1000;
  }

  /* Logo-Stile */
  .logo {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    text-decoration: none;
    color: white;
    font-size: 1.2rem;
    font-weight: bold;
    transition: transform 0.4s ease;
  }

  .logo:hover {
    transform: scale(1.25);
  }

  .logo img {
    height: 60px;
    width: auto;
    object-fit: contain;
  }

  /* Button-Stile */
  button {
    font-size: 1.2rem;
    font-weight: bold;
    color: rgb(0, 0, 0);
    background: #ffffff;
    border: 2px solid transparent;
    border-radius: 12px;
    padding: 1rem 2rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    cursor: pointer;
    transition: all 0.3s ease;
    min-width: 160px;
    text-align: center;
  }

  button:hover {
    border-color: #1abc9c;
    transform: scale(1.1);
  }

  button.active {
    color: rgb(0, 0, 0);
    border-color: rgb(21, 151, 112);
    transform: scale(1.05);
  }

  /* Footer-Stile */
  footer {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: #ffffff;
    padding: 2rem 1rem;
    border-radius: 0 0 12px 12px;
    box-shadow: 0 -4px 6px rgba(0, 0, 0, 0.3);
    margin-top: 2rem;
    overflow: hidden;
  }

  footer::before {
    content: '';
    position: absolute;
    top: -30px;
    left: 0;
    width: 100%;
    height: 60px;
    background: #ffffff;
    border-radius: 50%;
    box-shadow: 0 -4px 6px rgba(0, 0, 0, 0.1);
    z-index: -1;
  }

  .footer-buttons {
    display: flex;
    gap: 1.5rem;
    margin-bottom: 1.5rem;
  }

  .footer-buttons button {
    font-size: 1rem;
    font-weight: bold;
    color: rgb(0, 0, 0);
    background: #ffffff;
    border: 2px solid transparent;
    border-radius: 12px;
    padding: 0.8rem 1.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    cursor: pointer;
    transition: all 0.3s ease;
  }

  .footer-buttons button:hover {
    border-color: #1abc9c;
    transform: scale(1.1);
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
    background: #ffffff;
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

  .social-icons img {
    width: 100%;
    height: 100%;
    object-fit: contain;
  }

  .scroll-to-top {
    font-size: 1rem;
    font-weight: bold;
    color: white;
    background: #3498db;
    border: 2px solid transparent;
    border-radius: 50px;
    padding: 0.8rem 1.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    cursor: pointer;
    transition: all 0.3s ease;
    margin-top: 1.5rem;
  }

  .scroll-to-top:hover {
    border-color: #1abc9c;
    transform: scale(1.1);
    background: #24b497;
  }

  .footer-text {
    color: black;
    font-size: 0.9rem;
    text-align: center;
  }

  /* Login-Dropdown-Stile */
  .dropdown-container {
    position: relative;
  }

  .dropdown-menu {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    position: absolute;
    top: calc(100% + 10px);
    right: 0;
    background: #ffffff;
    padding: 1rem 20px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    border-radius: 12px;
    z-index: 1000;
    width: 300px;
    transform: scaleY(0);
    transform-origin: top;
    transition: transform 0.3s ease-in-out;
  }

  .dropdown-container.open .dropdown-menu {
    transform: scaleY(1);
  }

  .dropdown-menu input {
    width: calc(100% - 16px);
    padding: 0.8rem;
    margin: 0.5rem 0;
    border: 1px solid #ccc;
    border-radius: 8px;
    font-size: 1rem;
    box-sizing: border-box;
  }

  .dropdown-menu input:focus {
    outline: none;
    border-color: #1abc9c;
    box-shadow: 0 0 4px rgba(26, 188, 156, 0.5);
  }

  .dropdown-menu button {
    width: 100%;
    background: #3498db;
    color: #ffffff;
    font-size: 1rem;
    font-weight: bold;
    padding: 0.8rem;
    border: none;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
  }

  .dropdown-menu button:hover {
    background: #24b497;
  }

  /* Profil-Dropdown-Stile */
  .profile-dropdown-container {
    position: relative;
  }

  .profile-dropdown-menu {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: flex-start;
    position: absolute;
    top: calc(100% + 10px);
    right: 0;
    background: #ffffff;
    padding: 1rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    border-radius: 12px;
    z-index: 1000;
    width: 200px;
    transform: scaleY(0);
    transform-origin: top;
    transition: transform 0.3s ease-in-out;
  }

  .profile-dropdown-container.open .profile-dropdown-menu {
    transform: scaleY(1);
  }

  .profile-dropdown-menu ul {
    list-style: none;
    padding: 0;
    margin: 0;
    width: 100%;
  }

  .profile-dropdown-menu li {
    padding: 0.8rem;
    font-size: 1rem;
    color: #333;
    cursor: pointer;
    transition: background-color 0.3s ease;
    width: 100%;
    text-align: left;
  }

  .profile-dropdown-menu li:hover {
    background-color: #f0f0f0;
    border-radius: 8px;
  }

  .profile-container {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    font-size: 1rem;
    font-weight: bold;
    color: black;
    transition: all 0.3s ease;
  }

  .profile-container:hover {
    transform: scale(1.1);
  }

  .profile-initials {
    width: 50px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background-color: red;
    color: white;
    font-size: 20px;
    font-weight: bold;
  }
</style>

<Router {url}>
  <!-- Navbar -->
  <nav>
      <!-- Logo -->
      <a href="/" class="logo" on:click={() => navigate('/')}>
          <img src="/Logo.png" alt="Logo" />
      </a>

      <!-- Navigationsbuttons -->
      <button
          class="{currentPath === '/' ? 'active' : ''}"
          on:click={() => navigate('/')}
      >
          Alle Filme
      </button>
      <button
          class="{currentPath === '/nowplaying' ? 'active' : ''}"
          on:click={() => navigate('/nowplaying')}
      >
          Programm
      </button>
      <button
          class="{currentPath === '/upcoming' ? 'active' : ''}"
          on:click={() => navigate('/upcoming')}
      >
          Upcoming
      </button>
      <button
          class="{currentPath === '/sitzplan' ? 'active' : ''}"
          on:click={() => navigate('/sitzplan')}
      >
          Sitzplan
      </button>

      <!-- Benutzerbereich -->
      {#if isLoggedIn}
          <!-- Profil-Dropdown -->
          <div class="profile-dropdown-container {isProfileDropdownOpen ? 'open' : ''}">
              <div class="profile-container" on:click={toggleProfileMenu}>
                  <div class="profile-initials">{initials}</div>
              </div>
              <div class="profile-dropdown-menu">
                  <ul>
                      <li on:click={() => navigate('/profil')}>Profil anzeigen</li>
                      <li on:click={() => navigate('/einstellungen')}>Einstellungen</li>
                      <li on:click={logout}>Abmelden</li>
                  </ul>
              </div>
          </div>
      {:else}
          <!-- Login-Dropdown -->
          <div class="dropdown-container {isLoginOpen ? 'open' : ''}">
              <button on:click={toggleLoginDropdown}>Login</button>
              <div class="dropdown-menu">
                  <form on:submit|preventDefault={handleLogin}>
                      <input type="email" placeholder="E-Mail" bind:value={email} required />
                      <input type="password" placeholder="Passwort" bind:value={password} required />
                      <button type="submit">Einloggen</button>
                      <div style="display: flex; justify-content: space-between; gap: 10px; margin-top: 10px;">
                          <button type="button" on:click={() => navigate('/register')} style="background: none; border: none; color: #007bff; cursor: pointer;">
                              Stattdessen Registrieren
                          </button>
                          <button type="button" on:click={() => navigate('/forgot-password')} style="background: none; border: none; color: #007bff; cursor: pointer;">
                              Passwort vergessen?
                          </button>
                      </div>
                  </form>
              </div>
          </div>
      {/if}
  </nav>

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
      <!-- Admin-Routen -->
      <Route path="/adminkinosaal" component={Adminkinosaal} />
      <Route path="/adminseats/:screenId" component={Adminseats} />
      <Route path="/beschreibung/:id" component={Beschreibung} />
      <Route path="/unauthorized" component={Unauthorized} />
      <!-- Weitere Routen, wie z.B. Profil oder Einstellungen -->
  </div>

  <!-- Footer -->
  <footer>
      <!-- Interaktive Buttons -->
      <div class="footer-buttons">
          <button on:click={() => Swal.fire({
              title: "Kontakt",
              icon: "info",
              html: `
                  <h2>${firstCinema.name}</h2>
                  <p>Standort: ${firstCinema.location}<br />
                  Telefax: ${firstCinema.contact_number}<br />
              `,
              confirmButtonText: "Schließen"
          })}>
              Kontakt
          </button>
          <button on:click={() => Swal.fire({
              title: "Impressum",
              icon: "info",
              html: `
                  <p>Max Mustermann<br />
                  Musterweg 111<br />
                  Hausnummer 44<br />
                  90210 Musterstadt</p>
                  <h2>Kontakt</h2>
                  <p>Telefon: +49 (0) 123 44 55 66<br />
                  Telefax: +49 (0) 123 44 55 99<br />
                  E-Mail: mustermann@musterfirma.de</p>
              `,
              confirmButtonText: "Schließen"
          })}>
              Impressum
          </button>
          <button on:click={() => alert("Datenschutz anzeigen!")}>
              Datenschutz
          </button>
      </div>

      <!-- Social-Media-Icons -->
      <div class="social-icons">
          <a href="https://facebook.com" target="_blank" aria-label="Facebook">
              <img src="/facebook.png" alt="Facebook" />
          </a>
          <a href="https://twitter.com" target="_blank" aria-label="Twitter">
              <img src="/twitter.png" alt="Twitter" />
          </a>
          <a href="https://instagram.com" target="_blank" aria-label="Instagram">
              <img src="/instagram.png" alt="Instagram" />
          </a>
          <a href="https://linkedin.com" target="_blank" aria-label="LinkedIn">
              <img src="/linked.png" alt="LinkedIn" />
          </a>
      </div>

      <!-- Scroll-to-Top Button -->
      <button class="scroll-to-top" on:click={scrollToTop}>
          Nach oben
      </button>

      <!-- Footer-Text -->
      <p class="footer-text">
          © 2024 Cinephoria. Alle Rechte vorbehalten.
      </p>
  </footer>
</Router>