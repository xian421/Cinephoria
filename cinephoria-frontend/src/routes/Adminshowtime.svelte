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
        navigate('/admin'); // Passe den Pfad entsprechend an
    }
</script>

<style>


main {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 40px;
    max-width: 1200px;
    margin: 0 auto;
}

h1, h2 {
    color: #2ecc71;
    text-shadow: 0 0 20px #2ecc71, 0 0 40px #2ecc71;
    margin-bottom: 40px;
    font-size: 2rem;
    animation: glow 2s infinite alternate;
}

@keyframes glow {
  from {
    text-shadow: 0 0 10px #2ecc71, 0 0 20px #2ecc71;
  }
  to {
    text-shadow: 0 0 20px #2ecc71, 0 0 40px #2ecc71;
  }
}

/* Form Styling */
form {
    background: rgba(0,0,0,0.4);
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 0 20px rgba(0,0,0,0.5);
    width: 100%;
    max-width: 400px;
    color: #fff;
    font-weight: bold;
}

form label {
    margin-bottom: 10px;
    text-shadow: 0 0 10px #2ecc71;
    font-size: 1.1rem;
}

form select, form input {
    width: 100%;
    padding: 10px;
    font-size: 1rem;
    border-radius: 8px;
    border: none;
    background: #000;
    color: #2ecc71;
    margin-top: 5px;
    box-shadow: inset 0 0 10px #2ecc71;
    transition: box-shadow 0.3s;
}

form select:hover, form input:hover,
form select:focus, form input:focus {
    box-shadow: inset 0 0 15px #2ecc71;
    outline: none;
}

form button {
    background-color: #2ecc71;
    color: #000;
    border: none;
    padding: 12px;
    border-radius: 8px;
    font-size: 1rem;
    cursor: pointer;
    box-shadow: 0 0 10px #2ecc71;
    transition: background-color 0.3s, transform 0.3s;
    margin-top: 10px;
    width: 100%;
    font-weight: bold;
    text-shadow: 0 0 10px #000;
}

form button:hover {
    background-color: #27ae60;
    transform: translateY(-3px) scale(1.05);
    box-shadow: 0 0 15px #27ae60;
}

/* Error Text */
.error {
    color: #e74c3c;
    font-weight: bold;
    margin-bottom: 20px;
    text-shadow: 0 0 10px #e74c3c;
}

/* Table Styling */
table {
    width: 100%;
    max-width: 800px;
    border-collapse: collapse;
    margin-top: 30px;
    background: rgba(0,0,0,0.4);
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 0 20px rgba(0,0,0,0.5);
    color: #fff;
}

th, td {
    padding: 12px;
    text-align: center;
    font-size: 1rem;
    border-bottom: 1px solid #2ecc71;
    text-shadow: 0 0 5px #2ecc71;
}

th {
    background-color: #000;
    font-size: 1.1rem;
    color: #2ecc71;
    border-bottom: 2px solid #2ecc71;
}

tbody tr:nth-child(even) {
    background-color: rgba(42, 42, 42, 0.3);
}

tbody tr:hover {
    background-color: rgba(46, 204, 113, 0.1);
    cursor: pointer;
    box-shadow: inset 0 0 10px #2ecc71;
}

/* Edit Buttons */
.edit-buttons {
    display: flex;
    gap: 10px;
    margin-top: 10px;
}

.edit-buttons button {
    flex: 1;
    background-color: #2ecc71;
    color: #000;
    border: none;
    padding: 10px;
    border-radius: 8px;
    transition: background-color 0.3s, transform 0.3s;
    box-shadow: 0 0 10px #2ecc71;
    font-weight: bold;
    text-shadow: 0 0 10px #000;
}

.edit-buttons button:hover {
    background-color: #27ae60;
    transform: translateY(-3px) scale(1.05);
}

.cancel-button {
    background-color: #e74c3c !important;
    box-shadow: 0 0 10px #e74c3c;
}

.cancel-button:hover {
    background-color: #c0392b !important;
}

/* Back Button */
.back-button {
    margin-top: 20px;
    background-color: #2ecc71;
    font-size: 1rem;
    padding: 10px 20px;
    border-radius: 8px;
    color: #000;
    cursor: pointer;
    box-shadow: 0 0 10px #2ecc71;
    transition: background-color 0.3s, transform 0.3s;
    font-weight: bold;
    text-shadow: 0 0 10px #000;
}

.back-button:hover {
    background-color: #27ae60;
    transform: translateY(-3px) scale(1.05);
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

        <button class="back-button" on:click={goBack}>Zurück zum Adminbereich</button>
    {/if}
</main>
