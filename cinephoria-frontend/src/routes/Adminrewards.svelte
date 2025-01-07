<script>
    import { onMount } from 'svelte';
    import Swal from 'sweetalert2';
    import { get } from 'svelte/store';
    import { authStore } from '../stores/authStore.js';
    import { fetchRewards, addReward, updateReward, deleteReward } from '../services/api.js';
    import { navigate } from 'svelte-routing';


    let rewards = [];
    let isLoading = true;
    let error = null;

    // Neue Reward-Daten
    let newRewardTitle = '';
    let newRewardPoints = '';
    let newRewardDescription = '';
    // Entfernt: let newRewardImage = '';

    onMount(async () => {
        isLoading = true;
        const token = get(authStore).token;
        try {
            const fetchedRewards = await fetchRewards(token);
            console.log('Fetched Rewards:', fetchedRewards);
            rewards = fetchedRewards;
            isLoading = false;
        } catch (err) {
            console.error('Fehler beim Laden der Rewards:', err);
            error = err.message || 'Fehler beim Laden der Daten.';
            isLoading = false;
        }
    });

    // Funktion zum Hinzufügen einer neuen Reward
    async function handleAddReward() {
        const token = get(authStore).token;

        // Umwandlung in Strings vor trim()
        const titleStr = String(newRewardTitle);
        const pointsStr = String(newRewardPoints);

        if (!titleStr.trim() || !pointsStr.trim()) {
            Swal.fire({
                title: 'Fehler',
                text: 'Bitte geben Sie einen Titel und Punkte für die Belohnung ein.',
                icon: 'error',
                confirmButtonText: 'OK',
            });
            return;
        }

        const points = parseInt(pointsStr, 10);
        if (isNaN(points)) {
            Swal.fire({
                title: 'Fehler',
                text: 'Bitte geben Sie eine gültige Zahl für die Punkte ein.',
                icon: 'error',
                confirmButtonText: 'OK',
            });
            return;
        }

        try {
            await addReward(token, titleStr.trim(), points, newRewardDescription /*, newRewardImage */);
            // Nach erfolgreicher Hinzufügung neu laden
            const fetchedRewards = await fetchRewards(token);
            rewards = fetchedRewards;
            console.log('Added Reward');

            // Felder zurücksetzen
            newRewardTitle = '';
            newRewardPoints = '';
            newRewardDescription = '';
            // Entfernt: newRewardImage = '';

            Swal.fire({
                title: 'Erfolgreich',
                text: 'Die neue Belohnung wurde hinzugefügt.',
                icon: 'success',
                confirmButtonText: 'OK',
            });
        } catch (err) {
            console.error('Fehler beim Hinzufügen der Belohnung:', err);
            Swal.fire({
                title: 'Fehler',
                text: err.message || 'Fehler beim Hinzufügen der Belohnung.',
                icon: 'error',
                confirmButtonText: 'OK',
            });
        }
    }

    // Funktion zum Aktualisieren einer Reward
    async function handleUpdateReward(reward) {
        const token = get(authStore).token;

        const titleStr = String(reward.title || '');
        const pointsStr = String(reward.points || '');

        if (!titleStr.trim() || !pointsStr.trim()) {
            Swal.fire({
                title: 'Fehler',
                text: 'Bitte geben Sie einen Titel und Punkte für die Belohnung ein.',
                icon: 'error',
                confirmButtonText: 'OK',
            });
            return;
        }

        const points = parseInt(pointsStr, 10);
        if (isNaN(points)) {
            Swal.fire({
                title: 'Fehler',
                text: 'Bitte geben Sie eine gültige Zahl für die Punkte ein.',
                icon: 'error',
                confirmButtonText: 'OK',
            });
            return;
        }

        try {
            await updateReward(token, reward.reward_id, titleStr.trim(), points, reward.description /*, reward.image */);
            console.log('Updated Reward:', reward);

            Swal.fire({
                title: 'Erfolgreich',
                text: 'Die Belohnung wurde aktualisiert.',
                icon: 'success',
                confirmButtonText: 'OK',
            });
        } catch (err) {
            console.error('Fehler beim Aktualisieren der Belohnung:', err);
            Swal.fire({
                title: 'Fehler',
                text: err.message || 'Fehler beim Aktualisieren der Belohnung.',
                icon: 'error',
                confirmButtonText: 'OK',
            });
        }
    }

    // Funktion zum Löschen einer Reward
    async function handleDeleteReward(reward_id) {
        const token = get(authStore).token;

        Swal.fire({
            title: 'Sind Sie sicher?',
            text: 'Möchten Sie diese Belohnung wirklich löschen?',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Ja, löschen',
            cancelButtonText: 'Abbrechen',
        }).then(async (result) => {
            if (result.isConfirmed) {
                try {
                    await deleteReward(token, reward_id);
                    rewards = rewards.filter(r => r.reward_id !== reward_id);
                    console.log('Deleted Reward ID:', reward_id);

                    Swal.fire({
                        title: 'Gelöscht',
                        text: 'Die Belohnung wurde gelöscht.',
                        icon: 'success',
                        confirmButtonText: 'OK',
                    });
                } catch (err) {
                    console.error('Fehler beim Löschen der Belohnung:', err);
                    Swal.fire({
                        title: 'Fehler',
                        text: err.message || 'Fehler beim Löschen der Belohnung.',
                        icon: 'error',
                        confirmButtonText: 'OK',
                    });
                }
            }
        });
    }


