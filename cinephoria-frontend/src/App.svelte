<script>
  // Import von Abhängigkeiten
  import { Router, Route } from "svelte-routing";
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
  import Unauthorized from "./routes/Unauthorized.svelte";

  //Exportierte Eigenschaften
  export let url = ""; // Für Server-Side Rendering (SSR)

  // Konstanten
  const KONTAKT_URL = 'https://cinephoria-backend-c53f94f0a255.herokuapp.com/cinemas';

  // State-Variablen
  let currentPath = ""; // Aktuelle Route
  let isLoggedIn = false;
  let isAdmin = false;
  let isLoginOpen = false;
  let isProfileDropdownOpen = false;

  //Benutzerdaten
  let userFirstName = ""; 
  let userLastName = ""; 
  let initials = "";

  //Login-Formular
  let email = "";
  let password = "";

  //Kontaktinformationen
  let kontakt = [];
  let firstCinema = {};

  // Navigationsfunktionen 
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

  // Dropdown-Funktionen 
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

      if (response.ok) {
        // Login erfolgreich
        email = "";
        password = "";
        isLoggedIn = true;

        // Speichere das Token in den Cookies
        document.cookie = `token=${data.token}; path=/; max-age=3600; secure; samesite=strict`;

        // Setze Benutzerdaten
        userFirstName = data.first_name;
        userLastName = data.last_name;
        initials = data.initials;

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
    // Cookie löschen
    document.cookie = "token=; path=/; max-age=0; secure; samesite=strict";

    // Benutzer-Status zurücksetzen
    isLoggedIn = false;
    isAdmin = false;
    userFirstName = '';
    userLastName = '';
    initials = '';

    Swal.fire({
      title: "Abgemeldet",
      text: "Du wurdest erfolgreich abgemeldet.",
      icon: "success",
      timer: 1500,
      showConfirmButton: false,
    });
  };

  const checkLoginStatus = () => {
    const cookies = document.cookie.split("; ").reduce((acc, cookie) => {
      const [key, value] = cookie.split("=");
      acc[key] = value;
      return acc;
    }, {});

    if (cookies.token) {
      const token = cookies.token;
      try {
        // Token dekodieren
        const payload = JSON.parse(atob(token.split(".")[1]));
        isLoggedIn = true;
        isAdmin = payload.role === "admin";

        // Benutzerdaten aus dem Token extrahieren
        userFirstName = payload.first_name;
        userLastName = payload.last_name;
        initials = payload.initials;

        // Initialen berechnen, falls nicht vorhanden
        if (!initials && userFirstName && userLastName) {
          initials = `${userFirstName[0].toUpperCase()}${userLastName[0].toUpperCase()}`;
        }
      } catch (error) {
        console.error("Fehler beim Dekodieren des Tokens:", error);
        isLoggedIn = false;
        isAdmin = false;
        userFirstName = '';
        userLastName = '';
        initials = '';
      }
    } else {
      isLoggedIn = false;
      isAdmin = false;
      userFirstName = '';
      userLastName = '';
      initials = '';
    }
  };

  // Lifecycle-Methode
  onMount(async () => {
    checkLoginStatus();
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
            <li on:click={() => alert('Profil anzeigen')}>Profil anzeigen</li>
            <li on:click={() => alert('Einstellungen')}>Einstellungen</li>
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
              <button on:click={() => navigate('/register')} style="background: none; border: none; color: #007bff; cursor: pointer;">Stattdessen Registrieren</button>
              <button on:click={() => navigate('/forgot-password')} style="background: none; border: none; color: #007bff; cursor: pointer;">Passwort vergessen?</button>
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
    <Route path="/adminkinosaal" component={isAdmin ? Adminkinosaal : Unauthorized} />
    <Route path="/beschreibung/:id" component={Beschreibung} />
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
