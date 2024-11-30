<!-- src/components/Navbar.svelte -->
<script>
    import { navigate } from "svelte-routing";
    export let currentPath;
    export let toggleLoginDropdown;
    export let toggleProfileMenu;
    export let logout;
    export let isLoginOpen;
    export let isProfileDropdownOpen;
    export let email;
    export let password;
    export let handleLogin;
    export let initials;
    export let isLoggedIn;

    // Optional: Debugging-Log
    console.log('Navbar received logout:', logout);
    console.log('Navbar received email:', email);
    console.log('Navbar received password:', password);
</script>

<style>
    /* Navbar-Stile */
    nav {
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: #ffffff;
      padding: 1rem 2rem;
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
      color: #333;
      font-size: 1.5rem;
      font-weight: bold;
      transition: transform 0.4s ease;
    }
  
    .logo:hover {
      transform: scale(1.05);
    }
  
    .logo img {
      height: 60px;
      width: auto;
      object-fit: contain;
    }
  
    /* Navigationsbuttons */
    .nav-buttons {
      display: flex;
      gap: 1rem;
    }

    button.nav-button {
      font-size: 1rem;
      font-weight: bold;
      color: #333;
      background: #ffffff;
      border: 2px solid transparent;
      border-radius: 8px;
      padding: 0.5rem 1rem;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
      cursor: pointer;
      transition: all 0.3s ease;
      min-width: 120px;
      text-align: center;
    }
  
    button.nav-button:hover {
      border-color: #1abc9c;
      transform: scale(1.05);
    }
  
    button.nav-button.active {
      color: #1abc9c;
      border-color: #1abc9c;
      transform: scale(1.05);
    }
  
    /* Dropdown-Stile */
    .dropdown-container {
      position: relative;
    }
  
    .dropdown-menu, .profile-dropdown-menu {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      justify-content: center;
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
  
    .dropdown-container.open .dropdown-menu,
    .profile-dropdown-container.open .profile-dropdown-menu {
      transform: scaleY(1);
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
      outline: none;
      border-color: #1abc9c;
      box-shadow: 0 0 4px rgba(26, 188, 156, 0.5);
    }
  
    .dropdown-menu button.submit-button {
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
      margin-top: 0.5rem;
    }
  
    .dropdown-menu button.submit-button:hover {
      background: #24b497;
    }
  
    .dropdown-menu .secondary-buttons {
      display: flex;
      justify-content: space-between;
      gap: 10px;
      margin-top: 0.5rem;
      width: 100%;
    }
  
    .dropdown-menu .secondary-buttons button {
      background: none;
      border: none;
      color: #007bff;
      cursor: pointer;
      font-size: 0.9rem;
      padding: 0;
    }
  
    /* Profil-Dropdown-Stile */
    .profile-container {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      font-size: 1rem;
      font-weight: bold;
      color: #333;
      transition: all 0.3s ease;
      background: none;
      border: none;
      padding: 0;
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
      background-color: #e74c3c; /* Rotes Design */
      color: white;
      font-size: 1rem;
      font-weight: bold;
    }
  
    .profile-dropdown-menu ul {
      list-style: none;
      padding: 0;
      margin: 0;
      width: 100%;
    }
  
    .profile-dropdown-menu li {
      width: 100%;
      padding: 0.8rem;
      font-size: 1rem;
      color: #333;
      cursor: pointer;
      transition: background-color 0.3s ease;
      border: none;
      background: none;
      text-align: left;
    }
  
    .profile-dropdown-menu li:hover {
      background-color: #f0f0f0;
      border-radius: 8px;
    }
</style>

<nav>
    <!-- Logo -->
    <a href="/" class="logo" on:click={() => navigate('/')}>
        <img src="/Logo.png" alt="Logo" />
    </a>

    <!-- Navigationsbuttons -->
    <div class="nav-buttons">
        <button
            class="nav-button {currentPath === '/' ? 'active' : ''}"
            on:click={() => navigate('/')}
        >
            Alle Filme
        </button>
        <button
            class="nav-button {currentPath === '/nowplaying' ? 'active' : ''}"
            on:click={() => navigate('/nowplaying')}
        >
            Programm
        </button>
        <button
            class="nav-button {currentPath === '/upcoming' ? 'active' : ''}"
            on:click={() => navigate('/upcoming')}
        >
            Upcoming
        </button>
        <button
            class="nav-button {currentPath === '/sitzplan' ? 'active' : ''}"
            on:click={() => navigate('/sitzplan')}
        >
            Sitzplan
        </button>
    </div>

    <!-- Benutzerbereich -->
    {#if isLoggedIn}
        <!-- Profil-Dropdown -->
        <div class="dropdown-container profile-dropdown-container {isProfileDropdownOpen ? 'open' : ''}">
            <!-- Verwende einen Button für die Profil-Initialen -->
            <button class="profile-container" on:click={toggleProfileMenu} aria-haspopup="true" aria-expanded={isProfileDropdownOpen}>
                <div class="profile-initials" aria-label="Benutzerprofil">{initials}</div>
            </button>
            <div class="profile-dropdown-menu">
                <ul>
                    <li><button on:click={() => navigate('/profil')}>Profil anzeigen</button></li>
                    <li><button on:click={() => navigate('/einstellungen')}>Einstellungen</button></li>
                    <li><button on:click={logout}>Abmelden</button></li>
                </ul>
            </div>
        </div>
    {:else}
        <!-- Login-Dropdown -->
        <div class="dropdown-container {isLoginOpen ? 'open' : ''}">
            <button on:click={toggleLoginDropdown} aria-haspopup="true" aria-expanded={isLoginOpen}>Login</button>
            <div class="dropdown-menu">
                <form on:submit|preventDefault={handleLogin}>
                    <input type="email" placeholder="E-Mail" bind:value={email} required aria-label="E-Mail" />
                    <input type="password" placeholder="Passwort" bind:value={password} required aria-label="Passwort" />
                    <button type="submit" class="submit-button">Einloggen</button>
                    <div class="secondary-buttons">
                        <button type="button" on:click={() => navigate('/register')}>Stattdessen Registrieren</button>
                        <button type="button" on:click={() => navigate('/forgot-password')}>Passwort vergessen?</button>
                    </div>
                </form>
            </div>
        </div>
    {/if}
</nav>