function goBack() {
    navigate('/admin'); // Passe den Pfad entsprechend an
}
</script>

<style>
    /* Gemeinsame CSS-Variablen für Konsistenz */
    :root {
        --primary-color: #2ecc71;
        --primary-color-dark: #27ae60;
        --table-background: rgba(0, 0, 0, 0.4);
        --input-background: rgba(0, 0, 0, 0.5);
        --text-color: #fff;
        --error-color: #e74c3c;
    }

    /* Basis-Layout */
    main {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 40px;
        max-width: 1200px;
        margin: 0 auto;
        background: var(--background-color);-+
        color: var(--text-color);
        font-family: 'Roboto', sans-serif;
    }

    /* Überschriften */
    h1 {
        color: var(--primary-color);
        text-shadow: 0 0 20px var(--primary-color), 0 0 40px var(--primary-color);
        margin-bottom: 40px;
        font-size: 2.5rem;
        animation: glow 2s infinite alternate;
    }

    h2 {
        color: var(--primary-color);
        text-shadow: 0 0 20px var(--primary-color), 0 0 40px var(--primary-color);
        margin-bottom: 40px;
        font-size: 2rem;
        animation: glow 2s infinite alternate;
    }

    @keyframes glow {
        from {
            text-shadow: 0 0 10px var(--primary-color), 0 0 20px var(--primary-color);
        }
        to {
            text-shadow: 0 0 20px var(--primary-color), 0 0 40px var(--primary-color);
        }
    }

    /* Tabellen */
    table {
        width: 100%;
        max-width: 900px;
        border-collapse: collapse;
        margin: 20px 0;
        background: var(--table-background);
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 0 20px rgba(0,0,0,0.5);
        color: var(--text-color);
        text-align: center;
    }

    th, td {
        padding: 20px;
        text-align: center;
        border-bottom: 1px solid var(--primary-color);
        font-size: 1rem;
        vertical-align: middle;
        text-shadow: 0 0 5px var(--primary-color);
    }

    th {
        background-color: #000;
        font-size: 1.1rem;
        color: var(--primary-color);
        border-bottom: 2px solid var(--primary-color);
        text-transform: uppercase;
    }

    td {
        background-color: rgba(42, 42, 42, 0.7);
    }

    td:last-child {
        text-align: center;
    }

    /* Spezielle Klasse für Beschreibungstextfelder */
    .description-textarea {
        min-height: 60px; /* Vergrößert die Höhe des Textbereichs */
    }

    /* Eingabefelder */
    input, select, textarea {
        width: 100%;
        padding: 12px;
        border: 1px solid var(--primary-color);
        border-radius: 8px;
        font-size: 1rem;
        background: var(--input-background);
        color: var(--primary-color);
        margin-top: 5px;
        box-shadow: inset 0 0 10px var(--primary-color);
        transition: box-shadow 0.3s, border-color 0.3s;
    }

    input:focus, select:focus, textarea:focus {
        border-color: var(--primary-color-dark);
        box-shadow: 0 0 15px var(--primary-color-dark);
        outline: none;
    }

    /* Buttons */
    button {
        background: var(--primary-color);
        color: #000;
        padding: 12px 20px;
        font-size: 1rem;
        margin-bottom: 10px;
        border: none;
        border-radius: 25px;                                                                                
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        font-weight: bold;
        text-shadow: 0 0 10px #000;
    }

    button:hover {
        background: var(--primary-color-dark);
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 0 15px var(--primary-color-dark);
    }

    /* Delete Button */
    .delete-button {
        padding: 10px 20px;
        font-size: 1rem;
        cursor: pointer;
        border: none;
        background-color: #e74c3c;
        color: white;
        border-radius: 10px;
        transition: background-color 0.3s ease, transform 0.3s ease;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
    }

    .delete-button:hover {
        background-color: #c0392b !important;
        transform: translateY(-3px) !important;
    }

    /* Icons */
    .fas {
        margin-right: 5px;
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        h1 {
            font-size: 2rem;
        }

        h2 {
            font-size: 1.5rem;
        }

        table {
            font-size: 0.9rem;
        }

        button {
            font-size: 0.9rem;
            padding: 10px 15px;
        }

        .reward-list {
            max-width: 100%;
        }
    }

    /* Nachrichten */
    .error {
        color: var(--error-color);
        font-weight: bold;
        margin-bottom: 20px;
        text-shadow: 0 0 10px var(--error-color);
    }
