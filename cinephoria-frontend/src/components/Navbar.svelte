<!-- src/components/Navbar.svelte -->
<script>
  import { navigate, useLocation } from "svelte-routing";
  import { authStore } from '../stores/authStore';
  import Swal from "sweetalert2";

  export let toggleLoginDropdown;
  export let toggleProfileMenu;
  export let logout;
  export let handleLogin;
  
  export let isLoginOpen = false;
  export let isProfileDropdownOpen;
  
  let email = "";
  let password = "";
  let firstName = "";
  let lastName = "";
  
  let currentView = 'login'; // 'login', 'register', 'forgotPassword'

  const onLoginSubmit = async () => {
      if (!email || !password) {
          Swal.fire("Fehler", "Bitte gib E-Mail und Passwort ein.", "error");
          return;
      }
      await handleLogin(email, password);
      email = "";
      password = "";
      toggleLoginDropdown(false);
  };

  const handleRegisterFn = async () => {
      if (!firstName || !lastName || !email || !password) {
          Swal.fire("Fehler", "Bitte fülle alle Felder aus.", "error");
          return;
      }

      try {
          const response = await fetch("https://cinephoria-backend-c53f94f0a255.herokuapp.com/register", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ first_name: firstName, last_name: lastName, email, password }),
          });

          const data = await response.json();

          if (response.ok) {
              Swal.fire("Erfolgreich registriert!", "Du kannst dich jetzt einloggen.", "success");
              currentView = 'login';
              firstName = "";
              lastName = "";
              email = "";
              password = "";
          } else {
              Swal.fire("Fehler", data.error || "Ein Fehler ist aufgetreten.", "error");
          }
      } catch (error) {
          Swal.fire("Fehler", "Es konnte keine Verbindung zum Server hergestellt werden.", "error");
      }
  };

  const handleForgotPasswordFn = async () => {
      if (!email) {
          Swal.fire("Fehler", "Bitte gib deine E-Mail-Adresse ein.", "error");
          return;
      }

      try {
          const response = await fetch("https://cinephoria-backend-c53f94f0a255.herokuapp.com/forgot-password", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ email }),
          });

          const data = await response.json();

          if (response.ok) {
              Swal.fire(
                  "E-Mail gesendet!",
                  "Falls die E-Mail existiert, erhältst du in Kürze Anweisungen zum Zurücksetzen des Passworts.",
                  "success"
              );
              email = "";
              currentView = 'login';
          } else {
              Swal.fire("Fehler", data.error || "Ein Fehler ist aufgetreten.", "error");
          }
      } catch (error) {
          Swal.fire("Fehler", "Es konnte keine Verbindung zum Server hergestellt werden.", "error");
      }
  };

  const location = useLocation();

  // Helper function to determine active class
  const isActive = (path) => location.pathname === path;
</script>

