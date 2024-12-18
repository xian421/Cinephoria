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
    import Beschreibung from './routes/Beschreibung.svelte';
    import Sitzplan from './routes/Sitzplan.svelte';
    import Adminshowtime from './routes/Adminshowtime.svelte';
    import Register from './routes/Register.svelte';
    import Forgotpassword from "./routes/Forgotpassword.svelte";
    import Adminkinosaal from "./routes/Adminkinosaal.svelte";
    import Adminseats from "./routes/Adminseats.svelte";
    import Adminpreise from './routes/Adminpreise.svelte';
    import Buchung from './routes/Buchung.svelte';
    import Unauthorized from "./routes/Unauthorized.svelte";
    import Profile from "./routes/profile.svelte";
    import Warenkorb from './routes/Warenkorb.svelte';
    import Einstellung from "./routes/einstellung.svelte";
    import Admin from './routes/Admin.svelte';
    import Checkout from './routes/checkout.svelte';
    import Admindiscount from './routes/Admindiscount.svelte';
    import Bestellungen from './routes/Bestellungen.svelte';
    import Belohnung from './routes/Belohnung.svelte';
    import Leaderboard from './routes/leaderboard.svelte';
    import Bestelluebersicht from './routes/Bestelluebersicht.svelte';
    import Adminrewards from './routes/Adminrewards.svelte';
  
    // Import von Svelte Stores
    import { authStore, setAuth, updateAuth } from './stores/authStore.js';
  
    // Import der ProtectedRoute Komponente
    import ProtectedRoute from './components/ProtectedRoute.svelte';
    import Navbar from './components/Navbar.svelte';
    import Footer from './components/Footer.svelte';
  
    // State-Variablen
    let kontakt = [];
    let firstCinema = "";
  
    // Reaktive Zuweisung der Store-Werte
    $: isLoggedIn = $authStore.isLoggedIn;
    $: isAdmin = $authStore.isAdmin;
    $: userFirstName = $authStore.userFirstName;
    $: userLastName = $authStore.userLastName;
    $: initials = $authStore.initials;
    $: token = $authStore.token;
  
    // Ladezustand
    let isLoading = true;
  
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
    const handleLogin = async (email, password) => {
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
                localStorage.setItem('token', data.token);
                updateAuth(current => ({
                    isLoggedIn: true,
                    userFirstName: data.first_name,
                    userLastName: data.last_name,
                    initials: data.initials,
                    isAdmin: data.role.toLowerCase() === 'admin',
                    token: data.token, // Token im Store speichern
                }));
  
                const Toast = Swal.mixin({
                    toast: true,
                    position: "top-end",
                    showConfirmButton: false,
                    timer: 3000,
                    timerProgressBar: true,
                    didOpen: (toast) => {
                        toast.onmouseenter = Swal.stopTimer;
                        toast.onmouseleave = Swal.resumeTimer;
                    }
                });
                Toast.fire({
                    icon: "success",
                    title: "Erfolgreich angemeldet!"
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
  
        const storedToken = localStorage.getItem('token');
        if (storedToken) {
            try {
                const data = await validateToken(storedToken);
                console.log('Validate Token Response:', data);
  
                // Da validateToken keine isValid zurückgibt, setze den Auth-Zustand direkt
                updateAuth(current => ({
                    isLoggedIn: true,
                    userFirstName: data.first_name,
                    userLastName: data.last_name,
                    initials: data.initials,
                    isAdmin: data.role.toLowerCase() === 'admin',
                    token: storedToken,
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
    <Router>
        <Navbar 
            toggleLoginDropdown={toggleLoginDropdown} 
            toggleProfileMenu={toggleProfileMenu} 
            logout={logout} 
            isLoginOpen={isLoginOpen} 
            isProfileDropdownOpen={isProfileDropdownOpen} 
            handleLogin={handleLogin} 
            initials={initials} 
            isLoggedIn={isLoggedIn}
        />
  
        <!-- Routen -->
        <Route path="/" component={Home} />
        <Route path="/nowplaying" component={NowPlaying} />
        <Route path="/upcoming" component={Upcoming} />
        <Route path="/sitzplan" component={Sitzplan} />
        <Route path="/adminshowtime" component={Adminshowtime} />
        <Route path="/register" component={Register} />
        <Route path="/forgot-password" component={Forgotpassword} />
        <Route path="/checkout" component={Checkout} />
        
        <!-- Korrigierte Buchung Route -->
        <Route path="/buchung/:showtime_id" let:params>
            <Buchung showtime_id={Number(params.showtime_id)} />
        </Route>
  
        <Route path="/profile" component={Profile} />
        <Route path="/einstellungen" component={Einstellung} />
        <Route path="/warenkorb" component={Warenkorb} />
        <Route path="/bestellungen" component={Bestellungen} />
        <Route path="/belohnung" component={Belohnung} />
        <Route path="/leaderboard" component={Leaderboard} />
        <Route path="/bestelluebersicht" component={Bestelluebersicht} />



  
        <!-- Geschützte Admin-Routen mit ProtectedRoute -->
        <Route path="/adminkinosaal" let:params>
            <ProtectedRoute admin={true}>
                <Adminkinosaal />
            </ProtectedRoute>
        </Route>
        <Route path="/adminseats/:screenId" let:params>
            <ProtectedRoute admin={true}>
                <Adminseats screenId={params.screenId} />
            </ProtectedRoute>
        </Route>
  
        <Route path="/adminpreise" let:params>
            <ProtectedRoute admin={true}>
                <Adminpreise />
            </ProtectedRoute>
        </Route>
  
        <Route path="/admin" let:params>
            <ProtectedRoute admin={true}>
                <Admin />
            </ProtectedRoute>
        </Route>

        <Route path="/admindiscount" let:params>
            <ProtectedRoute admin={true}>
                <Admindiscount />
            </ProtectedRoute>
        </Route>

        <Route path="/adminrewards" let:params>
            <ProtectedRoute admin={true}>
                <Adminrewards />
            </ProtectedRoute>
        </Route>
  
        <Route path="/beschreibung/:id" let:params>
            <Beschreibung id={params.id} />
        </Route>        
        <Route path="/unauthorized" component={Unauthorized} />
        <Route path="*" component={NotFound} />
  
        <Footer firstCinema={firstCinema} />
    </Router>
  {/if}



  <style>
    :global(html, body) {
        font-family: 'Roboto', sans-serif;
        background: linear-gradient(135deg, #000428, #004e92);
        color: #fff;
        
        overflow-x: hidden; /* Verhindert horizontales Scrollen */
        position: relative; /* Notwendig für die Pseudo-Elemente */
    }
</style>
  