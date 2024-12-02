<!-- src/routes/Buchung.svelte -->
<script>
    import { onMount } from 'svelte';
    import { navigate } from 'svelte-routing';
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
        console.log('onMount gestartet');
        if (!showtime_id) {
            console.error('Keine Showtime-ID gefunden!');
            error = 'Keine Showtime-ID gefunden!';
            isLoading = false;
            return;
        }

        try {
            const token = get(authStore).token;
            const data = await fetchSeatsForShowtime(showtime_id, token);
            console.log('Empfangene Sitzplätze:', data.seats);
            seats = data.seats; // Format: [{ seat_id, row, number, type, status }, ...]
            console.log('Zugewiesene Sitzplätze:', seats);

            // Sitzplätze nach Reihen gruppieren
            seatsByRow = groupSeatsByRow(seats);
            console.log('Sitzplätze nach Reihen gruppiert:', seatsByRow);
        } catch (err) {
            console.error('Netzwerkfehler:', err);
            error = 'Netzwerkfehler. Bitte versuche es erneut.';
            Swal.fire({
                title: "Fehler",
                text: error,
                icon: "error",
                confirmButtonText: "OK",
            });
        } finally {
            isLoading = false;
            console.log('isLoading auf false gesetzt');
        }
    });

    // Funktion zum Gruppieren der Sitzplätze nach Reihen
    function groupSeatsByRow(seats) {
        const rows = {};
        seats.forEach(seat => {
            if (!rows[seat.row]) {
                rows[seat.row] = [];
            }
            rows[seat.row].push(seat);
        });

        // Sitzplätze innerhalb jeder Reihe nach Nummer sortieren
        for (let row in rows) {
            rows[row].sort((a, b) => a.number - b.number);
        }

        // Reihen nach Reihenbezeichnung sortieren
        const sortedRows = {};
        Object.keys(rows).sort().forEach(key => {
            sortedRows[key] = rows[key];
        });

        return sortedRows;
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
            console.log('Sitzplatz abgewählt:', seat.seat_id);
        } else {
            // Sitzplatz auswählen
            selectedSeats = [...selectedSeats, seat];
            console.log('Sitzplatz ausgewählt:', seat.seat_id);
        }
        console.log('Aktuelle selectedSeats:', selectedSeats);
    }

    // Funktion zur Überprüfung, ob ein Sitz ausgewählt ist
    function isSelected(seat_id) {
        const result = selectedSeats.some(seat => seat.seat_id === seat_id);
        console.log(`isSelected(${seat_id}):`, result);
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
                    {#each seatsByRow[row] as seat (seat.seat_id)}
                        <div 
                            class="seat {seat.status} {isSelected(seat.seat_id) ? 'selected' : ''}" 
                            on:click={() => {
                                toggleSeatSelection(seat);
                                console.log('Seat clicked:', seat);
                            }}
                        >
                            {seat.number}
                        </div>
                    {/each}
                </div>
            {/each}
        </div>

        <!-- PayPal Button Container -->
        
    {/if}
    <div id="paypal-button-container"></div>
</main>
