<!-- src/routes/Adminseats.svelte -->
<script>
    import { onMount } from "svelte";
    import { fetchSeats, batchUpdateSeats } from '../services/api.js';
    import { navigate } from "svelte-routing";
    import { get } from 'svelte/store';
    import { authStore } from '../stores/authStore.js';
    import Swal from 'sweetalert2';
    import "@fortawesome/fontawesome-free/css/all.min.css";


    export let screenId; 

    // Modus: 'add' oder 'edit' abgeleitet von isEditMode (Boolean)
    let isEditMode = false; // Standardmäßig im Hinzufügen-Modus
    const mode = () => isEditMode ? 'Aktiver Modus: Bearbeiten' : 'Aktiver Modus: Hinzufügen/Löschen';

    // Grid: 2D-Array mit Sitztypen ('standard', 'wheelchair', 'vip' oder null)
    let grid = [
        [null, null, null],
        [null, null, null],
        [null, null, null],
    ];

    let rowLabels = ['A', 'B', 'C']; // Anfangszeilenbeschriftungen

    let loading = true;
    let error = "";

    // Map zur Speicherung der ursprünglichen Sitzdaten: "A,1" -> 'standard'
    let originalSeats = new Map();

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
        if (!isEditMode) {
            // Hinzufügen-Modus: Toggle zwischen 'standard' und null
            grid[row][col] = grid[row][col] ? null : 'standard';
        } else {
            // Bearbeiten-Modus: Zyklische Änderung der Sitztypen
            if (grid[row][col]) {
                switch (grid[row][col]) {
                    case 'standard':
                        grid[row][col] = 'wheelchair';
                        break;
                    case 'wheelchair':
                        grid[row][col] = 'vip';
                        break;
                    case 'vip':
                        grid[row][col] = 'standard';
                        break;
                    default:
                        grid[row][col] = 'standard';
                }
            }
        }
        grid = [...grid]; // Reaktivität sicherstellen
    }

    function toggleMode() {
        isEditMode = !isEditMode;
    }

    function toggleRow(row) {
        if (!isEditMode) {
            // Hinzufügen-Modus: Toggle ganze Reihe zwischen 'standard' und null
            const allActive = grid[row].every(cell => cell);
            grid[row] = grid[row].map(() => allActive ? null : 'standard');
            grid = [...grid];
        }
    }

    function toggleColumn(col) {
        if (!isEditMode) {
            // Hinzufügen-Modus: Toggle ganze Spalte zwischen 'standard' und null
            const allActive = grid.every(row => row[col]);
            grid = grid.map(row => {
                row[col] = allActive ? null : 'standard';
                return row;
            });
            grid = [...grid];
        }
    }

    function addRow() {
        if (!isEditMode) {
            const lastLabel = rowLabels[rowLabels.length - 1];
            const newRowLabel = String.fromCharCode(lastLabel.charCodeAt(0) + 1); // 'D', 'E', ...
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
            grid = [...grid]; // Reaktivität sicherstellen
        }
    }

    function removeColumn() {
        if (!isEditMode && grid[0].length > 1) {
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

            // Aktuelle Sitzdaten basierend auf dem Grid ermitteln
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

            // Sitze zum Hinzufügen: In currentSeats, aber nicht in originalSeats
            let seatsToAdd = [];
            currentSeats.forEach((type, seat) => {
                if (!originalSeats.has(seat)) {
                    const [row, number] = seat.split(',');
                    seatsToAdd.push({ row, number: parseInt(number, 10), type });
                }
            });

            // Sitze zum Löschen: In originalSeats, aber nicht in currentSeats
            let seatsToDelete = [];
            originalSeats.forEach((type, seat) => {
                if (!currentSeats.has(seat)) {
                    const [row, number] = seat.split(',');
                    seatsToDelete.push({ row, number: parseInt(number, 10) });
                }
            });

            // Sitze, deren Typ sich geändert hat
            let seatsToUpdate = [];
            currentSeats.forEach((type, seat) => {
                if (originalSeats.has(seat) && originalSeats.get(seat) !== type) {
                    const [row, number] = seat.split(',');
                    seatsToUpdate.push({ row, number: parseInt(number, 10), type });
                }
            });

            // Logge die zu addierenden, zu löschenden und zu aktualisierenden Sitze
            console.log("Zu addierende Sitze:", seatsToAdd);
            console.log("Zu löschende Sitze:", seatsToDelete);
            console.log("Zu aktualisierende Sitze:", seatsToUpdate);

            // Sende die Änderungen an das Backend
            const result = await batchUpdateSeats(screenId, seatsToAdd, seatsToDelete, seatsToUpdate);

            // Schließe den Ladebildschirm und zeige die Erfolgsnachricht an
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

            // Aktualisiere originalSeats mit den neuen Daten
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
                        if (seat) {
                            // Füge das Sitz-Tuple zum originalSeats Map hinzu
                            originalSeats.set(`${seat.row},${seat.number}`, seat.type);
                            return seat.type;
                        }
                        return null;
                    });
                });
            } else {
                // Falls keine Sitze vorhanden sind, initialisiere mit mindestens einer Reihe
                grid = [
                    [null, null, null],
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
</script>

<style>
    /* Dein bestehendes CSS bleibt größtenteils unverändert */
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
        user-select: none;
    }

    .cell {
        width: 50px;
        height: 50px;
        border: 1px solid #ddd;
        cursor: pointer;
        transition: background-color 0.3s;
    }

    /* Sitztypen-Farben */
    .cell.standard {
        background-color: rgb(103, 139, 224);
    }

    /* Entfernen Sie die Hintergrundfarbe für Rollstuhlplätze */
    .cell.wheelchair {
        background-color: rgb(103, 139, 224);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px; /* Größe des Icons anpassen */
    }

    /* Optional: Stil für 'null' Zellen anpassen, falls erforderlich */
    .cell.null {
        background-color: rgba(0, 0, 0, 0.05);
    }


    .cell.vip {
        background-color: rgb(140, 76, 140);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px; 
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

    .add-buttons {
        background-color: rgb(0, 114, 28);
    }

    .remove-buttons {
        background-color: darkred;
    }

    .submit-button {
        background-color: white;
        color: black;
        border: 3px solid #1976d2;
        font-weight: bold;
        font-size: 18px;
        font-family: Arial, sans-serif;
    }
    
    /* Hinzufügen von Styles für den Switch */



    #screen-label {
        font-size: 1.5rem;
        font-weight: bold;
        margin: 10px;
    }

    .Testklasse {
        width: 5000px;
        font-size: 1.5rem;
        font-weight: bold;
        margin: 10px;
    }


        /* Stil für den Modus-Switch-Container */
    .mode-switch {
        display: flex;
        align-items: center;
        gap: 15px; 
        margin: 20px 0; 
    }

    /* Stil für die Modus-Beschriftung */
    .mode-label {
        font-size: 18px;
        font-weight: bold;
        color: #333;
    }

    /* Stil für den Switch */
    .switch {
        position: relative;
        display: inline-block;
        width: 60px;
        height: 30px;
    }

    .switch input {
        opacity: 0;
        width: 0;
        height: 0;
    }

    .slider {
        position: absolute;
        cursor: pointer;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: green;
        transition: 0.4s;
        border-radius: 30px;
    }

    .slider:before {
        position: absolute;
        content: "";
        height: 24px;
        width: 24px;
        left: 3px;
        bottom: 3px;
        background-color: white;
        transition: 0.4s;
        border-radius: 50%;
    }

    input:checked + .slider {
        background-color: #1976d2;
    }

    input:checked + .slider:before {
        transform: translateX(30px);
    }

    /* Optional: Hover-Effekt */
    .switch:hover .slider {
        transform: scale(1.05);
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
            <button on:click={submitChanges} class="submit-button">EINTRAGEN</button>
           
            
            <button on:click={addRow} class="add-buttons" disabled={isEditMode}>Zeile hinzufügen</button>
            <button on:click={addColumn} class="add-buttons" disabled={isEditMode}>Spalte hinzufügen</button>
            <button on:click={removeRow} class="remove-buttons" disabled={isEditMode || grid.length <= 1}>Zeile entfernen</button>
            <button on:click={removeColumn} class="remove-buttons" disabled={isEditMode || grid[0].length <= 1}>Spalte entfernen</button>
        </div>
        <!-- Modus-Switch -->
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
                            class="cell {cell.type || 'null'}"
                            on:click={() => toggleCell(rowIndex, colIndex)}
                            title={`Reihe: ${getRowLabel(rowIndex)}, Sitz: ${colIndex + 1}${cell.type ? `, Typ: ${cell.type}, Preis: ${cell.price}€` : ''}`}
                        >
                        {#if cell === 'wheelchair'}
                            <i class="fas fa-wheelchair"></i>
                        {:else if cell === 'vip'}
                            <i class="fas fa-star"></i>
                        {:else if cell === 'standard'}
                            <!-- Optional: Standard-Sitzsymbol oder Farbe -->
                            <div class="standard-seat"></div>
                        {/if}
                        </div>
                    {/each}

                </div>
            {/each}
        </div>
    {/if}

    <button on:click={() => navigate('/adminkinosaal')}>Zurück zu Überblick der Kinosäle</button>
</main>
