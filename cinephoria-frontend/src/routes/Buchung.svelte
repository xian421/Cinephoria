<!-- src/routes/Buchung.svelte -->
<script>
    import { onMount } from 'svelte';
    import { navigate } from 'svelte-routing';
    import Swal from 'sweetalert2';
    import { fetchSeatsForShowtime, createBooking } from '../services/api.js';
    import { get } from 'svelte/store';
    import { authStore } from '../stores/authStore'; 

    export let showtime_id; // Wird aus der Route übergeben

    let seats = [];
    let isLoading = true;
    let error = null;

    let selectedSeats = [];

    // Neue Variable für gruppierte Sitzplätze
    let seatsByRow = {};

    onMount(async () => {
        if (!showtime_id) {
            console.error('Keine Showtime-ID gefunden!');
            error = 'Keine Showtime-ID gefunden!';
            isLoading = false;
            return;
        }

        try {
            const token = get(authStore).token;
            const data = await fetchSeatsForShowtime(showtime_id, token);
            seats = data.seats; // Format: [{ seat_id, row, number, type, status }, ...]

            // Sitzplätze nach Reihen gruppieren
            seatsByRow = groupSeatsByRow(seats);
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
        if (seat.status !== 'available') return;

        if (isSelected(seat.seat_id)) {
            // Sitzplatz abwählen
            selectedSeats = selectedSeats.filter(s => s.seat_id !== seat.seat_id);
        } else {
            // Sitzplatz auswählen
            selectedSeats = [...selectedSeats, seat];
        }
    }

    // Funktion zum Bestätigen der Buchung
    async function confirmBooking() {
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
            const booking = await createBooking(showtime_id, seatIds, token);
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

    // Funktion zur Überprüfung, ob ein Sitz ausgewählt ist
    function isSelected(seat_id) {
        return selectedSeats.some(seat => seat.seat_id === seat_id);
    }
</script>



<style>
    .booking-container {
        padding: 2rem;
        font-family: Arial, sans-serif;
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

    .seat.selected {
        background-color: #3498db !important;
    }

    .seat:hover.available {
        transform: scale(1.1);
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

    .btn-confirm {
        display: block;
        margin: 0 auto;
        padding: 0.75rem 1.5rem;
        background-color: #3498db;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 1rem;
        transition: background-color 0.3s;
    }

    .btn-confirm:hover {
        background-color: #2980b9;
    }

    .error-message {
        color: red;
        text-align: center;
        margin-bottom: 1rem;
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
                    {#each seatsByRow[row] as seat}
                        <div 
                            class="seat {isSelected(seat.seat_id) ? 'selected' : ''} {seat.status}" 
                            on:click={() => toggleSeatSelection(seat)}
                        >
                            {seat.number}
                        </div>
                    {/each}
                </div>
            {/each}
        </div>

        <!-- Bestätigungsbutton -->
        <button class="btn-confirm" on:click={confirmBooking}>
            Buchung bestätigen
        </button>
    {/if}
</main>