</style>

<main>
    <h1>Verwaltung von Rewards</h1>

    {#if isLoading}
        <p>Lade Rewards...</p>
    {:else if error}
        <p class="error">{error}</p>
    {:else}
        <div class="reward-list">
            <h2>Bestehende Rewards</h2>
            <table>
                <thead>
                    <tr>
                        <th>Title</th>
                        <th>Punkte</th>
                        <th>Beschreibung</th>
                        <!-- Entfernt die Bild-URL-Spalte -->
                        <th>Aktionen</th>
                    </tr>
                </thead>
                <tbody>
                    {#each rewards as reward}
                        <tr>
                            <td>
                                <input
                                    type="text"
                                    bind:value={reward.title}
                                />
                            </td>
                            <td>
                                <input
                                    type="number"
                                    bind:value={reward.points}
                                />
                            </td>
                            <td>
                                <textarea
                                    bind:value={reward.description}
                                    class="description-textarea"
                                ></textarea>
                            </td>
                            <!-- Entfernt die Bild-URL-Eingabe -->
                            <td>
                                <button on:click={() => handleUpdateReward(reward)}>
                                    <i class="fas fa-save"></i> Speichern
                                </button>
                                <button class="delete-button" on:click={() => handleDeleteReward(reward.reward_id)}>
                                    <i class="fas fa-trash-alt"></i> Löschen
                                </button>
                            </td>
                        </tr>
                    {/each}
                    <!-- Zeile zum Hinzufügen einer neuen Reward -->
                    <tr>
                        <td>
                            <input
                                type="text"
                                placeholder="Neuer Reward-Titel"
                                bind:value={newRewardTitle}
                            />
                        </td>
                        <td>
                            <input
                                type="number"
                                placeholder="Punkte"
                                bind:value={newRewardPoints}
                            />
                        </td>
                        <td>
                            <textarea
                                placeholder="Neue Beschreibung"
                                bind:value={newRewardDescription}
                                class="description-textarea"
                            ></textarea>
                        </td>
                        <!-- Entfernt die Bild-URL-Eingabe -->
                        <td>
                            <button on:click={handleAddReward}>
                                <i class="fas fa-plus-circle"></i> Hinzufügen
                            </button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    {/if}
    <button class="back-button" on:click={goBack}>Zurück zum Adminbereich</button>
</main>
