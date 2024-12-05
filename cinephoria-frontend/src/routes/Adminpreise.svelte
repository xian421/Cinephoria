<!-- /src/routes/Adminpreise.svelte -->
<script>
    import { onMount } from 'svelte';
    import { navigate } from 'svelte-routing';
    import Swal from 'sweetalert2';

    // Fake-Daten für die Sitztypen und ihre aktuellen Preise
    let seatTypes = [
        { type: 'standard', label: 'Standard', price: 10.00 },
        { type: 'wheelchair', label: 'Rollstuhl', price: 8.00 },
        { type: 'vip', label: 'VIP', price: 15.00 },
    ];

    // Funktion zum Aktualisieren des Preises eines Sitztyps
    function updatePrice(index, event) {
        const value = parseFloat(event.target.value);
        if (!isNaN(value) && value >= 0) {
            seatTypes[index].price = value;
        } else {
            // Fehlerbehandlung bei ungültiger Eingabe
            Swal.fire({
                title: 'Ungültiger Wert',
                text: 'Bitte geben Sie einen gültigen Preis ein.',
                icon: 'error',
                confirmButtonText: 'OK',
            });
        }
    }

    // Funktion zum Speichern der Preise (aktuell nur eine Simulation)
    function savePrices() {
        // Hier würden Sie normalerweise die Preise an das Backend senden
        // Da wir mit Fake-Daten arbeiten, zeigen wir nur eine Erfolgsnachricht an
        Swal.fire({
            title: 'Erfolgreich',
            text: 'Die Preise wurden erfolgreich gespeichert.',
            icon: 'success',
            confirmButtonText: 'OK',
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

    h1 {
        margin-bottom: 20px;
    }

    table {
        border-collapse: collapse;
        width: 100%;
        max-width: 600px;
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

    input[type="number"] {
        width: 100px;
        padding: 8px;
        margin-right: 10px;
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

    @media (max-width: 600px) {
        input[type="number"] {
            width: 80px;
        }

        button {
            padding: 8px 16px;
            font-size: 14px;
        }
    }
</style>

<main>
    <h1>Preisverwaltung für Sitztypen</h1>

    <table>
        <thead>
            <tr>
                <th>Sitztyp</th>
                <th>Aktueller Preis (€)</th>
            </tr>
        </thead>
        <tbody>
            {#each seatTypes as seat, index}
                <tr>
                    <td>{seat.label}</td>
                    <td>
                        <input
                            type="number"
                            min="0"
                            step="0.01"
                            value={seat.price}
                            on:change={(event) => updatePrice(index, event)}
                        />
                    </td>
                </tr>
            {/each}
        </tbody>
    </table>

    <div class="button-container">
        <button on:click={savePrices}>Speichern</button>
        <button on:click={() => navigate('/admin')}>Zurück zum Adminbereich</button>
    </div>
</main>
