<!-- <div class="seat-map">
    <div class="row" data-row="A">
      <div class="seat" data-seat="1"></div>
      <div class="seat reserved" data-seat="2"></div>
      <div class="seat" data-seat="3"></div>
      <div class="seat" data-seat="4"></div>
    </div>
    <div class="row" data-row="B">
      <div class="seat" data-seat="1"></div>
      <div class="seat reserved" data-seat="2"></div>
      <div class="seat" data-seat="3"></div>
      <div class="seat" data-seat="4"></div>
    </div>
  </div>

<style>
  .seat-map {
    display: grid;
    gap: 10px;
  }
  
  .row {
    display: flex;
    justify-content: center;
  }
  
  .seat {
    width: 30px;
    height: 30px;
    background-color: #2b6802;
    border-radius: 5px;
    cursor: pointer;
  }
  
  .seat.reserved {
    background-color: #f44336;
    cursor: not-allowed;
  }
  
  .seat:hover:not(.reserved) {
    background-color: #ffeb3b;
  }
</style> -->


<script>
    let grid = [
        [false, false, false],
        [false, false, false],
        [false, false, false],
      //  [false, false, false],
    ]; // Start mit 4x3 Raster
    let editMode = false;

    function toggleCell(row, col) {
        if (editMode) {
            grid[row][col] = !grid[row][col];
        }
    }

    function toggleEditMode() {
        editMode = !editMode;
    }

    function toggleRow(row) {
        if (editMode) {
            const allActive = grid[row].every(cell => cell);
            grid[row] = grid[row].map(() => !allActive);
        }
    }

    function toggleColumn(col) {
        if (editMode) {
            const allActive = grid.every(row => row[col]);
            grid = grid.map(row => {
                row[col] = !allActive;
                return row;
            });
        }
    }

    function addRow() {
        const newRow = Array(grid[0].length).fill(false);
        grid = [newRow, ...grid];
    }

    function addColumn() {
        grid = grid.map(row => [...row, false]);
    }

    function removeRow() {
        if (grid.length > 1) {
            grid = grid.slice(1);
        }
    }

    function removeColumn() {
        if (grid[0].length > 1) {
            grid = grid.map(row => row.slice(0, -1));
        }
    }

    function getRowLabel(index) {
        const charCode = 65 + (grid.length - 1 - index);
        return String.fromCharCode(charCode);
    }



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
    console.log(selectedSeats.join(''));
}

</script>

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

    .row {
        display: flex;
        align-items: center;
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
        background-color: rgba(0, 255, 0, 0.2);
        border: 1px solid #ddd;
        cursor: pointer;
    }

    .cell.active {
        background-color: green;
    }

    .column-labels {
        display: grid;
        grid-template-columns: 50px repeat(auto-fit, 50px); /* Platzhalter links */
        gap: 2px;
        /* margin-bottom: 2px; */
    }

    button {
        margin: 10px;
        padding: 10px 20px;
        font-size: 16px;
        cursor: pointer;
    }
</style>

<main>
    <h1>Kinositz-Editor</h1>
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
                    ></div>
                {/each}
            </div>
        {/each}
    </div>
</main>

