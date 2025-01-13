<!-- src/App.svelte -->
<script>
    import { onMount } from 'svelte';
    import { Router, Route, navigate } from 'svelte-routing';

    import Home from './routes/Home.svelte';
    import NowPlaying from './routes/Nowplaying.svelte';
    import Upcoming from './routes/Upcoming.svelte';
    import NotFound from './routes/Notfound.svelte';
    import Beschreibung from './routes/Beschreibung.svelte';
    import Sitzplan from './routes/Sitzplan.svelte';
    import Adminshowtime from './routes/Adminshowtime.svelte';
    import Register from './routes/Register.svelte';
    import Forgotpassword from './routes/Forgotpassword.svelte';
    import Adminkinosaal from './routes/Adminkinosaal.svelte';
    import Adminseats from './routes/Adminseats.svelte';
    import Adminpreise from './routes/Adminpreise.svelte';
    import Buchung from './routes/Buchung.svelte';
    import Unauthorized from './routes/Unauthorized.svelte';
    import Profile from './routes/profile.svelte';
    import Warenkorb from './routes/Warenkorb.svelte';
    import Einstellung from './routes/einstellung.svelte';
    import Admin from './routes/Admin.svelte';
    import Checkout from './routes/checkout.svelte';
    import Admindiscount from './routes/Admindiscount.svelte';
    import Bestellungen from './routes/Bestellungen.svelte';
    import Belohnung from './routes/Belohnung.svelte';
    import Leaderboard from './routes/leaderboard.svelte';
    import Bestelluebersicht from './routes/Bestelluebersicht.svelte';
    import Adminrewards from './routes/Adminrewards.svelte';
    import Ticketanzeige from './routes/Ticketanzeige.svelte';
    import Viewbooking from './routes/Viewbooking.svelte';
    import Snacksanddrinks from './routes/snacksanddrinks.svelte';
    import Mitarbeiter from './routes/mitarbeiter.svelte';
    import Mitarbeiterkino from './routes/mitarbeiterkino.svelte';
    import Mitarbeitersupermarkt from './routes/mitarbeitersupermarkt.svelte';
    import Mitarbeiterscannen from './routes/mitarbeiterscannen.svelte';
    import './global.css';
    

    import { loadProfile } from './stores/profileStore.js';
    import { authStore, setAuth, updateAuth } from './stores/authStore.js';
    import { showSuccessToast, showErrorAlert } from './utils/notifications.js';
    import Navbar from './components/Navbar.svelte';
    import Footer from './components/Footer.svelte';
    import ProtectedRoute from './components/ProtectedRoute.svelte';

    import { login, validateToken, fetchCinemas } from './services/api.js';
    import { params } from 'svelte-spa-router';

    const minimalRoutes = ['/mitarbeiter', '/mitarbeiter/kino', '/mitarbeiter/supermarkt', '/mitarbeiter/scannen'];

    $: isMinimalRoute = minimalRoutes.includes(window.location.pathname);

    $: {
        document.body.classList.toggle('minimal-route', isMinimalRoute);
    }


    let cinemas = [];
    let firstCinema = '';
    let isLoading = true;
    let isLoginOpen = false;
    let isProfileDropdownOpen = false;

    const toggleLoginDropdown = () => {
        isLoginOpen = !isLoginOpen;
    };

    const toggleProfileMenu = () => {
        isProfileDropdownOpen = !isProfileDropdownOpen;
    };

    const handleLogin = async (email, password) => {
        if (!email || !password) {
            showErrorAlert("Bitte E-Mail und Passwort eingeben!");
            return;
        }

        try {
            const data = await login(email, password);
            if (data.token) {
                localStorage.setItem('token', data.token);
                updateAuth(current => ({
                    ...current,
                    isLoggedIn: true,
                    token: data.token 
                }));

                await loadProfile();
                showSuccessToast("Erfolgreich angemeldet!");
            } else {
                showErrorAlert(data.error || "Unbekannter Fehler");
            }
        } catch (error) {
            showErrorAlert(error.message || "Ein Fehler ist aufgetreten.");
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
        showSuccessToast("Du wurdest erfolgreich abgemeldet.");
        navigate('/');
    };

    onMount(async () => {
        try {
            const data = await fetchCinemas();
            cinemas = data.cinemas;
            if (cinemas && cinemas.length > 0) {
                firstCinema = cinemas[0];
            }
        } catch (error) {
            console.error('Fehler beim Laden der Kinos:', error);
        }

        const storedToken = localStorage.getItem('token');
        if (storedToken) {
            try {
                await validateToken(storedToken);
                updateAuth(current => ({
                    ...current,
                    isLoggedIn: true,
                    token: storedToken,
                }));
                await loadProfile();
            } catch (error) {
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

<slot></slot>

{#if isLoading}
  <p>Loading...</p>
{:else}
  <Router>
    
    {#if !isMinimalRoute}
      <Navbar 
          toggleLoginDropdown={toggleLoginDropdown} 
          toggleProfileMenu={toggleProfileMenu} 
          logout={logout} 
          isLoginOpen={isLoginOpen} 
          isProfileDropdownOpen={isProfileDropdownOpen} 
          handleLogin={handleLogin} 
          initials={$authStore.initials} 
          isLoggedIn={$authStore.isLoggedIn}
      />
    {/if}

      <!-- Routen -->
      <Route path="/" component={Home} />
      <Route path="/nowplaying" component={NowPlaying} />
      <Route path="/upcoming" component={Upcoming} />
      <Route path="/sitzplan" component={Sitzplan} />
      <Route path="/adminshowtime" component={Adminshowtime} />
      <Route path="/register" component={Register} />
      <Route path="/forgot-password" component={Forgotpassword} />
      <Route path="/checkout" component={Checkout} />
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
      <Route path="/ticketanzeige/:token" let:params>
        <Ticketanzeige token={params.token} />
      </Route>
      <Route path="/viewbooking/:token" let:params>
        <Viewbooking token={params.token} />
        </Route>
    


      <!-- WICHTIG: Neue Route für Snacks & Drinks -->
      <Route path="/snacksanddrinks" component={Snacksanddrinks} />



      <!-- Geschützte Admin-Routen -->
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

      {#if !isMinimalRoute}
        <Footer firstCinema={firstCinema} />
      {/if}

<!-- Supermarkt -->
        <Route path="/mitarbeiter" let:params>
            <ProtectedRoute admin={true}>
                <Mitarbeiter />
            </ProtectedRoute>
        </Route>
        <Route path="/mitarbeiter/kino" let:params>
            <ProtectedRoute admin={true}>
                <Mitarbeiterkino />
            </ProtectedRoute>
        </Route>
        <Route path="/mitarbeiter/supermarkt" let:params>
            <ProtectedRoute admin={true}>
                <Mitarbeitersupermarkt />
            </ProtectedRoute>
        </Route>         
        <Route path="/mitarbeiter/scannen" let:params>
            <ProtectedRoute admin={true}>
                <Mitarbeiterscannen />
            </ProtectedRoute>
        </Route>
  </Router>
{/if}
