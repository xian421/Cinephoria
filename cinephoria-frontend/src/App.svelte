<script>
  import { Router, Route } from "svelte-routing";
  import Home from "./routes/Home.svelte";
  import NowPlaying from "./routes/Nowplaying.svelte";
  import Upcoming from "./routes/Upcoming.svelte";
  import NotFound from "./routes/Notfound.svelte";
  import Test from "./routes/Test.svelte";
  import Beschreibung from './routes/Beschreibung.svelte';
  import Sitzplan from './routes/Sitzplan.svelte';
  import Register from './routes/Register.svelte';
  import Forgotpassword from "./routes/Forgotpassword.svelte";
  import Swal from 'sweetalert2';

  export let url = ""; // Für SSR

  let currentPath = ""; // Aktuelle Route
  let userFirstName = ""; 
  let userLastName = ""; 
  let initials = "";

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



  let email = "";
  let password = "";
  let isLoginOpen = false;
  let isLoggedIn = false;

  const toggleLoginDropdown = () => {
    isLoginOpen = !isLoginOpen; // Öffnen/Schließen des Dropdowns
  };

 // Initialen berechnen
 const calculateInitials = () => {
    if (userFirstName && userLastName) {
      initials = `${userFirstName[0]}${userLastName[0]}`.toUpperCase();
      console.log("Initials:", initials); // Debugging

    }
  };

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
        console.log("Login-Daten:", data);
        email = "";
        password = "";
        isLoggedIn = true;

        // Speichere das Token in den Cookies
        document.cookie = `token=${data.token}; path=/; max-age=3600; secure; samesite=strict`;

        // Setze den Benutzernamen und berechne Initialen
        userFirstName = data.first_name; // Vom Backend
        userLastName = data.last_name; // Vom Backend
        calculateInitials();

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


let isProfileMenuOpen = false;

const toggleProfileMenu = () => {
  isProfileMenuOpen = !isProfileMenuOpen; // Öffnen/Schließen des Dropdowns
};

let isProfileDropdownOpen = false;

const logout = () => {
  // Cookie löschen
  document.cookie = "token=; path=/; max-age=0; secure; samesite=strict";

  // Benutzer-Status zurücksetzen
  isLoggedIn = false;

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
    isLoggedIn = true;
  } else {
    isLoggedIn = false;
  }
};








// Beim Laden der Seite überprüfen
checkLoginStatus();



</script>


<style>
  nav {
    display: flex;
    align-items: center;
    justify-content: space-around; /* Gleichmäßige Verteilung */
    background: #ffffff;
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
    transition: transform 0.4s ease;
  }

  .logo:hover {
    transform: scale(1.25); /* Vergrößerung des Logos beim Hover */
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
  background: #ffffff; /* Grundfarbe der Buttons */
  border: 2px solid transparent; /* Standardmäßig kein Rand */
  border-radius: 12px;
  padding: 1rem 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 160px; /* Einheitliche Breite */
  text-align: center;
}

button:hover {
  border-color: #1abc9c; /* Farbiger Rand beim Hover */
  transform: scale(1.1); /* Leichte Vergrößerung beim Hover */
}

button.active {
  color: rgb(0, 0, 0);
  border-color: rgb(21, 151, 112);
  transform: scale(1.05); /* Leichte Vergrößerung für aktiven Zustand */
}



footer {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #ffffff;
  padding: 2rem 1rem;
  border-radius: 0 0 12px 12px; /* Nur die unteren Ecken abrunden */
  box-shadow: 0 -4px 6px rgba(0, 0, 0, 0.3);
  margin-top: 2rem;
  overflow: hidden; /* Verhindert Überlagerungen durch das Pseudo-Element */
}

footer::before {
  content: '';
  position: absolute;
  top: -30px; /* Hebt die Form nach oben */
  left: 0;
  width: 100%;
  height: 60px;
  background: #ffffff;
  border-radius: 50%; /* Halbkreis-Effekt */
  box-shadow: 0 -4px 6px rgba(0, 0, 0, 0.1);
  z-index: -1; /* Hinter dem Footer platzieren */
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
  background: #ffffff; /* Grundfarbe der Buttons */
  border: 2px solid transparent; /* Standardmäßig kein Rand */
  border-radius: 12px;
  padding: 0.8rem 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  cursor: pointer;
  transition: all 0.3s ease;
}

