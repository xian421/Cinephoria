<!-- src/routes/AdminShowtime.svelte -->
<script>
    import { onMount } from "svelte";
    import { fetchNowPlayingMovies, fetchScreens, createShowtime } from '../services/api.js';
    import { get } from 'svelte/store';
    import { authStore } from '../stores/authStore.js';
    import Swal from 'sweetalert2';
    import { navigate } from "svelte-routing";

    let movies = [];
    let screens = [];

    let selectedMovieId = '';
    let selectedScreenId = '';
    let startTime = '';
    let endTime = '';

    let loading = true;
    let error = "";

    onMount(async () => {
        const auth = get(authStore);
        const token = auth.token;

        try {
            const [moviesData, screensData] = await Promise.all([
                fetchNowPlayingMovies(token),
                fetchScreens(token)
            ]);

            movies = moviesData.results;
            screens = screensData.screens; // Annahme: Backend gibt { screens: [...] }
            console.log('Screens data richtig:', screens);
        } catch (err) {
            console.error("Fehler beim Laden der Daten:", err);
            error = err.message || "Fehler beim Laden der Daten.";
        } finally {
            loading = false;
        }
    });

    async function handleSubmit(event) {
        event.preventDefault();

        if (!selectedMovieId || !selectedScreenId || !startTime) {
            Swal.fire({
                title: "Fehler",
                text: "Bitte alle erforderlichen Felder ausfüllen.",
                icon: "error",
                confirmButtonText: "OK",
            });
            return;
        }

        const showtimeData = {
            movie_id: selectedMovieId,
            screen_id: selectedScreenId,
            start_time: startTime,
            end_time: endTime || null, // Optional
        };

        const auth = get(authStore);
        const token = auth.token;

        try {
            Swal.fire({
                title: 'Lädt...',
                text: 'Bitte warten, während der Showtime erstellt wird...',
                icon: 'info',
                showConfirmButton: false,
                didOpen: () => {
                    Swal.showLoading();
                },
            });

            await createShowtime(showtimeData, token);

            Swal.fire({
                title: "Erfolgreich",
                text: "Showtime wurde erstellt.",
                icon: "success",
                timer: 2000,
                showConfirmButton: false,
            });

            // Reset Formular
            selectedMovieId = '';
            selectedScreenId = '';
            startTime = '';
            endTime = '';

        } catch (err) {
            console.error("Fehler beim Erstellen des Showtimes:", err);
            Swal.fire({
                title: "Fehler",
                text: err.message || "Ein Fehler ist aufgetreten.",
                icon: "error",
                confirmButtonText: "OK",
            });
        }
    }

    function goBack() {
        navigate('/adminkinosaal'); // Passe den Pfad entsprechend an
    }
</script>

<style>
    main {
        display: flex;
        flex-direction: column;
        align-items: center;
        font-family: Arial, sans-serif;
        padding: 20px;
    }

    form {
        display: flex;
        flex-direction: column;
        gap: 15px;
        width: 300px;
    }

    label {
        display: flex;
        flex-direction: column;
        font-weight: bold;
    }

    select, input {
        padding: 8px;
        font-size: 14px;
        margin-top: 5px;
    }

    button {
        padding: 10px;
        font-size: 16px;
        cursor: pointer;
        border: none;
        background-color: #1976d2;
        color: white;
        border-radius: 5px;
        transition: background-color 0.3s;
    }

    button:hover {
        background-color: #1565c0;
    }

    .error {
        color: red;
        font-weight: bold;
    }

    .back-button {
        margin-top: 20px;
        background-color: #757575;
    }

    .back-button:hover {
        background-color: #616161;
    }
</style>

<main>
    {#if error}
        <p class="error">{error}</p>
    {:else if loading}
        <p>Lade Daten...</p>
    {:else}
        <h1>Showtime hinzufügen</h1>
        <form on:submit|preventDefault={handleSubmit}>
            <label>
                Film auswählen:
                <select bind:value={selectedMovieId} required>
                    <option value="" disabled>-- Wähle einen Film --</option>
                    {#each movies as movie}
                        <option value={movie.id}>{movie.title}</option>
                    {/each}
                </select>
            </label>

            <label>
                Kinosaal auswählen:
                <select bind:value={selectedScreenId} required>
                    <option value="" disabled>-- Wähle einen Kinosaal --</option>
                    {#each screens as screen}
                        <option value={screen.screen_id}>Kinosaal: {screen.name}</option>
                    {/each}
                </select>
            </label>

            <label>
                Startzeit:
                <input type="datetime-local" bind:value={startTime} required />
            </label>

            <label>
                Endzeit (optional):
                <input type="datetime-local" bind:value={endTime} />
            </label>

            <button type="submit">Showtime hinzufügen</button>
        </form>

        <button class="back-button" on:click={goBack}>Zurück zu Überblick der Kinosäle</button>
    {/if}
</main>
