<!-- src/routes/Adminseats.svelte -->
<script>
    import { onMount } from "svelte";
    import { fetchSeats, createSeat, deleteSeat } from '../services/api.js';
    import { navigate } from "svelte-routing";
    import { get } from 'svelte/store';
    import { authStore } from '../stores/authStore.js';
    import Swal from 'sweetalert2';

    export let screenId; 

    let seats = [];
    let error = "";
    let loading = true;

    // Grid-Array: Array von Arrays, die die Sitzpositionen darstellen
    let grid = [];
    let rowLabels = []; // Für die Anzeige der Zeilenbeschriftungen

    // Bearbeitungsmodus
    let editMode = false;

    // Funktionen zum Bearbeiten des Grids
    async function toggleCell(row, col) {
        if (editMode) {
            const cell = grid[row][col];
            if (!cell.exists) {
                // Sitze hinzufügen
                const rowLabel = cell.row;
                const seatNumber = cell.number;

                try {
                    const data = await createSeat(screenId, rowLabel, seatNumber, 'standard');
                    // Aktualisiere die Grid-Zelle mit der neuen seat_id
                    grid[row][col].exists = true;
                    grid[row][col].type = 'standard';
                    grid[row][col].seat_id = data.seat_id;

                    Swal.fire({
                        title: "Erfolgreich",
                        text: `Sitz (${rowLabel},${seatNumber}) hinzugefügt.`,
                        icon: "success",
                        timer: 1500,
                        showConfirmButton: false,
                    });
                } catch (err) {
                    console.error("Fehler beim Erstellen des Sitzes:", err);
                    Swal.fire({
                        title: "Fehler",
                        text: err.message || "Ein Fehler ist aufgetreten.",
                        icon: "error",
                        confirmButtonText: "OK",
                    });
                }
            } else {
                // Sitze entfernen
                try {
                    await deleteSeat(cell.seat_id);
                    grid[row][col].exists = false;
                    grid[row][col].type = 'empty';
                    grid[row][col].seat_id = null;

                    Swal.fire({
                        title: "Erfolgreich",
                        text: `Sitz (${cell.row},${cell.number}) entfernt.`,
                        icon: "success",
                        timer: 1500,
                        showConfirmButton: false,
                    });
                } catch (err) {
                    console.error("Fehler beim Löschen des Sitzes:", err);
                    Swal.fire({
                        title: "Fehler",
                        text: err.message || "Ein Fehler ist aufgetreten.",
                        icon: "error",
                        confirmButtonText: "OK",
                    });
                }
            }
        }
    }

    function toggleEditMode() {
        editMode = !editMode;
    }

    async function toggleRow(row) {
        if (editMode) {
            const rowData = grid[row];
            const seatsToAdd = [];

            rowData.forEach(cell => {
                if (!cell.exists) {
                    seatsToAdd.push(cell);
                }
            });

            if (seatsToAdd.length === 0) {
                Swal.fire({
                    title: "Info",
                    text: "Alle Sitze in dieser Zeile sind bereits angelegt.",
                    icon: "info",
                    timer: 1500,
                    showConfirmButton: false,
                });
                return;
            }

            // Füge alle Sitze in der Zeile hinzu
            for (const cell of seatsToAdd) {
                try {
                    const data = await createSeat(screenId, cell.row, cell.number, 'standard');
                    cell.exists = true;
                    cell.type = 'standard';
                    cell.seat_id = data.seat_id;
                } catch (err) {
                    console.error("Fehler beim Erstellen des Sitzes:", err);
                    Swal.fire({
                        title: "Fehler",
                        text: err.message || "Ein Fehler ist aufgetreten.",
                        icon: "error",
                        confirmButtonText: "OK",
                    });
                }
            }

            Swal.fire({
                title: "Erfolgreich",
                text: `Alle verfügbaren Sitze in Zeile ${grid[row][0].row} wurden hinzugefügt.`,
                icon: "success",
                timer: 1500,
                showConfirmButton: false,
            });
        }
    }

    async function toggleColumn(col) {
        if (editMode) {
            const seatsToAdd = [];

            grid.forEach(row => {
                const cell = row[col];
                if (!cell.exists) {
                    seatsToAdd.push(cell);
                }
            });

            if (seatsToAdd.length === 0) {
                Swal.fire({
                    title: "Info",
                    text: "Alle Sitze in dieser Spalte sind bereits angelegt.",
                    icon: "info",
                    timer: 1500,
                    showConfirmButton: false,
                });
                return;
            }

            // Füge alle Sitze in der Spalte hinzu
            for (const cell of seatsToAdd) {
                try {
                    const data = await createSeat(screenId, cell.row, cell.number, 'standard');
                    cell.exists = true;
                    cell.type = 'standard';
                    cell.seat_id = data.seat_id;
                } catch (err) {
                    console.error("Fehler beim Erstellen des Sitzes:", err);
                    Swal.fire({
                        title: "Fehler",
                        text: err.message || "Ein Fehler ist aufgetreten.",
                        icon: "error",
                        confirmButtonText: "OK",
                    });
                }
            }

            Swal.fire({
                title: "Erfolgreich",
                text: `Alle verfügbaren Sitze in Spalte ${col + 1} wurden hinzugefügt.`,
                icon: "success",
                timer: 1500,
                showConfirmButton: false,
            });
        }
    }

    function addRow() {
        if (editMode) {
            const newRowIndex = grid.length;
            const newRowLabel = String.fromCharCode(65 + newRowIndex); // 'A', 'B', 'C', ...
            const newRow = [];

            for (let i = 0; i < grid[0].length; i++) {
                newRow.push({
                    seat_id: null, // Noch kein Sitz erstellt
                    row: newRowLabel,
                    number: i + 1,
                    exists: false,
                    type: 'empty',
                });
            }

            grid.push(newRow);
            rowLabels.push(newRowLabel);
        }
    }

    function addColumn() {
        if (editMode) {
            const newColIndex = grid[0].length;

            grid.forEach(row => {
                const rowLabel = row[0].row;
                row.push({
                    seat_id: null, // Noch kein Sitz erstellt
                    row: rowLabel,
                    number: newColIndex + 1,
                    exists: false,
                    type: 'empty',
                });
            });
        }
    }

    async function removeRow() {
        if (editMode && grid.length > 1) {
            const removedRow = grid.pop();
            const removedLabel = rowLabels.pop();

            // Entferne alle Sitze in dieser Zeile aus dem Backend
            for (const cell of removedRow) {
                if (cell.exists && cell.seat_id) {
                    try {
                        await deleteSeat(cell.seat_id);
                    } catch (err) {
                        console.error("Fehler beim Löschen des Sitzes:", err);
                    }
                }
            }

            Swal.fire({
                title: "Erfolgreich",
                text: `Zeile ${removedLabel} entfernt.`,
                icon: "success",
                timer: 1500,
                showConfirmButton: false,
            });
        }
    }

    async function removeColumn() {
        if (editMode && grid[0].length > 1) {
            const removedColIndex = grid[0].length - 1;

            for (const row of grid) {
                const removedCell = row.pop();
                if (removedCell.exists && removedCell.seat_id) {
                    try {
                        await deleteSeat(removedCell.seat_id);
                    } catch (err) {
                        console.error("Fehler beim Löschen des Sitzes:", err);
                    }
                }
            }

            Swal.fire({
                title: "Erfolgreich",
                text: `Spalte ${removedColIndex + 1} entfernt.`,
                icon: "success",
                timer: 1500,
                showConfirmButton: false,
            });
        }
    }

    function getRowLabel(index) {
        return rowLabels[index];
    }

    function logSelectedSeats() {
        let selectedSeats = [];

        grid.forEach((row) => {
            row.forEach((cell) => {
                if (cell.exists) {
                    selectedSeats.push(`(${cell.row},${cell.number})`);
                }
            });
        });

        console.log(selectedSeats.join(', '));
    }

    onMount(async () => {
        const auth = get(authStore);
        const token = auth.token;
        const isAdmin = auth.isAdmin;

        console.log('Adminseats mounted with screenId:', screenId);
        console.log('Token:', token);
        console.log('Is Admin:', isAdmin);

        try {
            const data = await fetchSeats(screenId, token);
            console.log('Fetched seats data:', data);

            if (data && data.seats) {
                seats = data.seats;

                // Verarbeite die Sitzdaten, um das Grid zu erstellen
                const rows = [...new Set(seats.map(seat => seat.row))].sort(); // Alle eindeutigen Zeilen, sortiert
                const cols = Math.max(...seats.map(seat => seat.number)); // Maximale Sitznummer

                // Initialisiere das Grid
                grid = rows.map(row => {
                    return Array(cols).fill(null).map((_, colIndex) => {
                        const seat = seats.find(s => s.row === row && s.number === colIndex + 1);
                        return seat ? { 
                            seat_id: seat.seat_id,
                            row: seat.row,
                            number: seat.number,
                            exists: true,
                            type: seat.type || 'standard' 
                        } : { 
                            seat_id: null, 
                            row: row, 
                            number: colIndex + 1, 
                            exists: false, 
                            type: 'empty' 
                        };
                    });
                });

                rowLabels = rows;
            } else {
                error = "Fehler beim Laden der Sitze.";
            }
        } catch (err) {
            console.error("Fehler beim Abrufen der Sitze:", err);
            error = err.message || "Ein Fehler ist aufgetreten. Bitte versuche es erneut.";
        } finally {
            loading = false;
        }
    });
