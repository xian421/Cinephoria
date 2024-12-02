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
                    <li on:click={() => navigate('/adminkinosaal')}>Kinosaal</li>
                    <li on:click={() => navigate('/adminshowtime')}>Vorstellung erstellen</li>
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
                    <div class="button-container" style="display: flex; justify-content: space-between; gap: 10px; margin-top: 10px;">
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

