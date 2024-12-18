<script>
    import { onMount } from 'svelte';
    import Swal from 'sweetalert2';
    import { get } from 'svelte/store';
    import { authStore } from '../stores/authStore.js';
    import { fetchRewards, addReward, updateReward, deleteReward } from '../services/api.js';

    let rewards = [];
    let isLoading = true;
    let error = null;

    // Neue Reward-Daten
    let newRewardTitle = '';
    let newRewardPoints = '';
    let newRewardDescription = '';
    let newRewardImage = '';

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

        if (!newRewardTitle.trim() || !newRewardPoints.trim()) {
            Swal.fire({
                title: 'Fehler',
                text: 'Bitte geben Sie einen Titel und Punkte für die Belohnung ein.',
                icon: 'error',
                confirmButtonText: 'OK',
            });
            return;
        }

        try {
            await addReward(token, newRewardTitle, parseInt(newRewardPoints), newRewardDescription, newRewardImage);
            // Nach erfolgreicher Hinzufügung neu laden
            const fetchedRewards = await fetchRewards(token);
            rewards = fetchedRewards;
            console.log('Added Reward');

            // Felder zurücksetzen
            newRewardTitle = '';
            newRewardPoints = '';
            newRewardDescription = '';
            newRewardImage = '';

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

        if (!reward.title.trim() || !reward.points) {
            Swal.fire({
                title: 'Fehler',
                text: 'Bitte geben Sie einen Titel und Punkte für die Belohnung ein.',
                icon: 'error',
                confirmButtonText: 'OK',
            });
            return;
        }

        try {
            await updateReward(token, reward.reward_id, reward.title, parseInt(reward.points), reward.description, reward.image);
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
</script>

<style>
    @import "@fortawesome/fontawesome-free/css/all.min.css";

    main {
        display: flex;
        flex-direction: column;
        align-items: center;
        font-family: 'Roboto', sans-serif;
        padding: 30px;
        background: linear-gradient(120deg, #f0f9ff, #cfefff);
        border-radius: 10px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    }

    h1, h2 {
        text-align: center;
        margin-bottom: 20px;
    }

    h1 {
        font-size: 2.8rem;
        color: #34495e;
        margin-bottom: 15px;
        border-bottom: 4px solid #3498db;
        display: inline-block;
        padding-bottom: 10px;
    }

    h2 {
        font-size: 2rem;
        color: #2c3e50;
    }

    table {
        width: 100%;
        max-width: 900px;
        border-collapse: collapse;
        margin: 20px 0;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        overflow: hidden;
        text-align: center;
    }

    th, td {
        padding: 20px;
        text-align: center;
        border-bottom: 1px solid #ddd;
        font-size: 1rem;
        vertical-align: middle;
    }

    th {
        background-color: #2c3e50;
        color: #ffffff;
        text-transform: uppercase;
        font-weight: bold;
    }

    td {
        color: #555;
        background-color: #ffffff;
    }

    input, select, textarea {
        width: 100%;
        padding: 12px;
        border: 1px solid #ddd;
        border-radius: 6px;
        font-size: 1rem;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
    }

    input:focus, select:focus, textarea:focus {
        border-color: #3498db;
        box-shadow: 0 2px 10px rgba(52, 152, 219, 0.3);
        outline: none;
    }

    button {
        background: #3498db;
        color: white;
        padding: 12px 20px;
        font-size: 1rem;
        border: none;
        border-radius: 25px;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }

    button:hover {
        transform: translateY(-3px);
    }

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
                        <th>Points</th>
                        <th>Description</th>
                        <th>Image</th>
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
                                ></textarea>
                            </td>
                            <td>
                                <input
                                    type="text"
                                    placeholder="Bild-URL"
                                    bind:value={reward.image}
                                />
                            </td>
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
                            ></textarea>
                        </td>
                        <td>
                            <input
                                type="text"
                                placeholder="Bild-URL"
                                bind:value={newRewardImage}
                            />
                        </td>
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
</main>
