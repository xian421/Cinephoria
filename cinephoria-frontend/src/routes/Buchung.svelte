<!-- src/routes/Buchung.svelte -->
<script>
    import { onMount, tick } from 'svelte';
    import { navigate } from 'svelte-routing';
    import Swal from 'sweetalert2';
    import { fetchSeatsForShowtime, createBooking, createPayPalOrder, capturePayPalOrder, fetchSeatTypes } from '../services/api.js';
    import { get } from 'svelte/store';
    import { authStore } from '../stores/authStore'; 
    import "@fortawesome/fontawesome-free/css/all.min.css";

    export let showtime_id; // Wird aus der Route übergeben

    let seats = [];
    let isLoading = true;
    let error = null;

    let selectedSeats = [];

    // Variable für gruppierte Sitzplätze
    let seatsByRow = {};

    // Gesamtpreis der ausgewählten Sitzplätze
    let totalPrice = 0.00;

    // PayPal Client ID aus Umgebungsvariablen oder Backend beziehen
    const PAYPAL_CLIENT_ID = 'AXWfRwPPgPCoOBZzqI-r4gce1HuWZXDnFqUdES0bP8boKSv5KkkPvZrMFwcCDShXjC3aTdChUjOhwxhW'; // Ersetzen Sie dies durch Ihre tatsächliche Client ID

    // Liste aller Sitztypen laden (inkl. color & icon)
    let seatTypesList = [];

    // Referenz zum PayPal-Button-Container
    let paypalContainer;

    // Variable, um zu verhindern, dass PayPal-Buttons mehrfach initialisiert werden
    let payPalInitialized = false;

    onMount(async () => {
        isLoading = true;
        try {
            const token = get(authStore).token;

            // Zuerst Sitztypen laden
            seatTypesList = await fetchSeatTypes(token);

            // Hole die Sitzstatus für die Vorstellung
            const seatStatusData = await fetchSeatsForShowtime(showtime_id, token);
            const seatStatusSeats = seatStatusData.seats;

            // Nutze die vorhandenen Sitze aus seatStatusSeats
            seats = seatStatusSeats;

            // Gruppiere die Sitze mit Lücken
            seatsByRow = groupSeatsByRowWithGaps(seats);

        } catch (error) {
            console.error('Fehler beim Laden der Sitze oder Sitztypen:', error);
            error = error.message || 'Fehler beim Laden der Sitze oder Sitztypen.';
        } finally {
            isLoading = false;
            await tick(); // Warten, bis der DOM aktualisiert ist
            if (!payPalInitialized) {
                initializePayPalButtons();
                payPalInitialized = true;
            }
        }
    });

    function getSeatTypeColor(typeName) {
        const type = seatTypesList.find(st => st.name === typeName);
        return type ? type.color : '#678be0'; // Standardfarbe, falls nicht gefunden
    }

    // Funktion, um das Icon eines Sitztyps zu bekommen
    function getSeatTypeIcon(typeName) {
        const type = seatTypesList.find(st => st.name === typeName);
        return type ? type.icon : null;
    }

    function initializePayPalButtons() {
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

        // Überprüfen, ob das PayPal-SDK bereits geladen wurde
        if (window.paypal) {
            renderPayPalButtons();
        } else {
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
                renderPayPalButtons();
            });
            document.body.appendChild(script);
        }
    }

    function renderPayPalButtons() {
        if (!paypalContainer) {
            console.error('Element #paypal-button-container existiert nicht im DOM.');
            Swal.fire({
                title: "Zahlungsfehler",
                text: 'Es gab ein Problem mit der Zahlung. Bitte versuche es erneut.',
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
        }).render(paypalContainer); // Verwende die gebundene Referenz
    }

    // Funktion zum Gruppieren der Sitzplätze nach Reihen mit Platzhaltern für fehlende Sitze
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
                    rowSeats.push({ row: rowLabel, number: seatNumber, status: 'missing', seat_id: null, type: null, price: 0.00 });
                }
            });
            rowsWithGaps[rowLabel] = rowSeats;
        });

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
        if (seat.status !== 'available') {
            return;
        }

        if (isSelected(seat.seat_id)) {
            // Sitzplatz abwählen
            selectedSeats = selectedSeats.filter(s => s.seat_id !== seat.seat_id);
        } else {
            // Sitzplatz auswählen
            selectedSeats = [...selectedSeats, seat];
        }

        // Gesamtpreis neu berechnen
        calculateTotalPrice();
    }

    // Funktion zur Berechnung des Gesamtpreises
    function calculateTotalPrice() {
        totalPrice = selectedSeats.reduce((sum, seat) => sum + seat.price, 0);
    }

    // Funktion zur Überprüfung, ob ein Sitz ausgewählt ist
    function isSelected(seat_id) {
        return selectedSeats.some(seat => seat.seat_id === seat_id);
    }

    // Reaktives Statement zur Überwachung von selectedSeats
    $: if (selectedSeats) {
        console.log('Ausgewählte Sitze:', selectedSeats);
    }

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
        align-items: center;
    }

    .seat {
        width: 40px;
        height: 40px;
        background-color: rgb(103, 139, 224); /* Einheitliche Grundfarbe */
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

    .seat.selected {
        background-color: #2ecc71 !important; /* Grüner Hintergrund für ausgewählte Sitze */
    }

    .seat.selected:before {
        content: "\f007"; /* Unicode für das Icon */
        font-family: "Font Awesome 5 Free";
        font-weight: 900; /* Fett für das Icon */
    }

    .seat.vip {
        background-color: rgb(140, 76, 140);
    }

    .seat.wheelchair {
        font-size: 24px; /* Größere Schriftgröße für Icons */
    }

    .seat.placeholder {
        background-color: transparent;
        pointer-events: none;
        width: 40px;
        height: 40px;
    }

    .seat:hover.available {
        transform: scale(1.1);
    }

    .legend {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin-bottom: 2rem;
        flex-wrap: wrap;
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
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
    }

    .row-label {
        width: 20px;
        text-align: right;
        margin-right: 5px;
        font-weight: bold;
    }

    .error-message {
        color: red;
        font-weight: bold;
        text-align: center;
    }

    .button-container {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-bottom: 2rem;
    }

    .legend-box.available {
        background-color: #3498db;
    }

    .legend-box.selected {
        background-color: #2ecc71;
    }
    .legend-box.selected::before {
        content: "\f007"; /* Unicode für das Icon */
        font-family: "Font Awesome 5 Free";
        font-weight: 900; /* Fett für das Icon */
    }

    .legend-box.unavailable {
        background-color: rgb(186, 186, 186);
    }

    .legend-box.unavailable::before {
        content: "\f007"; /* Unicode für das Icon */
        font-family: "Font Awesome 5 Free";
        font-weight: 900; /* Fett für das Icon */
    }

    .seat.unavailable {
        background-color: #7f8c8d !important; /* Grauer Hintergrund für nicht verfügbare Sitze */
        cursor: not-allowed;
    }

    /* Dynamische Legenden für Sitztypen */
    .legend-box.type {
        width: 20px;
        height: 20px;
        border-radius: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        margin-right: 5px;
    }

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
            <!-- Generische Legenden für Sitzstatus -->
            <div class="legend-item">
                <div class="legend-box selected"></div>
                <span>Ausgewählt</span>
            </div>
            <div class="legend-item">
                <div class="legend-box unavailable"></div>
                <span>Besetzt</span>
            </div>

            <!-- Dynamische Legenden für Sitztypen -->
            {#each seatTypesList as seatType}
                <div class="legend-item">
                    <div 
                        class="legend-box type" 
                        style="background-color: {seatType.color};"
                        title={seatType.name}
                    >
                        {#if seatType.icon}
                            <i class={`fas ${seatType.icon}`} style="color: white;"></i>
                        {/if}
                    </div>
                    <span>{`${seatType.name} ab ${seatType.price} €`}</span>
                </div>
            {/each}
        </div>

        <!-- Sitzplan -->
        <div class="seating-chart">
            {#each Object.keys(seatsByRow) as row}
                <div class="seat-row">
                    <!-- Reihenlabel -->
                    <div class="row-label">{row}</div>
                    <!-- Sitzplätze -->
                    {#each seatsByRow[row] as seat (row + '-' + seat.number)}
                        {#if seat.status !== 'missing'}
                            <div 
                                class="seat {seat.status} {seat.type} {isSelected(seat.seat_id) ? 'selected' : ''}" 
                                on:click={() => toggleSeatSelection(seat)}
                                title={`Reihe ${seat.row}, Sitz ${seat.number}${seat.type ? `, Typ: ${seat.type}, Preis: ${seat.price.toFixed(2)}€` : ''}`}
                                style={seat.type ? `background-color: ${getSeatTypeColor(seat.type)};` : ''}
                            >
                                {#if seat.status === 'unavailable'}
                                    <!-- Icon für besetzte Sitze -->
                                    <i class="fas fa-user"></i>
                                {:else if seat.type && getSeatTypeIcon(seat.type)}
                                    <!-- Icon basierend auf dem Sitztyp -->
                                    <i class={`fas ${getSeatTypeIcon(seat.type)}`}></i>
                                {:else if seat.status === 'selected'}
                                    <!-- Optional: Icon für ausgewählte Sitze -->
                                    <i class="fas fa-check"></i>
                                {:else}
                                    {seat.number}
                                {/if}
                            </div>
                        {:else}
                            <div class="seat placeholder"></div>
                        {/if}
                    {/each}
                </div>
            {/each}
        </div>

        <!-- Anzeige des Gesamtpreises -->
        <p>Gesamtpreis: {totalPrice.toFixed(2)}€</p>

        <!-- PayPal Button Container -->
        <div id="paypal-button-container" bind:this={paypalContainer}></div>
    {/if}
</main>