</script>

<main>
    {#if error}
        <p class="error">{error}</p>
    {:else if loading}
        <p>Lade Sitze...</p>
    {:else}
        <h1>Kinositze für Screen {screenId}</h1>

        <div>
            <button on:click={logSelectedSeats}>EINTRAGEN</button>
            <button on:click={toggleEditMode}>
                Bearbeitungsmodus: {editMode ? "Ein" : "Aus"}
            </button>
            <button on:click={addRow}>Zeile hinzufügen</button>
            <button on:click={addColumn}>Spalte hinzufügen</button>
            <button on:click={removeRow}>Zeile entfernen</button>
            <button on:click={removeColumn}>Spalte entfernen</button>
        </div>

        <div class="grid-container">
            <!-- Spaltennummern -->
            <div
                class="column-labels"
                style={`grid-template-columns: 50px repeat(${grid[0].length}, 50px);`}
            >
                <div></div>
                {#each Array(grid[0].length) as _, colIndex}
                    <div
                        class="column-selector"
                        on:click={() => toggleColumn(colIndex)}
                        title="Klicke, um die gesamte Spalte auszuwählen/deaktivieren"
                    >
                        {colIndex + 1}
                    </div>
                {/each}
            </div>

            <!-- Sitzplan -->
            {#each grid as row, rowIndex}
                <div class="row">
                    <div
                        class="row-selector"
                        on:click={() => toggleRow(rowIndex)}
                        title="Klicke, um die gesamte Zeile auszuwählen/deaktivieren"
                    >
                        {getRowLabel(rowIndex)}
                    </div>
                    {#each row as cell, colIndex}
                        <div
                            class="cell {cell.exists ? 'active' : 'empty'}"
                            on:click={() => toggleCell(rowIndex, colIndex)}
                            title={`Reihe: ${cell.row}, Sitz: ${cell.number}`}
                        ></div>
                    {/each}
                </div>
            {/each}
        </div>
    {/if}

    <button on:click={() => navigate('/adminkinosaal')}>Zurück zu Überblick der Kinosäle</button>
</main>

<style>
    main {
        display: flex;
        flex-direction: column;
        align-items: center;
        font-family: Arial, sans-serif;
    }

    .grid-container {
        display: grid;
        overflow-x: auto;
        justify-content: center;
        margin: 20px auto;
    }

    .column-labels {
        display: grid;
        gap: 2px;
        margin-bottom: 10px;
    }

    .row {
        display: flex;
        align-items: center;
        margin-bottom: 5px;
    }

    .row-selector,
    .column-selector {
        width: 50px;
        height: 50px;
        background-color: lightgray;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        font-weight: bold;
        border: 1px solid #ddd;
    }

    .cell {
        width: 50px;
        height: 50px;
        border: 1px solid #ddd;
        cursor: pointer;
        transition: background-color 0.3s;
    }

    .cell.active {
        background-color: #90ee90; /* Hellgrün für verfügbare Sitze */
    }

    .cell.empty {
        background-color: #d3d3d3; /* Grau für nicht vorhandene Sitze */
        cursor: not-allowed;
    }

    .cell:hover:not(.empty) {
        background-color: #3cb371; /* Etwas dunkleres Grün beim Hover für verfügbare Sitze */
    }

    .error {
        color: red;
        font-weight: bold;
    }

    button {
        margin: 10px;
        padding: 10px 20px;
        font-size: 16px;
        cursor: pointer;
    }
</style>
