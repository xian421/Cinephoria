<!-- src/routes/Buchung.svelte -->
<script>
    import { onMount } from 'svelte';
    // @ts-ignore
    import { navigate } from 'svelte-routing';
    // @ts-ignore
    import Swal from 'sweetalert2';
    import { fetchSeatsForShowtime, createBooking, createPayPalOrder, capturePayPalOrder } from '../services/api.js';
    import { get } from 'svelte/store';
    import { authStore } from '../stores/authStore'; 

    export let showtime_id; // Wird aus der Route übergeben

    let seats = [];
    let isLoading = true;
    let error = null;

    let selectedSeats = [];

    // Neue Variable für gruppierte Sitzplätze
    let seatsByRow = {};

    // PayPal Client ID aus Umgebungsvariablen oder Backend beziehen
    // Für dieses Beispiel nehmen wir an, dass Sie sie als Umgebungsvariable bereitstellen
    const PAYPAL_CLIENT_ID = 'AXWfRwPPgPCoOBZzqI-r4gce1HuWZXDnFqUdES0bP8boKSv5KkkPvZrMFwcCDShXjC3aTdChUjOhwxhW'; // Ersetzen Sie dies durch Ihre tatsächliche Client ID

    onMount(async () => {
    isLoading = true;
    try {
        const token = get(authStore).token;

        // Hole die Sitzstatus für die Vorstellung
        const seatStatusData = await fetchSeatsForShowtime(showtime_id, token);
        const seatStatusSeats = seatStatusData.seats;

        // Nutze die vorhandenen Sitze aus seatStatusSeats
        seats = seatStatusSeats;

        // Gruppiere die Sitze mit Lücken
        seatsByRow = groupSeatsByRowWithGaps(seats);

        // Berechne Unterschiede (to_add und to_remove)
        const existingSeats = seats.map(seat => [seat.row, seat.number]); // Aktuelle Sitze
        const newSeats = /* hier neue Sitzplatzdaten einfügen */ [];

        const existingSet = new Set(existingSeats.map(([row, number]) => `${row}-${number}`));
        const newSet = new Set(newSeats.map(([row, number]) => `${row}-${number}`));

        const to_add = Array.from(newSet).filter(seat => !existingSet.has(seat));
        const to_remove = Array.from(existingSet).filter(seat => !newSet.has(seat));

        console.log('Hinzugefügte Sitze:', to_add);
        console.log('Entfernte Sitze:', to_remove);

        // Hier kannst du to_add und to_remove in die Datenbank schreiben, falls notwendig
        await updateSeatsInDatabase(to_add, to_remove, token);
    } catch (error) {
        console.error('Fehler beim Laden der Sitze:', error);
        error = error.message || 'Fehler beim Laden der Sitze.';
    } finally {
        isLoading = false;
    }
});



    // Funktion zum Gruppieren der Sitzplätze nach Reihen
    function groupSeatsByRowWithGaps(seats) {
    const rowsSet = new Set();
    const seatNumbersSet = new Set();

    // Sammle alle vorhandenen Reihen und Sitznummern
    seats.forEach(seat => {
        rowsSet.add(seat.row);
        seatNumbersSet.add(seat.number);
    });

    // Bestimme den Bereich aller Reihen und Sitznummern
    const allRowLabels = generateAllRowLabels(Array.from(rowsSet));
    const allSeatNumbers = generateAllSeatNumbers(Array.from(seatNumbersSet));

    // Erstelle eine Map für schnellen Zugriff auf Sitzdaten
    const seatMap = {};
    seats.forEach(seat => {
        seatMap[`${seat.row}-${seat.number}`] = seat;
    });

    // Baue den Sitzplan mit Platzhaltern für fehlende Sitze
    const rowsWithGaps = {};
    allRowLabels.forEach(rowLabel => {
        const rowSeats = [];
        allSeatNumbers.forEach(seatNumber => {
            const key = `${rowLabel}-${seatNumber}`;
            if (seatMap[key]) {
                rowSeats.push(seatMap[key]);
            } else {
                // Platzhalter für fehlenden Sitz einfügen
                rowSeats.push({ row: rowLabel, number: seatNumber, status: 'missing', seat_id: null });
            }
        });
        rowsWithGaps[rowLabel] = rowSeats;
    });

    console.log('rowsWithGaps:', rowsWithGaps);
    return rowsWithGaps;
}

// Hilfsfunktion zur Generierung aller Reihenbezeichnungen
function generateAllRowLabels(existingRows) {
    const minRowCharCode = Math.min(...existingRows.map(r => r.charCodeAt(0)));
    const maxRowCharCode = Math.max(...existingRows.map(r => r.charCodeAt(0)));
    const allRows = [];
    for (let code = minRowCharCode; code <= maxRowCharCode; code++) {
        allRows.push(String.fromCharCode(code));
    }
    return allRows;
}

