<!-- src/routes/AdminShowtime.svelte -->
<script>
    import { onMount } from "svelte";
    import { fetchNowPlayingMovies, fetchScreens, createShowtime, fetchShowtimes, updateShowtime } from '../services/api.js';
    import { get } from 'svelte/store';
    import { authStore } from '../stores/authStore.js';
    import Swal from 'sweetalert2';
    import { navigate } from "svelte-routing";

    let movies = [];
    let screens = [];
    let showtimes = [];

    let selectedMovieId = '';
    let selectedScreenId = '';
    let startTime = '';
    let endTime = '';

    let loading = true;
    let error = "";

    let editingShowtimeId = null;
    let editSelectedMovieId = '';
    let editSelectedScreenId = '';
    let editStartTime = '';
    let editEndTime = '';

    onMount(async () => {
        const auth = get(authStore);
        const token = auth.token;

        try {
            const [moviesData, screensData, showtimesData] = await Promise.all([
                fetchNowPlayingMovies(token),
                fetchScreens(token),
                fetchShowtimes(null, token)
            ]);

            movies = moviesData.results;
            screens = screensData.screens; // Annahme: Backend gibt { screens: [...] }
            showtimes = showtimesData.showtimes;
            console.log('Screens data richtig:', screens);
            console.log('Showtimes data:', showtimes);
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

            // Aktualisiere die Showtimes-Liste
            const updatedShowtimes = await fetchShowtimes(null, token);
            showtimes = updatedShowtimes.showtimes;

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

    async function handleEdit(showtime) {
        editingShowtimeId = showtime.showtime_id;
        editSelectedMovieId = showtime.movie_id;
        editSelectedScreenId = showtime.screen_id;
        editStartTime = showtime.start_time.slice(0,16); // Format für datetime-local
        editEndTime = showtime.end_time ? showtime.end_time.slice(0,16) : '';
    }

    async function handleUpdate(event) {
        event.preventDefault();

        if (!editSelectedMovieId || !editSelectedScreenId || !editStartTime) {
            Swal.fire({
                title: "Fehler",
                text: "Bitte alle erforderlichen Felder ausfüllen.",
                icon: "error",
                confirmButtonText: "OK",
            });
            return;
        }

        const updatedData = {
            movie_id: editSelectedMovieId,
            screen_id: editSelectedScreenId,
            start_time: editStartTime,
            end_time: editEndTime || null,
        };

        const auth = get(authStore);
        const token = auth.token;

        try {
            Swal.fire({
                title: 'Lädt...',
                text: 'Bitte warten, während der Showtime aktualisiert wird...',
                icon: 'info',
                showConfirmButton: false,
                didOpen: () => {
                    Swal.showLoading();
                },
            });

            await updateShowtime(editingShowtimeId, updatedData, token);

            Swal.fire({
                title: "Erfolgreich",
                text: "Showtime wurde aktualisiert.",
                icon: "success",
                timer: 2000,
                showConfirmButton: false,
            });

            // Reset Bearbeitungszustand
            editingShowtimeId = null;
            editSelectedMovieId = '';
            editSelectedScreenId = '';
            editStartTime = '';
            editEndTime = '';

            // Aktualisiere die Showtimes-Liste
            const updatedShowtimes = await fetchShowtimes(null, token);
            showtimes = updatedShowtimes.showtimes;

        } catch (err) {
            console.error("Fehler beim Aktualisieren des Showtimes:", err);
            Swal.fire({
                title: "Fehler",
                text: err.message || "Ein Fehler ist aufgetreten.",
                icon: "error",
                confirmButtonText: "OK",
            });
        }
    }

    function cancelEdit() {
        editingShowtimeId = null;
        editSelectedMovieId = '';
        editSelectedScreenId = '';
        editStartTime = '';
        editEndTime = '';
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
        background: linear-gradient(145deg, #f8f9fa, #ffffff);
        min-height: 100vh;
        color: #333;
    }

    h1, h2 {
        color: #1976d2;
        margin-bottom: 20px;
        text-align: center;
    }

    form {
        display: flex;
        flex-direction: column;
        gap: 15px;
        width: 100%;
        max-width: 400px;
        background: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
    }

    form label {
        display: flex;
        flex-direction: column;
        font-weight: bold;
        font-size: 1rem;
        margin-bottom: 5px;
    }

    form select, form input {
        padding: 10px;
        font-size: 1rem;
        border: 1px solid #ccc;
        border-radius: 8px;
        background: #f8f9fa;
        transition: all 0.3s ease;
    }

    form select:focus, form input:focus {
        border-color: #1976d2;
        box-shadow: 0 0 8px rgba(25, 118, 210, 0.3);
        outline: none;
    }

    form button {
        padding: 12px;
        font-size: 1rem;
        cursor: pointer;
        border: none;
        background: #1976d2;
        color: #ffffff;
        border-radius: 8px;
        transition: background-color 0.3s ease, transform 0.2s ease;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }

    form button:hover {
        background-color: #1565c0;
    }

    form button:active {
        transform: scale(0.98);
    }

    .back-button {
        margin-top: 20px;
        background-color: #757575;
        font-size: 1rem;
        padding: 10px 20px;
        border-radius: 8px;
        color: #fff;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }

    .back-button:hover {
        background-color: #616161;
    }

    .error {
        color: red;
        font-weight: bold;
        margin-bottom: 20px;
    }

    table {
        width: 100%;
        max-width: 800px;
        border-collapse: collapse;
        margin-top: 30px;
        background: #ffffff;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
    }

    th, td {
        border: 1px solid #ddd;
        padding: 12px;
        text-align: center;
        font-size: 1rem;
    }

    th {
        background-color: #1976d2;
        color: white;
        font-size: 1.1rem;
    }

    tbody tr:nth-child(even) {
        background-color: #f8f9fa;
    }

    tbody tr:hover {
        background-color: #f1f1f1;
    }

    .edit-form {
        display: flex;
        flex-direction: column;
        gap: 15px;
        width: 100%;
        max-width: 400px;
        margin: 20px auto;
        background: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
    }

    .edit-buttons {
        display: flex;
        gap: 10px;
        margin-top: 10px;
    }

    .cancel-button {
        background-color: #f44336;
        padding: 12px;
        font-size: 1rem;
        color: white;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }

    .cancel-button:hover {
        background-color: #d32f2f;
    }

    .edit-buttons button {
        flex: 1;
    }

    .edit-buttons button:hover {
        transform: none;
    }
</style>


<main>
    {#if error}
        <p class="error">{error}</p>
    {:else if loading}
        <p>Lade Daten...</p>
    {:else}
        <h2>Film Editor</h2>
        <form on:submit|preventDefault={handleSubmit}>
            <label>
                Film auswählen:
                <select bind:value={selectedMovieId} required>
                    <option value="" disabled>-- Film --</option>
                    {#each movies as movie}
                        <option value={movie.id}>{movie.title}</option>
                    {/each}
                </select>
            </label>

            <label>
                Kinosaal auswählen:
                <select bind:value={selectedScreenId} required>
                    <option value="" disabled>-- Kinosaal --</option>
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

        <h2>Film-Tabelle</h2>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Film</th>
                    <th>Kinosaal</th>
                    <th>Startzeit</th>
                    <th>Endzeit</th>
                    <th>Aktionen</th>
                </tr>
            </thead>
            <tbody>
                {#each showtimes as showtime}
                    <tr>
                        <td>{showtime.showtime_id}</td>
                        <td>
                            {#if editingShowtimeId === showtime.showtime_id}
                                <select bind:value={editSelectedMovieId} required>
                                    <option value="" disabled>-- Wähle einen Film --</option>
                                    {#each movies as movie}
                                        <option value={movie.id}>{movie.title}</option>
                                    {/each}
                                </select>
                            {:else}
                                {movies.find(movie => movie.id === showtime.movie_id)?.title || 'Unbekannt'}
                            {/if}
                        </td>
                        <td>
                            {#if editingShowtimeId === showtime.showtime_id}
                                <select bind:value={editSelectedScreenId} required>
                                    <option value="" disabled>-- Wähle einen Kinosaal --</option>
                                    {#each screens as screen}
                                        <option value={screen.screen_id}>Kinosaal: {screen.name}</option>
                                    {/each}
                                </select>
                            {:else}
                                {screens.find(screen => screen.screen_id === showtime.screen_id)?.name || 'Unbekannt'}
                            {/if}
                        </td>
                        <td>
                            {#if editingShowtimeId === showtime.showtime_id}
                                <input type="datetime-local" bind:value={editStartTime} required />
                            {:else}
                                {new Date(showtime.start_time).toLocaleString()}
                            {/if}
                        </td>
                        <td>
                            {#if editingShowtimeId === showtime.showtime_id}
                                <input type="datetime-local" bind:value={editEndTime} />
                            {:else}
                                {showtime.end_time ? new Date(showtime.end_time).toLocaleString() : '-'}
                            {/if}
                        </td>
                        <td>
                            {#if editingShowtimeId === showtime.showtime_id}
                                <div class="edit-buttons">
                                    <button type="button" on:click={handleUpdate}>Speichern</button>
                                    <button type="button" class="cancel-button" on:click={cancelEdit}>Abbrechen</button>
                                </div>
                            {:else}
                                <button type="button" on:click={() => handleEdit(showtime)}>Bearbeiten</button>
                            {/if}
                        </td>
                    </tr>
                {/each}
            </tbody>
        </table>

        <button class="back-button" on:click={goBack}>Zurück zu Überblick der Kinosäle</button>
    {/if}
</main>
