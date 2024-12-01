<!-- src/routes/Adminseats.svelte -->
<script>
    import { onMount } from "svelte";
    import { fetchSeats, createSeat, deleteAllSeats } from '../services/api.js';
    import { navigate } from "svelte-routing";
    import { get } from 'svelte/store';
    import { authStore } from '../stores/authStore.js';
    import Swal from 'sweetalert2';

    export let screenId; 

    let grid = [
        [false, false, false],
        [false, false, false],
        [false, false, false],
    ]; // Initiales 3x3 Raster
    let rowLabels = ['A', 'B', 'C']; // Anfangszeilenbeschriftungen

    let editMode = false;
    let loading = true;
    let error = "";

    // Hilfsfunktion zum Generieren von Reihenlabels von 'A' bis maxRow
    function generateRowLabels(maxRow) {
        const labels = [];
        const maxCode = maxRow.charCodeAt(0);
        for (let code = 65; code <= maxCode; code++) {
            labels.push(String.fromCharCode(code));
        }
        return labels;
    }

    // Funktionen zum Bearbeiten des Grids
    function toggleCell(row, col) {
        if (editMode) {
            grid[row][col] = !grid[row][col];
            grid = [...grid]; // Reaktivität sicherstellen
        }
    }

    function toggleEditMode() {
        editMode = !editMode;
    }

    function toggleRow(row) {
        if (editMode) {
            const allActive = grid[row].every(cell => cell);
            grid[row] = grid[row].map(() => !allActive);
            grid = [...grid]; // Reaktivität sicherstellen
        }
    }

    function toggleColumn(col) {
        if (editMode) {
            const allActive = grid.every(row => row[col]);
            grid = grid.map(row => {
                row[col] = !allActive;
                return row;
            });
            grid = [...grid]; // Reaktivität sicherstellen
        }
    }

    function addRow() {
        if (editMode) {
            const lastLabel = rowLabels[rowLabels.length - 1];
            const newRowLabel = String.fromCharCode(lastLabel.charCodeAt(0) + 1); // 'D', 'E', ...
            const newRow = Array(grid[0].length).fill(false);
            grid = [...grid, newRow];
            rowLabels = [...rowLabels, newRowLabel];
        }
    }

    function addColumn() {
        if (editMode) {
            grid = grid.map(row => [...row, false]);
        }
    }

    function removeRow() {
        if (editMode && grid.length > 1) {
            const removedLabel = rowLabels.pop();
            grid.pop();
            grid = [...grid]; // Reaktivität sicherstellen

           
        }
    }

    function removeColumn() {
        if (editMode && grid[0].length > 1) {
            const removedColIndex = grid[0].length; // Spaltenindex vor dem Entfernen
            grid = grid.map(row => row.slice(0, -1));
            grid = [...grid]; // Reaktivität sicherstellen

        }
    }

    function getRowLabel(index) {
        return rowLabels[index];
    }

    async function submitChanges() {
        const auth = get(authStore);
        const token = auth.token;

        try {
            // Zeige den Ladebildschirm
            const loadingSwal = Swal.fire({
                title: 'Lädt...',
                text: 'Bitte warten, während die Änderungen verarbeitet werden...',
                icon: 'info',
                showConfirmButton: false,
                didOpen: () => {
                    Swal.showLoading();  // Zeigt den Ladeindikator
                },
            });

            // Lösche alle bestehenden Sitze für den Screen
            await deleteAllSeats(screenId, token);

            // Erstelle alle aktiven Sitze aus dem aktuellen Grid
            let selectedSeats = [];
            for (let rowIndex = 0; rowIndex < grid.length; rowIndex++) {
                for (let colIndex = 0; colIndex < grid[rowIndex].length; colIndex++) {
                    if (grid[rowIndex][colIndex]) {
                        const rowLabel = getRowLabel(rowIndex);
                        const seatNumber = colIndex + 1;
                        await createSeat(screenId, rowLabel, seatNumber, 'standard', token);
                        selectedSeats.push(`(${rowLabel},${seatNumber})`);
                    }
                }
            }

            // Schließe den Ladebildschirm und zeige die Erfolgsnachricht an
            loadingSwal.close();
            Swal.fire({
                title: "Erfolgreich",
                text: `Alle Änderungen wurden eingetragen. Ausgewählte Sitze: ${selectedSeats.join(', ')}`,
                icon: "success",
                timer: 2500,
                showConfirmButton: false,
            });
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
            const data = await fetchSeats(screenId, token);
            console.log('Fetched seats data:', data);

            if (data && data.seats && data.seats.length > 0) {
                // Bestimme die höchste Reihenbezeichnung
                const maxRow = data.seats.reduce((max, seat) => {
                    return seat.row > max ? seat.row : max;
                }, 'A');

                // Generiere alle Reihenlabels von 'A' bis maxRow
                rowLabels = generateRowLabels(maxRow);

                // Bestimme die maximale Spaltenanzahl
                const cols = Math.max(...data.seats.map(seat => seat.number));

                // Erweitere das Grid auf die aktuelle Anzahl von Reihen und Spalten
                grid = Array.from({ length: rowLabels.length }, (_, rowIndex) => {
                    return Array.from({ length: cols }, (_, colIndex) => {
                        const seat = data.seats.find(
                            s => s.row === rowLabels[rowIndex] && s.number === colIndex + 1
                        );
                        return seat ? true : false;
                    });
                });
            } else {
                // Falls keine Sitze vorhanden sind, initialisiere mit mindestens einer Reihe
                grid = [
                    [false, false, false],
                ];
                rowLabels = ['A'];
            }
        } catch (err) {
            console.error("Fehler beim Abrufen der Sitze:", err);
            error = err.message || "Ein Fehler ist aufgetreten. Bitte versuche es erneut.";
        } finally {
            loading = false;
        }
    });

    function logSelectedSeats() {
        let selectedSeats = [];

        // Durchlaufe alle Zeilen
        grid.forEach((row, rowIndex) => {
            row.forEach((cell, colIndex) => {
                if (cell) { // Wenn die Zelle aktiv ist
                    const rowLabel = getRowLabel(rowIndex); // Konvertiere Zeilenindex in Label (A, B, ...)
                    selectedSeats.push(`(${rowLabel},${colIndex + 1})`); // Füge die Sitzposition hinzu
                }
            });
        });

        // Ausgabe im gewünschten Format
        console.log(selectedSeats.join(', '));
        Swal.fire({
            title: "Ausgewählte Sitze",
            text: selectedSeats.join(', '),
            icon: "info",
            confirmButtonText: "OK",
        });
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

    .grid-container {
        display: grid;
        overflow-x: auto;
        justify-content: center;
        margin: 20px auto;
    }

    .column-labels {
        display: grid;
        grid-template-columns: 50px repeat(auto-fit, 50px);
        gap: 2px;
        /* margin-bottom: 10px; */
    }

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
        user-select: none;
    }

    .row {
        display: flex;
        align-items: center;
        /* margin-bottom: 5px; */
    }

    .row-selector {
        width: 50px;
        height: 50px;
        background-color: lightgray;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        font-weight: bold;
        border: 1px solid #ddd;
        /* margin-right: 5px; */
        user-select: none;
    }

    .cell {
        width: 50px;
        height: 50px;
        background-color: rgba(0, 255, 0, 0.2);
        border: 1px solid #ddd;
        cursor: pointer;
        transition: background-color 0.3s;
    }

    .cell.active {
        background-color: green;
    }

    .cell:hover:not(.active) {
        background-color: #a5d6a7;
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
        border: none;
        background-color: #1976d2;
        color: white;
        border-radius: 5px;
        transition: background-color 0.3s;
    }

    button:hover {
        background-color: #1565c0;
    }

    h1 {
        margin-top: 20px;
        margin-bottom: 10px;
    }

    .controls {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 10px;
    }

    /* Responsive Design */
    @media (max-width: 600px) {
        .cell, .row-selector, .column-selector {
            width: 40px;
            height: 40px;
        }

        button {
            padding: 8px 16px;
            font-size: 14px;
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
            <button on:click={submitChanges}>EINTRAGEN</button>
            <button on:click={toggleEditMode}>
                Bearbeitungsmodus: {editMode ? "Ein" : "Aus"}
            </button>
            <button on:click={addRow} disabled={!editMode}>Zeile hinzufügen</button>
            <button on:click={addColumn} disabled={!editMode}>Spalte hinzufügen</button>
            <button on:click={removeRow} disabled={!editMode || grid.length <= 1}>Zeile entfernen</button>
            <button on:click={removeColumn} disabled={!editMode || grid[0].length <= 1}>Spalte entfernen</button>
            <button on:click={logSelectedSeats}>Ausgewählte Sitze anzeigen</button>
        </div>
        <p> LEINWAND <br>
   _____________________________________ </p>

        <div class="grid-container">
            <!-- Spaltennummern -->
            <div
                class="column-labels"
                style="grid-template-columns: 50px repeat({grid[0].length}, 50px);"
            >
                <div></div>
                {#each grid[0] as _, colIndex}
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
                            class="cell {cell ? 'active' : ''}"
                            on:click={() => toggleCell(rowIndex, colIndex)}
                            title={`Reihe: ${getRowLabel(rowIndex)}, Sitz: ${colIndex + 1}`}
                        ></div>
                    {/each}
                </div>
            {/each}
        </div>
    {/if}

    <button on:click={() => navigate('/adminkinosaal')}>Zurück zu Überblick der Kinosäle</button>
</main>
