<!-- src/routes/Buchung.svelte -->
<script>
    import { onMount, onDestroy, tick } from 'svelte';
    import { navigate } from 'svelte-routing';
    import Swal from 'sweetalert2';
    import { 
        createBooking, 
        createPayPalOrder, 
        capturePayPalOrder, 
        fetchSeatTypes,
        fetchSeatsWithReservation
    } from '../services/api.js';
    import { get } from 'svelte/store';
    import { authStore } from '../stores/authStore'; 
    import { cart, cartError, addToCart, removeFromCart, clearCart, loadCart } from '../stores/cartStore.js';

    import "@fortawesome/fontawesome-free/css/all.min.css";

    export let showtime_id;

    let seats = [];
    let isLoading = true;
    let error = null;
    let seatTypesList = [];
    let seatsByRow = {};
    let payPalInitialized = false;
    let paypalContainer;

    let totalPrice = 0.0;
    let timer = null;
    let timeLeft = 0; // in Sekunden
    let warning = false;

    const PAYPAL_CLIENT_ID = 'AXWfRwPPgPCoOBZzqI-r4gce1HuWZXDnFqUdES0bP8boKSv5KkkPvZrMFwcCDShXjC3aTdChUjOhwxhW';

    // Reaktive Abhängigkeiten mit direkter Zuweisung
    $: totalPrice = $cart.reduce((sum, seat) => sum + seat.price, 0);

    $: {
        if ($cart.length === 0) {
            timeLeft = 0;
            warning = false;
        } else {
            const now = new Date();
            const reservationTimes = $cart.map(seat => new Date(seat.reserved_until));
            const earliest = new Date(Math.min(...reservationTimes));
            timeLeft = Math.max(0, Math.floor((earliest - now) / 1000));
            warning = timeLeft <= 60;
        }
    }

    $: {
        clearInterval(timer);
        if (timeLeft > 0) {
            timer = setInterval(() => {
                if (timeLeft > 0) {
                    timeLeft -= 1;
                }
                if (timeLeft === 60 && !warning) {
                    showWarning();
                }
                if (timeLeft <= 0) {
                    clearInterval(timer);
                    loadCart(); // Aktualisiere den Warenkorb, um abgelaufene Sitze zu entfernen
                }
            }, 1000);
        }
    }

    // Reaktive Fehleranzeige mit angepasstem SweetAlert
    $: if ($cartError) {
        Swal.fire({
            title: "Fehler",
            text: $cartError,
            icon: "error",
            confirmButtonText: "Neu Laden",
            allowOutsideClick: false, // Optional: Verhindert das Schließen durch Klicken außerhalb
        }).then(async (result) => {
            if (result.isConfirmed) {
                await loadCart();
                await loadSeats(); // Aktualisiert die Sitzplatzkarte
            }
            cartError.set(null); // Setzt den Fehler zurück
        });
    }

    onMount(async () => {
        isLoading = true;
        try {
            await loadSeats();
            // Warenkorb laden, damit $cart aktuell ist
            await loadCart();
        } catch (err) {
            console.error('Fehler beim Laden der Sitze oder Sitztypen:', err);
            error = err.message || 'Fehler beim Laden.';
        } finally {
            isLoading = false;
            await tick(); // Warten, bis DOM-Änderungen abgeschlossen sind
            if (!payPalInitialized) {
                initializePayPalButtons();
                payPalInitialized = true;
            }
        }
    });

    onDestroy(() => {
        clearInterval(timer);
    });

    // Funktion zum Laden der Sitzplatzdaten
    async function loadSeats() {
        try {
            const token = get(authStore).token;
            let guest_id = localStorage.getItem('guest_id') || crypto.randomUUID();
            localStorage.setItem('guest_id', guest_id);

            seatTypesList = await fetchSeatTypes(token);
            const seatData = await fetchSeatsWithReservation(showtime_id, token, guest_id);
            seats = seatData.seats;
            seatsByRow = groupSeatsByRowWithGaps(seats);
        } catch (err) {
            console.error('Fehler beim Laden der Sitze oder Sitztypen:', err);
            error = err.message || 'Fehler beim Laden.';
        }
    }

    function groupSeatsByRowWithGaps(seats) {
        const rowsSet = new Set();
        const seatNumbersSet = new Set();
        seats.forEach(seat => {
            rowsSet.add(seat.row);
            seatNumbersSet.add(seat.number);
        });

        const allRowLabels = generateAllRowLabels(Array.from(rowsSet));
        const allSeatNumbers = generateAllSeatNumbers(Array.from(seatNumbersSet));

        const seatMap = {};
        seats.forEach(seat => {
            seatMap[`${seat.row}-${seat.number}`] = seat;
        });

        const rowsWithGaps = {};
        allRowLabels.forEach(rowLabel => {
            const rowSeats = [];
            allSeatNumbers.forEach(num => {
                const key = `${rowLabel}-${num}`;
                if (seatMap[key]) {
                    rowSeats.push(seatMap[key]);
                } else {
                    rowSeats.push({ row: rowLabel, number: num, status: 'missing', seat_id: null, type: null, price: 0.00 });
                }
            });
            rowsWithGaps[rowLabel] = rowSeats;
        });
        return rowsWithGaps;
    }

    function generateAllRowLabels(existingRows) {
        if (existingRows.length === 0) return [];
        const minRowCharCode = Math.min(...existingRows.map(r => r.charCodeAt(0)));
        const maxRowCharCode = Math.max(...existingRows.map(r => r.charCodeAt(0)));
        const allRows = [];
        for (let code = minRowCharCode; code <= maxRowCharCode; code++) {
            allRows.push(String.fromCharCode(code));
        }
        return allRows;
    }

    function generateAllSeatNumbers(existingNumbers) {
        if (existingNumbers.length === 0) return [];
        const min = Math.min(...existingNumbers);
        const max = Math.max(...existingNumbers);
        const all = [];
        for (let i = min; i <= max; i++) {
            all.push(i);
        }
        return all;
    }

    function getSeatTypeColor(typeName) {
        const type = seatTypesList.find(st => st.name === typeName);
        return type ? type.color : '#678be0';
    }

    function getSeatTypeIcon(typeName) {
        const type = seatTypesList.find(st => st.name === typeName);
        return type ? type.icon : null;
    }

    // Funktion zur Überprüfung, ob ein Sitzplatz in der aktuellen Vorstellung im Warenkorb ist
    function isSelectedBySelf(seat) {
        return $cart.some(s => s.seat_id === seat.seat_id && s.showtime_id === showtime_id);
    }

    async function toggleSeatSelection(seat) {
        console.log('Toggling seat:', seat);
        if (seat.status !== 'available' && !isSelectedBySelf(seat)) {
            // Nur wenn verfügbar oder bereits von uns ausgewählt
            return;
        }
        if (isSelectedBySelf(seat)) {
            try {
                console.log(`Entferne Sitzplatz ${seat.seat_id} von Showtime ${showtime_id} aus dem Warenkorb.`);
                await removeFromCart(seat.seat_id, showtime_id); // showtime_id übergeben
                // Toast-Benachrichtigung anzeigen
                showToast(`Sitzplatz ${seat.row}${seat.number} wurde aus dem Warenkorb entfernt.`);
            } catch (error) {
                // Fehler wird bereits über cartError behandelt
                console.error('Fehler beim Entfernen aus dem Warenkorb:', error);
            }
        } else {
            try {
                console.log(`Füge Sitzplatz ${seat.seat_id} zu Showtime ${showtime_id} dem Warenkorb hinzu.`);
                await addToCart(seat, showtime_id);
                // Toast-Benachrichtigung anzeigen
                showToast(`Sitzplatz ${seat.row}${seat.number} wurde zum Warenkorb hinzugefügt.`);
            } catch (error) {
                // Fehler wird bereits über cartError behandelt
                console.error('Fehler beim Hinzufügen zum Warenkorb:', error);
            }
        }

        console.log('Selected Seats after toggle:', $cart);
    }

    function showToast(message) {
        const Toast = Swal.mixin({
            toast: true,
            position: "top-end",
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true,
            didOpen: (toast) => {
                toast.onmouseenter = Swal.stopTimer;
                toast.onmouseleave = Swal.resumeTimer;
            }
        });
        Toast.fire({
            icon: "success",
            title: message
        });
    }

    function initializePayPalButtons() {
        if (!PAYPAL_CLIENT_ID) {
            Swal.fire({title: "Fehler", text: 'PayPal Client ID ist nicht gesetzt.', icon: "error"});
            return;
        }

        if (window.paypal) {
            renderPayPalButtons();
        } else {
            const script = document.createElement('script');
            script.src = `https://www.paypal.com/sdk/js?client-id=${PAYPAL_CLIENT_ID}&currency=EUR`;
            script.addEventListener('load', () => {
                if (!window.paypal) {
                    Swal.fire({title:"Fehler", text:'PayPal SDK konnte nicht geladen werden.', icon:"error"});
                    return;
                }
                renderPayPalButtons();
            });
            script.addEventListener('error', () => {
                Swal.fire({title:"Fehler", text:'PayPal SDK Fehler.', icon:"error"});
            });
            document.body.appendChild(script);
        }
    }

    function renderPayPalButtons() {
        if (!paypalContainer) {
            Swal.fire({title:"Zahlungsfehler",text:'PayPal Container nicht gefunden.',icon:"error"});
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
                if ($cart.length === 0) {
                    Swal.fire({title:"Keine Sitze",text:"Bitte wähle mindestens einen Sitzplatz aus.",icon:"warning"});
                    throw new Error('Keine Sitzplätze ausgewählt');
                }

                try {
                    const token = get(authStore).token;
                    if (!token) throw new Error('Nicht authentifiziert');
                    const response = await createPayPalOrder(showtime_id, $cart, token);
                    return response.orderID;
                } catch (err) {
                    console.error('Fehler beim Erstellen der PayPal-Order:', err);
                    Swal.fire({title:"Fehler",text:'Problem beim Erstellen der Zahlung.',icon:"error"});
                    throw err;
                }
            },
            onApprove: async (data, actions) => {
                try {
                    const token = get(authStore).token;
                    if (!token) throw new Error('Nicht authentifiziert');
                    const captureResult = await capturePayPalOrder(data.orderID, token);
                    if (captureResult.status === 'COMPLETED') {
                        await confirmBooking(data.orderID);
                    } else {
                        throw new Error('Zahlung nicht abgeschlossen');
                    }
                } catch (err) {
                    console.error('Fehler beim Abschließen der Zahlung:', err);
                    Swal.fire({title:"Zahlungsfehler",text:'Problem beim Abschließen der Zahlung.',icon:"error"});
                }
            },
            onCancel: () => {
                Swal.fire({title:"Abgebrochen",text:'Zahlung abgebrochen.',icon:"info"});
            },
            onError: (err) => {
                console.error('PayPal Fehler:', err);
                Swal.fire({title:"Zahlungsfehler",text:'Problem mit der Zahlung.',icon:"error"});
            }
        }).render(paypalContainer);
    }

    async function confirmBooking(orderID) {
        if ($cart.length === 0) {
            Swal.fire({title:"Keine Sitzplätze",text:"Bitte füge mindestens einen Sitzplatz zum Warenkorb hinzu.",icon:"warning"});
            return;
        }

        try {
            const token = get(authStore).token;
            const seatIds = $cart.map(seat => seat.seat_id);
            const booking = await createBooking(showtime_id, seatIds, token, orderID);
            Swal.fire({title:"Buchung erfolgreich",text:"Tickets gebucht.",icon:"success"})
            .then(() => {
                clearCart();
                navigate('/');
            });
        } catch (err) {
            console.error('Fehler bei der Buchung:', err);
            Swal.fire({title:"Fehler",text:'Problem bei der Buchung.',icon:"error"});
        }
    }

    function showWarning() {
        Swal.fire({
            title: 'Achtung!',
            text: 'Ihre Reservierung läuft in weniger als einer Minute ab.',
            icon: 'warning',
            timer: 3000,
            showConfirmButton: false
        });
    }

    function formatTime(seconds) {
        const min = Math.floor(seconds / 60);
        const sec = seconds % 60;
        return `${min}:${sec < 10 ? '0' : ''}${sec}`;
    }