// Hilfsfunktion zur Generierung aller Sitznummern
function generateAllSeatNumbers(existingSeatNumbers) {
    const minSeatNumber = Math.min(...existingSeatNumbers);
    const maxSeatNumber = Math.max(...existingSeatNumbers);
    const allSeatNumbers = [];
    for (let num = minSeatNumber; num <= maxSeatNumber; num++) {
        allSeatNumbers.push(num);
    }
    return allSeatNumbers;
}


    // Funktion zum Auswählen/Abwählen von Sitzplätzen
    function toggleSeatSelection(seat) {
        console.log('toggleSeatSelection aufgerufen für Sitz:', seat);
        if (seat.status !== 'available') {
            console.log('Sitz ist nicht verfügbar:', seat);
            return;
        }

        if (isSelected(seat.seat_id)) {
            // Sitzplatz abwählen
            selectedSeats = selectedSeats.filter(s => s.seat_id !== seat.seat_id);
        } else {
            // Sitzplatz auswählen
            selectedSeats = [...selectedSeats, seat];
        }
    }

    // Funktion zur Überprüfung, ob ein Sitz ausgewählt ist
    function isSelected(seat_id) {
        const result = selectedSeats.some(seat => seat.seat_id === seat_id);
        return result;
    }

    // Reaktives Statement zur Überwachung von selectedSeats
    $: console.log('Reaktives selectedSeats:', selectedSeats);

    // Funktion zur Bestätigung der Buchung mit PayPal
    async function confirmBooking(orderID) {
        if (selectedSeats.length === 0) {
            Swal.fire({
                title: "Keine Sitzplätze ausgewählt",
                text: "Bitte wähle mindestens einen Sitzplatz aus.",
                icon: "warning",
                confirmButtonText: "OK",
            });
            return;
        }

        try {
            const token = get(authStore).token;
            const seatIds = selectedSeats.map(seat => seat.seat_id);
            const booking = await createBooking(showtime_id, seatIds, token, orderID);
            Swal.fire({
                title: "Buchung erfolgreich",
                text: "Deine Tickets wurden erfolgreich gebucht.",
                icon: "success",
                confirmButtonText: "OK",
            }).then(() => {
                navigate('/'); // Zurück zur Startseite oder einer anderen Seite
            });
        } catch (err) {
            console.error('Fehler bei der Buchung:', err);
            Swal.fire({
                title: "Fehler",
                text: err.message || 'Es gab ein Problem bei der Buchung. Bitte versuche es erneut.',
                icon: "error",
                confirmButtonText: "OK",
            });
        }
    }

    // PayPal SDK laden und PayPal Buttons rendern
    onMount(() => {
        if (!PAYPAL_CLIENT_ID) {
            console.error('PayPal Client ID ist nicht gesetzt!');
            Swal.fire({
                title: "Fehler",
                text: 'PayPal Client ID ist nicht gesetzt.',
                icon: "error",
                confirmButtonText: "OK",
            });
            return;
        }

        const script = document.createElement('script');
        script.src = `https://www.paypal.com/sdk/js?client-id=${PAYPAL_CLIENT_ID}&currency=EUR`;
        script.addEventListener('load', () => {
            if (!window.paypal) {
                console.error('PayPal SDK konnte nicht geladen werden.');
                Swal.fire({
                    title: "Fehler",
                    text: 'PayPal SDK konnte nicht geladen werden.',
                    icon: "error",
                    confirmButtonText: "OK",
                });
                return;
            }

            window.paypal.Buttons({
                style: {
                    layout: 'vertical',
                    color:  'blue',
                    shape:  'rect',
                    label:  'paypal'
                },
                createOrder: async (data, actions) => {
                    if (selectedSeats.length === 0) {
                        Swal.fire({
                            title: "Keine Sitzplätze ausgewählt",
                            text: "Bitte wähle mindestens einen Sitzplatz aus.",
                            icon: "warning",
                            confirmButtonText: "OK",
                        });
                        throw new Error('Keine Sitzplätze ausgewählt');
                    }

                    try {
                        const token = get(authStore).token;
                        if (!token) {
                            throw new Error('Nicht authentifiziert');
                        }
                        const response = await createPayPalOrder(showtime_id, selectedSeats, token);
                        return response.orderID;
                    } catch (err) {
                        console.error('Fehler beim Erstellen der PayPal-Order:', err);
                        Swal.fire({
                            title: "Fehler",
                            text: 'Es gab ein Problem beim Erstellen der Zahlung. Bitte versuche es erneut.',
                            icon: "error",
                            confirmButtonText: "OK",
                        });
                        throw err;
                    }
                },
                onApprove: async (data, actions) => {
                    try {
                        const token = get(authStore).token;
                        if (!token) {
                            throw new Error('Nicht authentifiziert');
                        }
                        const captureResult = await capturePayPalOrder(data.orderID, token);
                        if (captureResult.status === 'COMPLETED') {
                            await confirmBooking(data.orderID);
                        } else {
                            throw new Error('Zahlung wurde nicht abgeschlossen.');
                        }
                    } catch (err) {
                        console.error('Fehler beim Abschließen der Zahlung:', err);
                        Swal.fire({
                            title: "Zahlungsfehler",
                            text: 'Es gab ein Problem beim Abschließen der Zahlung. Bitte versuche es erneut.',
                            icon: "error",
                            confirmButtonText: "OK",
                        });
                    }
                },
                onCancel: () => {
                    Swal.fire({
                        title: "Zahlung abgebrochen",
                        text: 'Die Zahlung wurde abgebrochen.',
                        icon: "info",
                        confirmButtonText: "OK",
                    });
                },
                onError: (err) => {
                    console.error('PayPal Fehler:', err);
                    Swal.fire({
                        title: "Zahlungsfehler",
                        text: 'Es gab ein Problem mit der Zahlung. Bitte versuche es erneut.',
                        icon: "error",
                        confirmButtonText: "OK",
                    });
                }
            }).render('#paypal-button-container');
        });
        document.body.appendChild(script);
    });
