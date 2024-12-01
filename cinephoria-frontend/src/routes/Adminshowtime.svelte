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

    table {
        width: 80%;
        border-collapse: collapse;
        margin-top: 30px;
    }

    th, td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: center;
    }

    th {
        background-color: #f2f2f2;
    }

    .edit-form {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin-top: 20px;
        width: 300px;
    }

    .edit-buttons {
        display: flex;
        gap: 10px;
    }

    .cancel-button {
        background-color: #f44336;
    }

    .cancel-button:hover {
        background-color: #d32f2f;
    }
</style>

<main>
    {#if error}
        <p class="error">{error}</p>
    {:else if loading}
        <p>Lade Daten...</p>
    {:else}
        <h1>Showtime hinzufügen und bearbeiten</h1>
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

        <h2>Bestehende Showtimes</h2>
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