</script>

<style>
    /* Ihr CSS bleibt unverändert */
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

    .seat.selected::before {
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

    button {
        padding: 0.5rem 1rem;
        font-size: 1rem;
        cursor: pointer;
        border: none;
        border-radius: 5px;
        transition: background-color 0.3s;
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

        <div class="legend">
            <div class="legend-item">
                <div class="legend-box selected"></div>
                <span>Ausgewählt</span>
            </div>
            <div class="legend-item">
                <div class="legend-box unavailable"></div>
                <span>Besetzt/Reserviert</span>
            </div>
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

        {#if timeLeft > 0}
            <p>Ihre Reservierung läuft in: {formatTime(timeLeft)}</p>
        {/if}

        <div class="seating-chart">
            {#each Object.keys(seatsByRow) as row}
                <div class="seat-row">
                    <div class="row-label">{row}</div>
                    {#each seatsByRow[row] as seat (row + '-' + seat.number)}
                        {#if seat.status !== 'missing'}
                            <div
                                class="seat {seat.status} {seat.type} {isSelectedBySelf(seat) ? 'selected' : ''}"
                                on:click={() => toggleSeatSelection(seat)}
                                title={`Reihe ${seat.row}, Sitz ${seat.number}${seat.type ? `, Typ: ${seat.type}, Preis: ${seat.price.toFixed(2)}€` : ''}`}
                                style={seat.type ? `background-color: ${getSeatTypeColor(seat.type)};` : ''}
                            >
                                {#if seat.status === 'unavailable' && !isSelectedBySelf(seat)}
                                    <i class="fas fa-user"></i>
                                {:else if isSelectedBySelf(seat)}
                                    <i class="fas fa-check"></i>
                                {:else if seat.type && getSeatTypeIcon(seat.type)}
                                    <i class={`fas ${getSeatTypeIcon(seat.type)}`}></i>
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

        <p>Gesamtpreis: {totalPrice.toFixed(2)}€</p>
        <div id="paypal-button-container" bind:this={paypalContainer}></div>

        <button on:click={() => navigate('/adminkinosaal')}>Zurück zu Überblick der Kinosäle</button>
    {/if}
</main>
