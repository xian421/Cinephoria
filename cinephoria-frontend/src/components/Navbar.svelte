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

    /* Profil-Dropdown-Stile */
    .profile-dropdown-container {
        position: relative;
    }

    .profile-dropdown-menu {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        position: absolute;
        top: calc(100% + 10px);
        right: 0;
        background: rgba(255, 255, 255, 0.95);
        padding: 1rem;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        border-radius: 12px;
        z-index: 1000;
        width: 220px;
        opacity: 0;
        transform: translateY(-10px);
        pointer-events: none;
        transition: opacity 0.3s ease, transform 0.3s ease;
    }

    .profile-dropdown-container.open .profile-dropdown-menu {
        opacity: 1;
        transform: translateY(0);
        pointer-events: auto;
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
        border-radius: 8px;
        transition: background-color 0.3s ease, transform 0.3s ease;
    }

    .profile-dropdown-menu li:hover {
        background-color: #f9f9f9;
        transform: translateX(5px);
    }

    .profile-container {
        display: flex;
        align-items: center;
        gap: 10px;
        cursor: pointer;
        font-size: 1rem;
        font-weight: bold;
        color: black;
        transition: transform 0.3s ease;
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
        background: linear-gradient(135deg, #1abc9c, #3498db);
        color: white;
        font-size: 20px;
        font-weight: bold;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
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
            <button
                type="button"
                class="profile-container"
                on:click={toggleProfileMenu}
                aria-label="Profil-Optionen anzeigen"
            >
                <div class="profile-initials">{initials || 'NA'}</div>
            </button>
            <div class="profile-dropdown-menu">
                <ul>
                    <li><button type="button" on:click={() => navigate('/profil')}>Profil anzeigen</button></li>
                    <li><button type="button" on:click={() => navigate('/einstellungen')}>Einstellungen</button></li>
                    <li><button type="button" on:click={logout}>Abmelden</button></li>
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
                </form>
            </div>
        </div>
    {/if}
</nav>
