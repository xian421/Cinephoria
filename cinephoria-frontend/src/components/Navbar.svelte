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
  
  // Zustandsvariable für die aktuelle Ansicht im Dropdown
  let currentView = 'login'; // 'login', 'register', 'forgotPassword'

  const onLoginSubmit = async () => {
    if (!email || !password) {
      Swal.fire("Fehler", "Bitte gib E-Mail und Passwort ein.", "error");
      return;
    }
    await handleLogin(email, password);
    // Felder zurücksetzen und Dropdown schließen
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
        // Zurück auf Login-Ansicht
        currentView = 'login';
        // Felder leeren
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
        email = ""; // Eingabefeld leeren
        currentView = 'login';
      } else {
        Swal.fire("Fehler", data.error || "Ein Fehler ist aufgetreten.", "error");
      }
    } catch (error) {
      Swal.fire("Fehler", "Es konnte keine Verbindung zum Server hergestellt werden.", "error");
    }
  };

  const location = useLocation();
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

    width: 1200px;
    margin: 0 auto;
  }

  /* Logo */
  .logo {
    display: flex;
    align-items: center;
    text-decoration: none;
    font-size: 1.2rem;
    font-weight: bold;
    transition: transform 0.3s ease;
  }

  .logo img {
    height: 60px;
    object-fit: contain;
  }

  .logo:hover {
    transform: scale(1.1);
  }

  /* Buttons */
  button {
    font-size: 1.1rem;
    font-weight: bold;
    background: #ffffff;
    border: 2px solid transparent;
    border-radius: 12px;
    padding: 0.8rem 1.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    cursor: pointer;
    transition: all 0.3s ease;
    min-width: 160px;
  }

  button:hover {
    border-color: #1abc9c;
    transform: scale(1.05);
  }

  button.active {
    color: #1abc9c;
    border-color: #1abc9c;
    transform: scale(1.05);
  }

  /* Dropdown Container */
  

  /* Dropdown Menü */
  .dropdown-menu, .profile-dropdown-menu {
    position: absolute;
    top: calc(100% + 10px);
    right: 0;
    background: #ffffff;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    border-radius: 12px;
    width: 300px;
    padding: 1rem;
    opacity: 0;
    transform: scaleY(0);
    transform-origin: top;
    transition: transform 0.3s ease, opacity 0.3s ease;
    z-index: 1000;
    text-align: center;
  }

  .dropdown-container.open .dropdown-menu,
  .profile-dropdown-container.open .profile-dropdown-menu {
    transform: scaleY(1);
    opacity: 1;
  }

  .dropdown-menu input {
    width: 100%;
    padding: 0.8rem;
    margin: 0.5rem 0;
    border: 1px solid #ccc;
    border-radius: 8px;
    font-size: 1rem;
    box-sizing: border-box;
  }

  .dropdown-menu input:focus {
    border-color: #1abc9c;
    box-shadow: 0 0 4px rgba(26, 188, 156, 0.5);
    outline: none;
  }

  .dropdown-menu button {
    background: #3498db;
    color: #ffffff;
    padding: 0.8rem;
    border-radius: 12px;
    border: none;
    cursor: pointer;
    width: 100%;
    transition: background-color 0.3s;
  }

  .dropdown-menu button:hover {
    background: #1abc9c;
  }

  .profile-dropdown-menu ul {
    list-style: none;
    margin: 0;
    padding: 0;
  }

  .profile-dropdown-menu li {
    padding: 0.8rem;
    cursor: pointer;
    border-radius: 8px;
    transition: background 0.3s, transform 0.2s;
  }

  .profile-dropdown-menu li:hover {
    background: #f1f1f1;
    transform: translateX(5px);
  }

  /* Profil Container */
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
  }

  .profile-initials {
    width: 50px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: #3498db;
    color: white;
    font-weight: bold;
    font-size: 1.2rem;
  }

  .button-container {
  display: flex !important; 
  justify-content: center !important; /* Zentriert die Buttons */
  gap: 1rem !important; /* Abstand zwischen den Buttons */
  margin-top: 1rem !important; /* Abstand nach oben */
}

.secondary-button {
  background-color: #ffffff !important; 
  color: #3498db !important; 
  font-size: 0.9rem !important;
  font-weight: 600 !important;
  box-shadow: black;
  border-radius: 8px!important; 
  padding: 0.5rem 1rem!important; 
  cursor: pointer!important;
  transition: all 0.3s ease!important;
  text-align: center!important;
  min-width: 120px!important; 
  border: 2px solid #ffffff !important;
}

.secondary-button:hover {
  border-color: #1abc9c !important;
  

  transform: scale(1.05)!important; /* Leichte Vergrößerung */
}



  </style>

<nav>
  <!-- Logo -->
  <a href="/" class="logo" on:click={() => navigate('/')}>
      <img src="/Logo.png" alt="Logo" />
  </a>

  <!-- Navigationsbuttons -->
  <button class="{location.pathname === '/' ? 'active' : ''}" on:click={() => navigate('/')}>Alle Filme</button>
  <button class="{location.pathname === '/nowplaying' ? 'active' : ''}" on:click={() => navigate('/nowplaying')}>Programm</button>
  <button class="{location.pathname === '/upcoming' ? 'active' : ''}" on:click={() => navigate('/upcoming')}>Upcoming</button>
  <button class="{location.pathname === '/warenkorb' ? 'active' : ''}" on:click={() => navigate('/warenkorb')}>Warenkorb</button>

  <!-- Benutzerbereich -->
  {#if $authStore.isLoggedIn}
      <!-- Profil-Dropdown -->
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
      <!-- Login-Dropdown mit Toggle zwischen Ansichten -->
      <div class="dropdown-container {isLoginOpen ? 'open' : ''}">
          <button on:click={() => toggleLoginDropdown(!isLoginOpen)}>Login</button>
          <div class="dropdown-menu">
            {#if currentView === 'login'}
              <!-- Login-Formular -->
              <form on:submit|preventDefault={onLoginSubmit}>
                <input type="email" placeholder="E-Mail" bind:value={email} required />
                <input type="password" placeholder="Passwort" bind:value={password} required />
                <button type="submit">Einloggen</button>
                <div class="button-container">
                  <button type="button" class="secondary-button" on:click={() => currentView = 'register'}>Registrieren</button>
                  <button type="button" class="secondary-button" on:click={() => currentView = 'forgotPassword'}>Passwort vergessen?</button>
                </div>
              </form>
            {:else if currentView === 'register'}
              <!-- Registrieren-Formular -->
              <div>
                <input type="text" placeholder="Vorname" bind:value={firstName} />
                <input type="text" placeholder="Nachname" bind:value={lastName} />
                <input type="email" placeholder="E-Mail" bind:value={email} />
                <input type="password" placeholder="Passwort" bind:value={password} />
                <button on:click={handleRegisterFn}>Registrieren</button>
                <div class="button-container">
                  <button type="button" class="secondary-button" on:click={() => currentView = 'login'}>Zurück</button>
                </div>
              </div>
            {:else if currentView === 'forgotPassword'}
              <!-- Passwort vergessen-Formular -->
              <div>
                <input type="email" placeholder="E-Mail-Adresse" bind:value={email} />
                <button on:click={handleForgotPasswordFn}>Link zum Zurücksetzen senden</button>
                <div class="button-container">
                  <button type="button" class="secondary-button" on:click={() => currentView = 'login'}>Zurück</button>
                </div>
              </div>
            {/if}
          </div>
      </div>
  {/if}
</nav>