.footer-buttons button:hover {
  border-color: #1abc9c; /* Farbiger Rand beim Hover */
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

  .scroll-to-top {
  font-size: 1rem;
  font-weight: bold;
  color: white;
  background: #3498db;
  border: 2px solid transparent; /* Standardmäßig kein Rand */
  border-radius: 50px;
  padding: 0.8rem 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 1.5rem;
}

.scroll-to-top:hover {
  border-color: #1abc9c; /* Farbiger Rand beim Hover */
  transform: scale(1.1);
  background: #24b497;
}

  .footer-text {
    color: #c0c0c0;
    font-size: 0.9rem;
    text-align: center;
  }


  .social-icons img {
    text-decoration: none;
  color: white;
  font-size: 1.5rem;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #ffffff;
  width: 50px;
  height: 50px;
  border: 2px solid transparent; /* Standardmäßig kein Rand */
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
}

.social-icons img:hover {
  border-color: #1abc9c; /* Farbiger Rand beim Hover */
  transform: scale(1.1);
}

.footer-text {
  color: black;
}


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
    padding: 1rem; /* Allgemeines Padding */
    padding-left: 20px; /* Zusätzlicher Abstand links */
    padding-right: 20px; /* Zusätzlicher Abstand rechts */
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    border-radius: 12px;
    z-index: 1000;
    width: 300px;
    transform: scaleY(0); /* Standardmäßig geschlossen */
    transform-origin: top;
    transition: transform 0.3s ease-in-out;
}


  .dropdown-container.open .dropdown-menu {
    transform: scaleY(1); /* Geöffnet */
  }

  .dropdown-menu input {
  width: calc(100% - 16px); /* Platz für Padding und Border */
  padding: 0.8rem;
  margin: 0.5rem 0;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 1rem;
  box-sizing: border-box; /* Sicherstellen, dass Padding/Borders eingerechnet werden */
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







  /* Profil-Dropdown */
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
  transform: scaleY(0); /* Standardmäßig geschlossen */
  transform-origin: top;
  transition: transform 0.3s ease-in-out;
}

.profile-dropdown-container.open .profile-dropdown-menu {
  transform: scaleY(1); /* Geöffnet */
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
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  font-weight: bold;
  color: black;
  transition: all 0.3s ease;
}

.profile-container:hover {
  transform: scale(1.05); /* Leichte Vergrößerung beim Hover */
}

.profile-initials {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background-color: red;
  color: white;
  font-size: 12px;
  font-weight: bold;
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

      {#if isLoggedIn}
      <div class="profile-dropdown-container {isProfileDropdownOpen ? 'open' : ''}">
        <button class="profile-container" on:click={() => (isProfileDropdownOpen = !isProfileDropdownOpen)}>
          <span>Profil</span>
          <div class="profile-initials">{initials}</div>
        </button>
        <div class="profile-dropdown-menu">
          <ul>
            <li on:click={() => alert('Profil anzeigen')}>Profil anzeigen</li>
            <li on:click={() => alert('Einstellungen')}>Einstellungen</li>
            <li on:click={logout}>Abmelden</li>
      </ul>
    </div>
  </div>

      {:else}
      <!-- Login Dropdown -->
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

  <!-- Routes -->
  <div>
    <Route path="/" component={Home} />
    <Route path="/nowplaying" component={NowPlaying} />
    <Route path="/upcoming" component={Upcoming} />
    <Route path="*" component={NotFound} />
    <Route path="/test" component={Test} />
    <Route path="/sitzplan" component={Sitzplan} />
    <Route path="/register" component={Register} />
    <Route path="/forgot-password" component={Forgotpassword} />

    <Route path="/beschreibung/:id" component={Beschreibung} />
  </div>
  
  <footer>
    <!-- Interaktive Buttons -->
    <div class="footer-buttons">
      <button on:click={() => alert("Kontaktformular öffnet sich hier!")}>
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
        <i class="fab fa-facebook-f"></i>
        <img src="/facebook.png" alt="LinkedIn" />
      </a>
      <a href="https://twitter.com" target="_blank" aria-label="Twitter">
        <i class="fab fa-twitter"></i>
        <img src="/twitter.png" alt="LinkedIn" />
      </a>
      <a href="https://instagram.com" target="_blank" aria-label="Instagram">
        <i class="fab fa-instagram"></i>
        <img src="/instagram.png" alt="LinkedIn" />
      </a>
      <a href="https://linkedin.com" target="_blank" aria-label="LinkedIn">
        <i class="fab fa-linkedin-in"></i>
        <img src="/linked.png" alt="LinkedIn" />
      </a>
    </div>

    
  
    <!-- Scroll-to-Top Button -->
    <button class="scroll-to-top" on:click={scrollToTop}>
      Nach oben
    </button>
  
    <!-- Footer Text -->
    <p class="footer-text">
      © 2024 Cinephoria. Alle Rechte vorbehalten.
    </p>
  </footer>
  
</Router>

