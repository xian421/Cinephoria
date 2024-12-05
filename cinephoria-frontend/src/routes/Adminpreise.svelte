<!-- src/routes/Adminpreise.svelte -->
<script>
    import { onMount } from 'svelte';
    import { navigate } from 'svelte-routing';
    import Swal from 'sweetalert2';
    import { fetchSeatTypes, updateSeatType, addSeatType } from '../services/api.js';
    import { get } from 'svelte/store';
    import { authStore } from '../stores/authStore.js';

    let seatTypes = []; // Wird vom Backend geladen
    let isLoading = true;
    let error = null;

    let newSeatTypeName = '';
    let newSeatTypePrice = 0.00;
    let newSeatTypeColor = '#678be0'; // Standardfarbe
    let newSeatTypeIcon = ''; // Standardicon

    // Beispielhafte Liste von Font Awesome Icons
    const availableIcons = [
        '',
       // 'fa-chair',
        'fa-wheelchair',
        'fa-star',
        'fa-user',
        'fa-crown',
        'fa-heart',
        'fa-music',
        // Fügen Sie weitere Icons hinzu, die Sie benötigen
    ];

    // Daten vom Backend laden
    onMount(async () => {
        isLoading = true;
        const token = get(authStore).token;

        try {
            const fetchedSeatTypes = await fetchSeatTypes(token);
            // Stelle sicher, dass jeder Sitztyp eine definierte Farbe hat
            seatTypes = fetchedSeatTypes.map(seat => ({
                ...seat,
                color: seat.color || '#678be0',
                icon: seat.icon
            }));
            isLoading = false;
        } catch (err) {
            console.error('Fehler beim Laden der Sitztypen:', err);
            error = err.message || 'Fehler beim Laden der Sitztypen.';
            isLoading = false;
        }
    });

    // Funktion zum Aktualisieren eines Sitztyps
    function updateSeatTypeField(index, field, value) {
        seatTypes[index] = { ...seatTypes[index], [field]: value };
        // Neuzuweisung des Arrays zur Auslösung der Reaktivität
        seatTypes = [...seatTypes];
    }

    // Funktion zum Speichern der Änderungen
    async function savePrices() {
        const token = get(authStore).token;

        try {
            const updatePromises = seatTypes.map(seat =>
                updateSeatType(token, seat.seat_type_id, { 
                    price: seat.price,
                    color: seat.color,
                    icon: seat.icon
                })
            );
            await Promise.all(updatePromises);
            Swal.fire({
                title: 'Erfolgreich',
                text: 'Die Sitztypen wurden erfolgreich gespeichert.',
                icon: 'success',
                confirmButtonText: 'OK',
            });
        } catch (err) {
            console.error('Fehler beim Speichern der Sitztypen:', err);
            Swal.fire({
                title: 'Fehler',
                text: err.message || 'Fehler beim Speichern der Sitztypen.',
                icon: 'error',
                confirmButtonText: 'OK',
            });
        }
    }

    // Funktion zum Hinzufügen eines neuen Sitztyps
    async function addNewSeatType() {
        const token = get(authStore).token;

        if (!newSeatTypeName.trim()) {
            Swal.fire({
                title: 'Fehler',
                text: 'Bitte geben Sie einen Namen für den Sitztyp ein.',
                icon: 'error',
                confirmButtonText: 'OK',
            });
            return;
        }

        if (isNaN(newSeatTypePrice) || newSeatTypePrice < 0) {
            Swal.fire({
                title: 'Fehler',
                text: 'Bitte geben Sie einen gültigen Preis ein.',
                icon: 'error',
                confirmButtonText: 'OK',
            });
            return;
        }

        try {
            const result = await addSeatType(token, newSeatTypeName, newSeatTypePrice, newSeatTypeColor, newSeatTypeIcon);
            // Fügen Sie den neuen Sitztyp zur Liste hinzu
            seatTypes = [...seatTypes, {
                seat_type_id: result.seat_type_id,
                name: newSeatTypeName,
                price: newSeatTypePrice,
                color: newSeatTypeColor,
                icon: newSeatTypeIcon
            }];
            // Felder zurücksetzen
            newSeatTypeName = '';
            newSeatTypePrice = 0.00;
            newSeatTypeColor = '#678be0';
            newSeatTypeIcon = '';
            Swal.fire({
                title: 'Erfolgreich',
                text: 'Der neue Sitztyp wurde hinzugefügt.',
                icon: 'success',
                confirmButtonText: 'OK',
            });
        } catch (err) {
            console.error('Fehler beim Hinzufügen des Sitztyps:', err);
            Swal.fire({
                title: 'Fehler',
                text: err.message || 'Fehler beim Hinzufügen des Sitztyps.',
                icon: 'error',
                confirmButtonText: 'OK',
            });
        }
    }
