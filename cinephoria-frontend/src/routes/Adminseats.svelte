<!-- src/routes/Adminseats.svelte -->
<script>
    import { onMount } from "svelte";
    import { fetchSeats, batchUpdateSeats, fetchSeatTypes } from '../services/api.js';
    import { navigate } from "svelte-routing";
    import { get } from 'svelte/store';
    import { authStore } from '../stores/authStore.js';
    import Swal from 'sweetalert2';
    import "@fortawesome/fontawesome-free/css/all.min.css";

    export let screenId;

    let isEditMode = false;
    const mode = () => isEditMode ? 'Aktiver Modus: Bearbeiten' : 'Aktiver Modus: Hinzufügen/Löschen';

    let grid = [
        [null, null, null],
        [null, null, null],
        [null, null, null],
    ];

    let rowLabels = ['A', 'B', 'C'];

    let loading = true;
    let error = "";

    let originalSeats = new Map();

    // Neu: Liste aller Sitztypen laden (inkl. color & icon)
    let seatTypesList = [];

    function standardexisting(){
    // Überprüft, ob irgendein Sitztyp den Namen 'standard' enthält
    const hasStandard = seatTypesList.some(st => st.name.includes('Standard'));

    if (hasStandard) {
        return 'Standard';
    } else if (seatTypesList.length > 0) {
        return seatTypesList[0].name;
    } else {
        return 'defaultType'; // Fallback-Wert, falls seatTypesList leer ist
    }
}



    function generateRowLabels(maxRow) {
        const labels = [];
        const maxCode = maxRow.charCodeAt(0);
        for (let code = 65; code <= maxCode; code++) {
            labels.push(String.fromCharCode(code));
        }
        return labels;
    }

    // Hilfsfunktion: Sitztyp nach Namen holen
    function getSeatType(name) {
        if (!name) return null;
        return seatTypesList.find(st => st.name === name) || null;
    }

    // toggleCell anpassen, um seatTypesList zu verwenden
    function toggleCell(row, col) {
        if (seatTypesList.length === 0) {
            // Wenn noch keine SeatTypes geladen, nichts tun
            return;
        }

        const current = grid[row][col];

        if (!isEditMode) {
            // Add-Modus: null <-> seatTypesList[0].name
            if (current === null) {
               // grid[row][col] = seatTypesList[0].name;
                grid[row][col] = standardexisting();

              //  console.log('Seat type:', seatTypesList);
            } else {
                grid[row][col] = null;
            }
        } else {
            // Edit-Modus: zyklisch durch seatTypesList
            if (current === null) {
                grid[row][col] = standardexisting();
            } else {
                const i = seatTypesList.findIndex(st => st.name === current);
                const nextIndex = (i + 1) % seatTypesList.length;
                grid[row][col] = seatTypesList[nextIndex].name;
            }
        }

        grid = [...grid];
    }

    function toggleMode() {
        isEditMode = !isEditMode;
    }

    function toggleRow(row) {
        if (!isEditMode && seatTypesList.length > 0) {
            const allActive = grid[row].every(cell => cell);
            grid[row] = grid[row].map(() => allActive ? null : standardexisting()); //seatTypesList[0].name);
            grid = [...grid];
        }
    }

    function toggleColumn(col) {
        if (!isEditMode && seatTypesList.length > 0) {
            const allActive = grid.every(row => row[col]);
            grid = grid.map(row => {
                row[col] = allActive ? null : standardexisting(); //seatTypesList[0].name;
                return row;
            });
            grid = [...grid];
        }
    }

    function addRow() {
        if (!isEditMode) {
            const lastLabel = rowLabels[rowLabels.length - 1];
            const newRowLabel = String.fromCharCode(lastLabel.charCodeAt(0) + 1);
            const newRow = Array(grid[0].length).fill(null);
            grid = [...grid, newRow];
            rowLabels = [...rowLabels, newRowLabel];
        }
    }

    function addColumn() {
        if (!isEditMode) {
            grid = grid.map(row => [...row, null]);
        }
    }

    function removeRow() {
        if (!isEditMode && grid.length > 1) {
            rowLabels.pop();
            grid.pop();
            grid = [...grid];
        }
    }

    function removeColumn() {
        if (!isEditMode && grid[0].length > 1) {
            grid = grid.map(row => row.slice(0, -1));
            grid = [...grid];
        }
    }

    function getRowLabel(index) {
        return rowLabels[index];
    }

    function getStandardSeatType() {
    return seatTypesList.find(st => st.name.toLowerCase() === 'standard');
    }


    async function submitChanges() {
        const auth = get(authStore);
        const token = auth.token;

        try {
            const loadingSwal = Swal.fire({
                title: 'Lädt...',
                text: 'Bitte warten, während die Änderungen verarbeitet werden...',
                icon: 'info',
                showConfirmButton: false,
                didOpen: () => {
                    Swal.showLoading();
                },
            });

            let currentSeats = new Map();
            for (let rowIndex = 0; rowIndex < grid.length; rowIndex++) {
                for (let colIndex = 0; colIndex < grid[rowIndex].length; colIndex++) {
                    if (grid[rowIndex][colIndex]) {
                        const rowLabel = getRowLabel(rowIndex);
                        const seatNumber = colIndex + 1;
                        currentSeats.set(`${rowLabel},${seatNumber}`, grid[rowIndex][colIndex]);
                    }
                }
            }

            let seatsToAdd = [];
            currentSeats.forEach((type, seat) => {
                if (!originalSeats.has(seat)) {
                    const [row, number] = seat.split(',');
                    seatsToAdd.push({ row, number: parseInt(number, 10), type });
                }
            });

            let seatsToDelete = [];
            originalSeats.forEach((type, seat) => {
                if (!currentSeats.has(seat)) {
                    const [row, number] = seat.split(',');
                    seatsToDelete.push({ row, number: parseInt(number, 10) });
                }
            });

            let seatsToUpdate = [];
            currentSeats.forEach((type, seat) => {
                if (originalSeats.has(seat) && originalSeats.get(seat) !== type) {
                    const [row, number] = seat.split(',');
                    seatsToUpdate.push({ row, number: parseInt(number, 10), type });
                }
            });

            const result = await batchUpdateSeats(screenId, seatsToAdd, seatsToDelete, seatsToUpdate);

            loadingSwal.close();
            Swal.fire({
                title: "Erfolgreich",
                html: `
                    <p>Zu addierende Sitze: ${seatsToAdd.length > 0 ? seatsToAdd.map(s => `(${s.row},${s.number},${s.type})`).join(', ') : 'Keine'}</p>
                    <p>Zu löschende Sitze: ${seatsToDelete.length > 0 ? seatsToDelete.map(s => `(${s.row},${s.number})`).join(', ') : 'Keine'}</p>
                    <p>Zu aktualisierende Sitze: ${seatsToUpdate.length > 0 ? seatsToUpdate.map(s => `(${s.row},${s.number},${s.type})`).join(', ') : 'Keine'}</p>
                `,
                icon: "success",
                timer: 2500,
                showConfirmButton: false,
            });

            originalSeats = new Map(currentSeats);

        } catch (err) {
            console.error("Fehler beim Eintragen der Änderungen:", err);
            Swal.fire({
                title: "Fehler",
                text: err.message || "Ein Fehler ist aufgetreten.",
                icon: "error",
                confirmButtonText: "OK",
            });
        }
    }

    onMount(async () => {
        const auth = get(authStore);
        const token = auth.token;
        const isAdmin = auth.isAdmin;

        console.log('Adminseats mounted with screenId:', screenId);
        console.log('Token:', token);
        console.log('Is Admin:', isAdmin);

        try {
            // SeatTypes laden, bevor Seats geladen werden
            seatTypesList = await fetchSeatTypes(token);

            const data = await fetchSeats(screenId, token);
            console.log('Fetched seats data:', data);

            if (data && data.seats && data.seats.length > 0) {
                const maxRow = data.seats.reduce((max, seat) => seat.row > max ? seat.row : max, 'A');
                rowLabels = generateRowLabels(maxRow);
                const cols = Math.max(...data.seats.map(seat => seat.number));

                grid = Array.from({ length: rowLabels.length }, (_, rowIndex) => {
                    return Array.from({ length: cols }, (_, colIndex) => {
                        const seat = data.seats.find(
                            s => s.row === rowLabels[rowIndex] && s.number === colIndex + 1
                        );
                        if (seat) {
                            originalSeats.set(`${seat.row},${seat.number}`, seat.type);
                            return seat.type;
                        }
                        return null;
                    });
                });
            } else {
                grid = [[null, null, null]];
                rowLabels = ['A'];
            }
        } catch (err) {
            console.error("Fehler beim Abrufen der Sitze:", err);
            error = err.message || "Ein Fehler ist aufgetreten. Bitte versuche es erneut.";
        } finally {
            loading = false;
        }
    });