</script>

<style>
    .booking-container {
        padding: 2rem;
        font-family: Arial, sans-serif;
        max-width: 800px;
        margin: 0 auto;
    }

    .seating-chart {
        display: flex;
        flex-direction: column;
        gap: 10px;
        justify-items: center;
        margin-bottom: 2rem;
    }

    .seat-row {
        display: flex;
        justify-content: center;
        gap: 5px;
    }

    .seat {
        width: 40px;
        height: 40px;
        background-color: #f0f0f0;
        border-radius: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: background-color 0.3s, transform 0.2s;
        font-size: 0.8rem;
        position: relative;
        color: white;
    }

    .seat.available {
        background-color: #2ecc71;
    }

    .seat.unavailable {
        background-color: #e74c3c;
        cursor: not-allowed;
    }

    .seat:hover.available {
        transform: scale(1.1);
    }

    .seat.selected {
        background-color: #3498db;
    }

    .legend {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin-bottom: 2rem;
    }

    .legend-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .legend-box {
        width: 20px;
        height: 20px;
        border-radius: 4px;
    }

    .seat.placeholder {
    background-color: transparent;
    pointer-events: none;
    width: 40px;
    height: 40px;
}

.row-label {
    width: 20px;
    text-align: right;
    margin-right: 5px;
    font-weight: bold;
}


    /* Legendenboxen Farben zuweisen */
    .legend-box.available {
        background-color: #2ecc71;
    }

    .legend-box.selected {
        background-color: #3498db;
    }

    .legend-box.unavailable {
        background-color: #e74c3c;
    }

    /* Ursprünglicher Bestätigungsbutton ausgeblendet */
    .btn-confirm {
        display: none;
    }

    /* Responsive Anpassungen */
    @media (max-width: 600px) {
        .seat {
            width: 30px;
            height: 30px;
        }

        .legend {
            flex-direction: column;
            gap: 1rem;
        }
    }
</style>

<main class="booking-container">
    {#if isLoading}
        <p>Lade Sitzplätze...</p>
    {:else if error}
        <p class="error-message">{error}</p>
    {:else}
        <h1>Tickets für Vorstellung #{showtime_id}</h1>

        <!-- Legende -->
        <div class="legend">
            <div class="legend-item">
                <div class="legend-box available"></div>
                <span>Verfügbar</span>
            </div>
            <div class="legend-item">
                <div class="legend-box selected"></div>
                <span>Ausgewählt</span>
            </div>
            <div class="legend-item">
                <div class="legend-box unavailable"></div>
                <span>Nicht verfügbar</span>
            </div>
        </div>

    <!-- Sitzplan -->
<div class="seating-chart">
    {#each Object.keys(seatsByRow) as row}
        <div class="seat-row">
            <!-- Reihenlabel -->
            <div class="row-label">{row}</div>
            {#each seatsByRow[row] as seat (row + '-' + seat.number)}
                {#if seat.status !== 'missing'}
                    <div 
                        class="seat {seat.status} {isSelected(seat.seat_id) ? 'selected' : ''}" 
                        on:click={() => {
                            toggleSeatSelection(seat);
                        }}
                    >
                        {seat.number}
                    </div>
                {:else}
                    <div class="seat placeholder"></div>
                {/if}
            {/each}
        </div>
    {/each}
</div>


        <!-- PayPal Button Container -->
        
    {/if}
    Email: sb-ng2ae34511206@personal.example.com PW: gK|i4A?q
    <div id="paypal-button-container"></div>
</main>