</script>

<style>
    @import "@fortawesome/fontawesome-free/css/all.min.css";

    main {
        display: flex;
        flex-direction: column;
        align-items: center;
        font-family: Arial, sans-serif;
        padding: 20px;
    }

    h1, h2 {
        margin-bottom: 20px;
    }

    table {
        border-collapse: collapse;
        width: 100%;
        max-width: 800px;
        margin-bottom: 20px;
    }

    th, td {
        text-align: left;
        padding: 12px;
        border-bottom: 1px solid #ddd;
    }

    th {
        background-color: #1976d2;
        color: white;
    }

    input[type="number"], input[type="color"], select {
        padding: 8px;
        margin-right: 10px;
    }

    input[type="text"] {
        padding: 8px;
        margin-right: 10px;
    }

    /* Neue Klasse für den Icon-Container */
    .icon-container {
        display: flex;
        align-items: center;
    }

    .icon-background {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
        background-color: var(--bg-color, #000000);
        border-radius: 5px;
        margin-right: 10px;
        transition: background-color 0.3s;
    }

    .icon-background i {
        color: white;
        font-size: 20px;
    }

    button {
        padding: 10px 20px;
        font-size: 16px;
        cursor: pointer;
        border: none;
        background-color: #1976d2;
        color: white;
        border-radius: 5px;
        transition: background-color 0.3s;
        margin: 5px;
    }

    button:hover {
        background-color: #1565c0;
    }

    .button-container {
        display: flex;
        justify-content: center;
        gap: 10px;
    }

    .new-seat-type {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
    }

    .new-seat-type label {
        margin-bottom: 10px;
    }

    @media (max-width: 600px) {
        input[type="number"], input[type="color"], select {
            width: 100%;
            margin-bottom: 10px;
        }

        button {
            padding: 8px 16px;
            font-size: 14px;
        }
    }
</style>

<main>
    <h1>Preisverwaltung für Sitztypen</h1>

    {#if isLoading}
        <p>Lade Sitztypen...</p>
    {:else if error}
        <p class="error">{error}</p>
    {:else}
        <table>
            <thead>
                <tr>
                    <th>Sitztyp</th>
                    <th>Preis (€)</th>
                    <th>Farbe</th>
                    <th>Icon</th>
                </tr>
            </thead>
            <tbody>
                {#each seatTypes as seat, index}
                    <tr>
                        <td>{seat.name}</td>
                        <td>
                            <input
                                type="number"
                                min="0"
                                step="0.01"
                                bind:value={seat.price}
                            />
                        </td>
                        <td>
                            <input
                                type="color"
                                bind:value={seat.color}
                            />
                        </td>
                        <td>
                            <div class="icon-container">
                                <!-- Icon-Container mit farbigem Hintergrund -->
                                <div
                                    class="icon-background"
                                    style="--bg-color: {seat.color};"
                                >
                                    <i class={`fas ${seat.icon}`}></i>
                                </div>
                                <!-- Auswahl des Icons -->
                                <select
                                    bind:value={seat.icon}
                                >
                                    {#each availableIcons as icon}
                                        <option value={icon}>{icon}</option>
                                    {/each}
                                </select>
                            </div>
                        </td>
                    </tr>
                {/each}
            </tbody>
        </table>

        <div class="button-container">
            <button on:click={savePrices}>Speichern</button>
            <button on:click={() => navigate('/admin')}>Zurück zum Adminbereich</button>
        </div>

        <h2>Neuen Sitztyp hinzufügen</h2>
        <div class="new-seat-type">
            <label>
                Name:
                <input type="text" bind:value={newSeatTypeName} />
            </label>
            <label>
                Preis (€):
                <input type="number" min="0" step="0.01" bind:value={newSeatTypePrice} />
            </label>
            <label>
                Farbe:
                <input type="color" bind:value={newSeatTypeColor} />
            </label>
            <label>
                Icon:
                <select bind:value={newSeatTypeIcon}>
                    {#each availableIcons as icon}
                        <option value={icon}>{icon}</option>
                    {/each}
                </select>
            </label>
            <button on:click={addNewSeatType}>Hinzufügen</button>
        </div>
    {/if}
</main>