</script>

<style>
    body {
    margin: 0;
    font-family: 'Roboto', sans-serif;
    background: linear-gradient(135deg, #000428, #004e92);
    color: #fff;
    overflow-x: hidden;
    max-width: 100%;
}

main {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 40px;
    max-width: 1200px;
    margin: 0 auto;
    text-align: center;
    gap: 30px; /* Mehr Abstand zwischen den Sektionen */
}

h1 {
    margin-top: 20px;
    margin-bottom: 10px;
    font-size: 3rem;
    color: #2ecc71;
    text-shadow: 0 0 20px #2ecc71, 0 0 40px #2ecc71;
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

.error {
    color: #e74c3c;
    font-weight: bold;
    margin-bottom: 20px;
    font-size: 1.2rem;
}

.grid-container {
    display: grid;
    overflow-x: auto;
    justify-content: center;
    margin: 40px auto;
}

.column-labels, .row {
    display: flex;
}

.column-selector, .row-selector {
    width: 50px;
    height: 50px;
    background: rgba(0,0,0,0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    border: 1px solid #333;
    user-select: none;
    color: #fff;
    cursor: pointer;
    transition: transform 0.3s, box-shadow 0.3s;
    text-shadow: 0 0 5px #fff;
}

.column-selector:hover, .row-selector:hover {
    transform: translateY(-5px);
    box-shadow: 0 0 20px #2ecc71;
}

.cell {
    width: 50px;
    height: 50px;
    border: 1px solid #333;
    cursor: pointer;
    transition: transform 0.3s, box-shadow 0.3s;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    color: #fff;
    text-shadow: 0 0 5px #fff;
}

.cell:hover {
    transform: translateY(-3px);
    box-shadow: 0 0 15px #2ecc71;
}

.cell.null {
    background-color: rgba(0,0,0,0.2);
}

.controls {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 10px;
    margin-bottom: 20px;
}

button {
    padding: 10px 20px;
    font-size: 1rem;
    cursor: pointer;
    border: none;
    border-radius: 8px;
    transition: background-color 0.3s, transform 0.3s, box-shadow 0.3s;
    font-weight: bold;
    color: #000;
    background: #2ecc71;
    box-shadow: 0 0 10px #2ecc71;
}

button:hover {
    background: #27ae60;
    transform: translateY(-3px) scale(1.05);
    box-shadow: 0 0 15px #27ae60;
}

.add-buttons {
    background: #2ecc71;
}

.remove-buttons {
    background: #e74c3c;
    color: #fff;
    box-shadow: 0 0 10px #e74c3c;
}

.remove-buttons:hover {
    background: #c0392b;
    box-shadow: 0 0 15px #c0392b;
}

.submit-button {
    background: #fff;
    color: #000;
    border: 3px solid #1976d2;
    font-size: 1.2rem;
    text-shadow: none;
    box-shadow: none;
}

.submit-button:hover {
    background: #e0e0e0;
    border-color: #1565c0;
    transform: translateY(-3px) scale(1.05);
    box-shadow: 0 0 15px #3498db;
}

.mode-switch {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 20px;
}

.switch {
    position: relative;
    display: inline-block;
    width: 60px;
    height: 30px;
    margin: 0 10px;
}

.switch input {
    opacity: 0;
    width: 0;
    height: 0;
}

.slider {
    position: absolute;
    cursor: pointer;
    top: 0; left: 0; right: 0; bottom: 0;
    background-color: green;
    border-radius: 30px;
    transition: 0.4s;
}

.slider:before {
    position: absolute;
    content: "";
    height: 24px; width: 24px;
    left: 3px; bottom: 3px;
    background-color: white;
    border-radius: 50%;
    transition: 0.4s;
}

input:checked + .slider {
    background-color: #1976d2;
}

input:checked + .slider:before {
    transform: translateX(30px);
}

.mode-label {
    font-size: 1.2rem;
    font-weight: bold;
    color: #2ecc71;
    text-shadow: 0 0 10px #2ecc71;
}

@media (max-width: 600px) {
    .cell, .row-selector, .column-selector {
        width: 40px;
        height: 40px;
    }

    button {
        padding: 8px 16px;
        font-size: 0.9rem;
    }
}

</style>

<main>
    {#if error}
        <p class="error">{error}</p>
    {:else if loading}
        <p>Lade Sitze...</p>
    {:else}
        <h1>Kinositz-Editor für Screen {screenId}</h1>

        <div class="controls">
            <button on:click={submitChanges} class="submit-button">EINTRAGEN</button>
            <button on:click={addRow} class="add-buttons" disabled={isEditMode}>Zeile hinzufügen</button>
            <button on:click={addColumn} class="add-buttons" disabled={isEditMode}>Spalte hinzufügen</button>
            <button on:click={removeRow} class="remove-buttons" disabled={isEditMode || grid.length <= 1}>Zeile entfernen</button>
            <button on:click={removeColumn} class="remove-buttons" disabled={isEditMode || grid[0].length <= 1}>Spalte entfernen</button>
        </div>
        
        <div class="mode-switch">
            <label class="switch">
                <input type="checkbox" bind:checked={isEditMode}>
                <span class="slider"></span>
            </label>
            <span class="mode-label">{mode()}</span>
        </div>
        
        <p> LEINWAND <br>
        _____________________________________ </p>

        <div class="grid-container">
            <!-- Dynamische Spaltenanzahl mit korrektem Template Literal -->
            <div class="column-labels" style={`grid-template-columns: 50px repeat(${grid[0].length}, 50px);`}>
                <div></div>
                {#each grid[0] as _, colIndex}
                    <div class="column-selector"
                         on:click={() => toggleColumn(colIndex)}
                         title="Klicke, um die gesamte Spalte auszuwählen/deaktivieren">
                        {colIndex + 1}
                    </div>
                {/each}
            </div>

            {#each grid as row, rowIndex}
                <div class="row">
                    <div class="row-selector"
                         on:click={() => toggleRow(rowIndex)}
                         title="Klicke, um die gesamte Zeile auszuwählen/deaktivieren">
                        {getRowLabel(rowIndex)}
                    </div>
                    {#each row as cell, colIndex}
                        {#if cell !== null}
                            {#if getSeatType(cell)}
                                <div class="cell"
                                     style="background-color: {getSeatType(cell).color};"
                                     on:click={() => toggleCell(rowIndex, colIndex)}
                                     title={`Reihe: ${getRowLabel(rowIndex)}, Sitz: ${colIndex + 1}, Typ: ${getSeatType(cell).name}, Preis: ${getSeatType(cell).price}€`}
                                >
                                    {#if getSeatType(cell).icon}
                                        <i class={`fas ${getSeatType(cell).icon}`}></i>
                                    {/if}
                                </div>
                            {:else}
                                <div class="cell null"
                                     on:click={() => toggleCell(rowIndex, colIndex)}
                                     title={`Reihe: ${getRowLabel(rowIndex)}, Sitz: ${colIndex + 1}`}
                                ></div>
                            {/if}
                        {:else}
                            <div class="cell null"
                                 on:click={() => toggleCell(rowIndex, colIndex)}
                                 title={`Reihe: ${getRowLabel(rowIndex)}, Sitz: ${colIndex + 1}`}
                            ></div>
                        {/if}
                    {/each}
                </div>
            {/each}
        </div>
    {/if}

    <button on:click={() => navigate('/adminkinosaal')}>Zurück zu Überblick der Kinosäle</button>
</main>
