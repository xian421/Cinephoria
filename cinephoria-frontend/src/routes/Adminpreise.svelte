
<!-- src/routes/Adminpreise.svelte -->
<script>
    import { onMount } from 'svelte';
    import { navigate } from 'svelte-routing';
    import Swal from 'sweetalert2';
    import { fetchSeatTypes, updateSeatType, addSeatType, deleteSeatType as apiDeleteSeatType } from '../services/api.js';
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
        'fa-chair',
        'fa-wheelchair',
        'fa-star',
        'fa-user',
        'fa-crown',
        'fa-heart',
        'fa-music',
        'fa-lock',        // Reservierte Plätze
        'fa-tag',         // Ermäßigte Sitze
        'fa-table',       // Sitze mit Tisch
        'fa-plug',        // Sitze mit Stromversorgung
        'fa-fire',        // Beheizte Sitze
        'fa-eye',         // Beste Sicht (erste Reihe)
        'fa-users',       // Familienbereich
        'fa-users-cog',   // Bereich für Gruppen
        'fa-throne',      // Luxus-Sitze
        'fa-tree',        // Outdoor-Kino
        'fa-glasses',     // 3D-Erlebnis
        'fa-ticket-alt',  // Spezialplätze oder Events
        'fa-bed',         // Relax-Sitze
        'fa-solid fa-couch' // Alternative für Entspannungssitze
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
                    name: seat.name,
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

    // Funktion zum Löschen eines Sitztyps
    async function handleDeleteSeatType(index) {
        const seat = seatTypes[index];
        const seat_type_id = seat.seat_type_id;

        Swal.fire({
            title: 'Sind Sie sicher?',
            text: 'Dieser Sitztyp wird dauerhaft gelöscht!',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Ja, löschen!',
            cancelButtonText: 'Abbrechen',
        }).then(async (result) => {
            if (result.isConfirmed) {
                try {
                    const token = get(authStore).token;
                    await apiDeleteSeatType(token, seat_type_id);
                    // Entfernen des Sitztyps aus der Liste
                    seatTypes.splice(index, 1);
                    seatTypes = [...seatTypes];
                    Swal.fire(
                        'Gelöscht!',
                        'Der Sitztyp wurde gelöscht.',
                        'success'
                    );
                } catch (err) {
                    console.error('Fehler beim Löschen des Sitztyps:', err);
                    Swal.fire({
                        title: 'Fehler',
                        text: err.message || 'Fehler beim Löschen des Sitztyps.',
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
    padding: 20px;
    background-color: #f7f9fc;
    border-radius: 10px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

h1 {
    font-size: 2.5rem;
    color: #2c3e50;
    margin-bottom: 1rem;
    text-align: center;
    border-bottom: 2px solid #3498db;
    display: inline-block;
    padding-bottom: 0.5rem;
}

h2 {
    font-size: 1.8rem;
    color: #34495e;
    margin-top: 2rem;
    margin-bottom: 1rem;
    text-align: center;
}

table {
    border-collapse: collapse;
    width: 100%;
    max-width: 800px;
    margin-bottom: 20px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    background-color: #ffffff;
    border-radius: 8px;
    overflow: hidden;
}

th, td {
    text-align: left;
    padding: 15px;
    border-bottom: 1px solid #ddd;
    font-size: 1rem;
    vertical-align: middle;
}

th {
    background-color: #3498db;
    color: white;
    font-weight: bold;
    text-transform: uppercase;
    white-space: nowrap;
    padding: 15px;
    text-align: center;
}

td {
    color: #555;
}

.actions-column {
    text-align: center;
    width: 100px;
}

input[type="number"], input[type="color"], select, input[type="text"] {
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 5px;
    margin-right: 10px;
    font-size: 1rem;
    width: 100%;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
}

input[type="number"]:focus, input[type="color"]:focus, select:focus, input[type="text"]:focus {
    border-color: #3498db;
    outline: none;
    box-shadow: 0 2px 6px rgba(52, 152, 219, 0.3);
}

.icon-container {
    display: flex;
    align-items: center;
    gap: 10px;
}

.icon-background {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 60px;
    height: 40px;
    background-color: var(--bg-color, #3498db);
    border-radius: 10%;
    transition: background-color 0.3s, transform 0.3s;
    cursor: pointer;
    position: relative;
}

.icon-background i {
    color: white;
    font-size: 18px;
}

.icon-background:hover {
    transform: scale(1.1);
}

.icon-background input[type="color"] {
    opacity: 0;
    position: absolute;
    width: 100%;
    height: 100%;
    cursor: pointer;
}




.delete-button {
    padding: 8px 16px;
    font-size: 0.9rem;
    cursor: pointer;
    border: none;
    background-color: #e74c3c;
    color: white;
    border-radius: 5px;
    transition: background-color 0.3s ease, transform 0.3s ease;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.delete-button:hover {
    background-color: #c0392b;
    transform: translateY(-2px);
}

select {
    padding: 10px;
    border-radius: 8px;
    border: 1px solid #ddd;
    background-color: #f7f9fc;
    font-size: 1rem;
    transition: border-color 0.3s, box-shadow 0.3s;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    width: 100%;
}

select:focus {
    border-color: #3498db;
    box-shadow: 0 2px 6px rgba(52, 152, 219, 0.3);
    outline: none;
}

button {
    padding: 12px 24px;
    font-size: 1rem;
    cursor: pointer;
    border: none;
    background-color: #3498db;
    color: white;
    border-radius: 8px;
    transition: background-color 0.3s ease, transform 0.3s ease;
    margin: 5px;
    font-weight: bold;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
}

button:hover {
    background-color: #2980b9;
    transform: translateY(-3px);
}

.button-container {
    display: flex;
    justify-content: center;
    gap: 15px;
    flex-wrap: wrap;
}

.new-seat-type {
    display: grid;
    grid-template-columns: 1fr;
    gap: 15px;
    background-color: #ffffff;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    margin-top: 2rem;
    width: 100%;
    max-width: 800px;
}

.new-seat-type .row {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
}

.new-seat-type .row > div {
    flex: 1;
    min-width: 200px;
}

.new-seat-type button {
    grid-column: 1 / -1;
    justify-self: center;
    margin-top: 15px;
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

    .new-seat-type {
        grid-template-columns: 1fr;
    }
}


.new-seat-type {
    display: flex;
    flex-direction: column;
    text-align: center;
    gap: 15px;
    background-color: #ffffff;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    margin-top: 2rem;
    width: 100%;
    max-width: 500px;
}

.field {
    display: flex;
    flex-direction: column;
    gap: 5px;
    width: 95%;
}

.field label {
    font-size: 0.9rem;
    color: #34495e;
    font-weight: bold;
}

.field input, .field select {
    padding: 10px;
    font-size: 1rem;
    border: 1px solid #ddd;
    border-radius: 5px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.field input:focus, .field select:focus {
    border-color: #3498db;
    box-shadow: 0 2px 6px rgba(52, 152, 219, 0.3);
    outline: none;
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
                    <th>Icon</th>
                    <th>Löschen</th>
                </tr>
            </thead>
            <tbody>
                {#each seatTypes as seat, index}
                    <tr>
                        <td>
                            <input
                                type="text"
                                bind:value={seat.name}
                            />
                        </td>
                        
                        <td>
                            <input
                                type="number"
                                min="0"
                                step="0.01"
                                bind:value={seat.price}
                            />
                        </td>
                        
                        <td>
                            <div class="icon-container">
                                <!-- Icon-Container mit farbigem Hintergrund -->
                                <div class="icon-background" style="--bg-color: {seat.color};">
                                    <i class={`fas ${seat.icon}`}></i>
                                    <input type="color" bind:value={seat.color} />
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
                        <td>
                            <button
                                class="delete-button"
                                on:click={() => handleDeleteSeatType(index)}
                            >
                                Löschen
                            </button>
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
            <div class="field">
                <label for="seat-name">Name:</label>
                <input id="seat-name" type="text" bind:value={newSeatTypeName} />
            </div>
            <div class="field">
                <label for="seat-price">Preis (€):</label>
                <input id="seat-price" type="number" min="0" step="0.01" bind:value={newSeatTypePrice} />
            </div>
            <div class="field">
                <label for="seat-icon">Icon & Farbe:</label>
                <div class="icon-container">
                    <div class="icon-background" style="--bg-color: {newSeatTypeColor};">
                        <i class={`fas ${newSeatTypeIcon}`}></i>
                        <input id="seat-color" type="color" bind:value={newSeatTypeColor} />
                    </div>
                    <select id="seat-icon" bind:value={newSeatTypeIcon}>
                        {#each availableIcons as icon}
                            <option value={icon}>{icon}</option>
                        {/each}
                    </select>
                </div>
            </div>
            <button on:click={addNewSeatType}>Hinzufügen</button>
        </div>
        
    {/if}
</main>