<div class="navbar-background">
  <nav>
      <a href="/" class="logo" on:click={() => navigate('/')}>
          <img src="/Logo.png" alt="Logo" />
      </a>

      <button class="{isActive('/') ? 'active' : ''}" on:click={() => navigate('/')}>Alle Filme</button>
      <button class="{isActive('/nowplaying') ? 'active' : ''}" on:click={() => navigate('/nowplaying')}>Programm</button>
      <button class="{isActive('/upcoming') ? 'active' : ''}" on:click={() => navigate('/upcoming')}>Upcoming</button>
      <button class="{isActive('/warenkorb') ? 'active' : ''}" on:click={() => navigate('/warenkorb')}>Warenkorb</button>

      {#if $authStore.isLoggedIn}
          <div class="profile-dropdown-container {isProfileDropdownOpen ? 'open' : ''}">
              <div class="profile-container" on:click={toggleProfileMenu}>
                  {#if $authStore.profile_image && $authStore.profile_image !== 'default.png'}
                      <img src={`/Profilbilder/${$authStore.profile_image}`} alt="Profilbild" class="profile-image" />
                  {:else}
                      <div class="profile-initials">{$authStore.initials}</div>
                  {/if}
              </div>
              <div class="profile-dropdown-menu">
                  <ul>
                      <li on:click={() => { navigate('/profile'); toggleProfileMenu(false); }}>Profil anzeigen</li>
                      <li on:click={() => { navigate('/einstellungen'); toggleProfileMenu(false); }}>Einstellungen</li>
                      {#if $authStore.isAdmin}
                          <li on:click={() => { navigate('/admin'); toggleProfileMenu(false); }}>Admin</li>
                      {/if}
                      <li on:click={() => { navigate('/bestellungen'); toggleProfileMenu(false); }}>Meine Bestellungen</li>
                      <li on:click={logout}>Abmelden</li>
                  </ul>
              </div>
          </div>
      {:else}
          <div class="dropdown-container {isLoginOpen ? 'open' : ''}">
              <button class="nav-button" on:click={() => toggleLoginDropdown(!isLoginOpen)}>Login</button>
              <div class="dropdown-menu">
                  {#if currentView === 'login'}
                      <form on:submit|preventDefault={onLoginSubmit}>
                          <input type="email" placeholder="E-Mail" bind:value={email} required />
                          <input type="password" placeholder="Passwort" bind:value={password} required />
                          <div class="login-button-container">
                              <button type="submit">Einloggen</button>
                          </div>
                          <div class="button-container">
                              <button type="button" class="secondary-button" on:click={() => currentView = 'register'}>Registrieren</button>
                              <button type="button" class="secondary-button" on:click={() => currentView = 'forgotPassword'}>Passwort vergessen?</button>
                          </div>
                      </form>
                  {:else if currentView === 'register'}
                      <div>
                          <input type="text" placeholder="Vorname" bind:value={firstName} />
                          <input type="text" placeholder="Nachname" bind:value={lastName} />
                          <input type="email" placeholder="E-Mail" bind:value={email} />
                          <input type="password" placeholder="Passwort" bind:value={password} />
                          <div class="login-button-container">
                              <button on:click={handleRegisterFn}>Registrieren</button>
                          </div>
                          <div class="button-container">
                              <button type="button" class="secondary-button" on:click={() => currentView = 'login'}>Zurück</button>
                          </div>
                      </div>
                  {:else if currentView === 'forgotPassword'}
                      <div>
                          <input type="email" placeholder="E-Mail-Adresse" bind:value={email} />
                          <div class="login-button-container">
                              <button on:click={handleForgotPasswordFn}>Link senden</button>
                          </div>
                          <div class="button-container">
                              <button type="button" class="secondary-button" on:click={() => currentView = 'login'}>Zurück</button>
                          </div>
                      </div>
                  {/if}
              </div>
          </div>
      {/if}
  </nav>
</div>

<style>
  @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
  @import url('https://use.fontawesome.com/releases/v5.15.4/css/all.css');

  /* Globale Stile */
  * {
      box-sizing: border-box;
  }

  html, body {
      margin: 0;
      padding: 0;
      width: 100%;
      height: 100%;
      font-family: 'Roboto', sans-serif;
      
      color: #fff;
      overflow-x: hidden;
  }

  /* Navbar-Hintergrund */
  .navbar-background {
    position: fixed;
    background: rgba(0, 0, 0, 0.2); /* 90% Deckkraft, leicht transparent */
    top: 0;
    left: 0;
    width: 100%;
    z-index: 1001;
    padding: 1rem 2rem;
    box-sizing: border-box;
}

 
  /* Navigation */
  nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
    width: 100%;
    z-index: 999999999;
    box-sizing: border-box;
  }

  /* Logo */
  .logo {
      display: flex;
      align-items: center;
      text-decoration: none;
      font-size: 1.2rem;
      font-weight: bold;
      transition: transform 0.3s ease;
      color: #2ecc71;
      text-shadow: 0 0 10px #2ecc71, 0 0 20px #2ecc71;
      z-index: 999999999;
  }

  .logo img {
      height: 60px;
      object-fit: contain;
      margin-right: 10px;
      z-index: 999999999;
  }

  .logo:hover {
      transform: scale(1.1);
  }

  /* Navigation Buttons */
  nav button {
      font-size: 1rem;
      font-weight: bold;
      background: transparent;
      color: #fff;
      border: 2px solid transparent;
      border-radius: 12px;
      padding: 0.6rem 1.2rem;
      cursor: pointer;
      transition: all 0.3s ease;
      margin: 0 0.5rem;
      text-shadow: 0 0 5px #fff;
      z-index: 999999999;
  }

  nav button:hover {
      border-color: #2ecc71;
      transform: scale(1.05);
      box-shadow: 0 0 10px #2ecc71;
  }

  /* Aktiver Navigationselement */
  nav button.active {
      border-color: #2ecc71;
      transform: scale(1.05);
      box-shadow: 0 0 10px #2ecc71;
  }

  /* Dropdown-Container */
  .dropdown-container, .profile-dropdown-container {
      position: relative;
      z-index: 999999999;
  }

  /* Dropdown-Menü */
  .dropdown-menu, .profile-dropdown-menu {
      position: absolute;
      top: calc(100% + 10px);
      right: 0;
      background: rgba(0, 0, 0, 0.8); /* Halbtransparente schwarze Hintergrundfarbe */
      background: linear-gradient(135deg, rgba(0,4,40,0.9), rgba(4, 29, 50, 0.9));
      border-radius: 12px;
      padding: 1rem;
      opacity: 0;
      transform: scaleY(0);
      transform-origin: top;
      transition: transform 0.3s ease, opacity 0.3s ease;
      z-index: 999999999;
      text-align: center;
      width: 320px;
      display: flex;
      flex-direction: column;
      align-items: center;
  }

  /* Öffne Dropdown-Menü bei Aktivierung */
  .dropdown-container.open .dropdown-menu,
  .profile-dropdown-container.open .profile-dropdown-menu {
      transform: scaleY(1);
      opacity: 1;
  }

  /* Dropdown-Inhalt */
  .dropdown-menu form,
  .dropdown-menu div {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      width: 100%;
  }

  /* Eingabefelder im Dropdown-Menü */
  .dropdown-menu input {
      background: rgba(255, 255, 255, 0.1); /* Halbtransparenter weißer Hintergrund */
      color: #fff; /* Weiße Schrift */
      border: 1px solid #2ecc71; /* Grüne Umrandung */
      border-radius: 8px;
      padding: 0.8rem;
      margin: 0.5rem 0;
      font-size: 1rem;
      text-align: center;
      box-shadow: 0 0 5px rgba(46, 204, 113, 0.5); /* Grüne Leuchten-Schatten */
      width: 100%; /* Eingabefelder füllen die gesamte Breite */
  }

  .dropdown-menu input:focus {
      border-color: #2ecc71;
      box-shadow: 0 0 10px #2ecc71;
      outline: none;
  }

  /* Login-Button Container */
  .login-button-container {
      display: flex;
      justify-content: center;
      width: 100%;
      margin-top: 0.5rem;
  }

  /* Login-Button-Stile */
  .dropdown-menu .login-button-container button {
      background: transparent; /* Transparenter Hintergrund */
      color: #fff; /* Weiße Schrift */
      border: 2px solid #2ecc71; /* Grüne, leuchtende Umrandung */
      border-radius: 12px; /* Abgerundete Ecken */
      padding: 0.8rem 1.2rem; /* Konsistente Padding */
      cursor: pointer;
      font-weight: bold;
      transition: all 0.3s ease;
      text-shadow: 0 0 5px #fff; /* Weißer Textschatten für Leuchteffekt */
      box-shadow: 0 0 5px rgba(46, 204, 113, 0.5); /* Grüne Leuchten-Schatten */
      width: 100%; /* Button füllt die gesamte Breite */
  }

  .dropdown-menu .login-button-container button:hover {
      border-color: #2ecc71; /* Grüne Umrandung bleibt bestehen */
      transform: scale(1.05); /* Leichtes Vergrößern */
      box-shadow: 0 0 15px #2ecc71; /* Intensiveres Leuchten */
      background: rgba(46, 204, 113, 0.1); /* Optional: Subtiles Hintergrundleuchten */
  }

  /* Sekundäre Buttons (z.B. Registrieren, Passwort vergessen) */
  .button-container {
      display: flex !important;
      justify-content: space-between !important; /* Platz zwischen den Buttons */
      gap: 0.5rem !important;
      margin-top: 1rem !important;
      width: 100%;
  }

  .dropdown-menu .button-container .secondary-button {
      background: transparent; /* Transparenter Hintergrund */
      color: #fff; /* Weiße Schrift */
      border: 2px solid #3498db; /* Blaue, leuchtende Umrandung */
      border-radius: 12px; /* Abgerundete Ecken */
      padding: 0.5rem 1rem; /* Konsistente Padding */
      cursor: pointer;
      font-weight: bold;
      transition: all 0.3s ease;
      text-shadow: 0 0 5px #fff; /* Weißer Textschatten für Leuchteffekt */
      box-shadow: 0 0 5px rgba(52, 152, 219, 0.5); /* Blaue Leuchten-Schatten */
      flex: 1; /* Jeder Button nimmt gleich viel Platz ein */
  }

  .dropdown-menu .button-container .secondary-button:first-child {
      margin-right: 0.25rem; /* Abstand zwischen den Buttons */
  }

  .dropdown-menu .button-container .secondary-button:last-child {
      margin-left: 0.25rem; /* Abstand zwischen den Buttons */
  }

  .dropdown-menu .button-container .secondary-button:hover {
      border-color: #3498db; /* Blaue Umrandung bleibt bestehen */
      transform: scale(1.05); /* Leichtes Vergrößern */
      box-shadow: 0 0 15px #3498db; /* Intensiveres Leuchten */
      background: rgba(52, 152, 219, 0.1); /* Optional: Subtiles Hintergrundleuchten */
  }

  /* Profil Dropdown Menü */
  .profile-dropdown-menu ul {
      list-style: none;
      margin: 0;
      padding: 0;
      width: 100%;
  }

  .profile-dropdown-menu li {
      padding: 0.8rem;
      cursor: pointer;
      border-radius: 8px;
      transition: background 0.3s, transform 0.2s;
      color: #fff;
  }

  .profile-dropdown-menu li:hover {
      background: #2ecc71;
      color: #000;
      transform: translateX(5px);
      font-weight: bold;
  }

  /* Profil-Container */
  .profile-container {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
  }

  .profile-image {
      width: 50px;
      height: 50px;
      border-radius: 50%;
      object-fit: cover;
      border: 2px solid #2ecc71;
  }

  .profile-initials {
      width: 50px;
      height: 50px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 50%;
      background: #2ecc71;
      color: #000;
      font-weight: bold;
      font-size: 1.2rem;
      box-shadow: 0 0 10px #2ecc71;
  }

  /* Fehlernachrichten */
  p.error {
      color: #e74c3c;
      text-align: center;
      font-weight: bold;
      margin-top: 20px;
  }

  /* Responsives Design */
  @media (max-width: 768px) {
      nav button {
          padding: 0.5rem 1rem;
          font-size: 0.9rem;
      }

      .dropdown-menu, .profile-dropdown-menu {
          width: 280px;
      }

      .logo img {
          height: 50px;
      }

      .profile-image, .profile-initials {
          width: 40px;
          height: 40px;
      }
  }

  /* Sicherstellen, dass alle Bilder nicht überlaufen */
  img {
      max-width: 100%;
      height: auto;
      display: block;
  }
</style>
