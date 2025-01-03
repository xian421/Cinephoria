<!-- src/routes/Buchung.svelte -->
<script lang="ts">
    import { onMount, tick } from 'svelte';
    import { navigate } from 'svelte-routing';
    import { 
        createBooking, 
        createPayPalOrder, 
        capturePayPalOrder, 
        fetchSeatTypes, 
        fetchSeatsWithReservation, 
        fetchSeatTypesWithDiscounts 
    } from '../services/api.js';
    import { get } from 'svelte/store';
    import { authStore } from '../stores/authStore'; 
    import { 
        cart, 
        addToCart, 
        removeFromCart, 
        clearCart, 
        loadCart
    } from '../stores/cartStore.js';
    import Timer from '../components/Timer.svelte'; // Importiere die Timer-Komponente
    import "@fortawesome/fontawesome-free/css/all.min.css";

    import { showSuccessToast, showErrorAlert, showSuccessAlert, showConfirmationDialog, showCustomAlert } from '../utils/notifications.js'; // Importiere die Benachrichtigungsfunktionen

    export let showtime_id: string;

    let seats = [];
    let isLoading = true;
    let error: string | null = null;
    let seatTypesList = [];
    let seatsByRow = {};
    let payPalInitialized = false;
    let paypalContainer: HTMLElement;

    let test = [];

    // Berechne Gesamtpreis
    $: totalPrice = $cart.reduce((sum, seat) => sum + seat.price, 0);

    onMount(async () => {
        isLoading = true;
        try {
            await loadSeats();
            await loadCart();
        } catch (err: any) {
            console.error('Fehler beim Laden der Sitze oder Sitztypen:', err);
            error = err.message || 'Fehler beim Laden.';
            showErrorAlert(error);
        } finally {
            isLoading = false;
            await tick();
            if (!payPalInitialized) {
                initializePayPalButtons();
                payPalInitialized = true;
            }
        }
    });

    async function loadSeats() {
        try {
            const token = get(authStore).token;
            let guest_id = localStorage.getItem('guest_id') || crypto.randomUUID();
            localStorage.setItem('guest_id', guest_id);

            // Laden der Sitzarten
            test = await fetchSeatTypes(token);
            seatTypesList = await fetchSeatTypesWithDiscounts(token);
            console.log(seatTypesList);
            console.log(test);

            // Funktion zur Berechnung des niedrigsten Preises
            function calculateLowestPrice(seatType) {
                const basePrice = seatType.price;
                let lowestPrice = basePrice;

                if (seatType.discounts && seatType.discounts.length > 0) {
                    seatType.discounts.forEach(discount => {
                        let discountedPrice = basePrice;

                        if (discount.discount_percentage) {
                            // Berechne Preis nach prozentualer Ermäßigung
                            discountedPrice = basePrice * (1 - discount.discount_percentage / 100);
                        }

                        if (discount.discount_amount) {
                            // Berechne Preis nach fester Ermäßigung
                            discountedPrice = basePrice - discount.discount_amount;
                        }

                        // Stelle sicher, dass der Preis nicht negativ wird
                        discountedPrice = Math.max(discountedPrice, 0);

                        // Aktualisiere den niedrigsten Preis, falls der berechnete Preis niedriger ist
                        if (discountedPrice < lowestPrice) {
                            lowestPrice = discountedPrice;
                        }
                    });
                }

                return lowestPrice;
            }

            // Erweiterung der seatTypesList mit lowestPrice
            seatTypesList = seatTypesList.map(seatType => ({
                ...seatType,
                lowestPrice: calculateLowestPrice(seatType)
            }));

            const seatData = await fetchSeatsWithReservation(showtime_id, token, guest_id);
            seats = seatData.seats;
            seatsByRow = groupSeatsByRowWithGaps(seats);
        } catch (err: any) {
            console.error('Fehler beim Laden der Sitze oder Sitztypen:', err);
            error = err.message || 'Fehler beim Laden.';
            showErrorAlert(error);
        }
    }

    function groupSeatsByRowWithGaps(seats: any[]) {
        const rowsSet = new Set();
        const seatNumbersSet = new Set();

        seats.forEach(seat => {
            rowsSet.add(seat.row);
            seatNumbersSet.add(seat.number);
        });

        const allRowLabels = generateAllRowLabels(Array.from(rowsSet));
        const allSeatNumbers = generateAllSeatNumbers(Array.from(seatNumbersSet));

        const seatMap: Record<string, any> = {};
        seats.forEach(seat => {
            seatMap[`${seat.row}-${seat.number}`] = seat;
        });

        const rowsWithGaps: Record<string, any[]> = {};
        allRowLabels.forEach(rowLabel => {
            const rowSeats: any[] = [];
            allSeatNumbers.forEach(num => {
                const key = `${rowLabel}-${num}`;
                if (seatMap[key]) {
                    rowSeats.push(seatMap[key]);
                } else {
                    rowSeats.push({ 
                        row: rowLabel, 
                        number: num, 
                        status: 'missing', 
                        seat_id: null, 
                        type: null, 
                        price: 0.00 
                    });
                }
            });
            rowsWithGaps[rowLabel] = rowSeats;
        });
        return rowsWithGaps;
    }

    function generateAllRowLabels(existingRows: string[]) {
        if (existingRows.length === 0) return [];
        const minRowCharCode = Math.min(...existingRows.map(r => r.charCodeAt(0)));
        const maxRowCharCode = Math.max(...existingRows.map(r => r.charCodeAt(0)));
        const allRows = [];
        for (let code = minRowCharCode; code <= maxRowCharCode; code++) {
            allRows.push(String.fromCharCode(code));
        }
        return allRows;
    }

    function generateAllSeatNumbers(existingNumbers: number[]) {
        if (existingNumbers.length === 0) return [];
        const min = Math.min(...existingNumbers);
        const max = Math.max(...existingNumbers);
        const all = [];
        for (let i = min; i <= max; i++) {
            all.push(i);
        }
        return all;
    }

    function getSeatTypeColor(typeName: string) {
        const type = seatTypesList.find((st: any) => st.name === typeName);
        return type ? type.color : '#678be0';
    }

    function getSeatTypeIcon(typeName: string) {
        const type = seatTypesList.find((st: any) => st.name === typeName);
        return type ? type.icon : null;
    }

    function isSelectedBySelf(seat: any) {
        return $cart.some(s => s.seat_id === seat.seat_id && s.showtime_id === showtime_id);
    }

    let selectedSeat: { row: string; number: number; type?: string; price: number; } | null = null;

    async function toggleSeatSelection(seat: any) {
        if (seat.status !== 'available' && !isSelectedBySelf(seat)) {
        //    console.log('Sitzplatz ist bereits reserviert:', seat);
            return;
        }

        try {
            if (isSelectedBySelf(seat)) {
                await removeFromCart(seat.seat_id, showtime_id);
                showSuccessToast(`Sitzplatz ${seat.row}${seat.number} wurde aus dem Warenkorb entfernt.`);
            } else {
                await addToCart(seat, showtime_id);
                showSuccessToast(`Sitzplatz ${seat.row}${seat.number} wurde zum Warenkorb hinzugefügt.`);
                selectedSeat = seat;
            }
        } catch (error) {
            console.error('Fehler beim Aktualisieren des Warenkorbs:', error);
        }
    }

    function initializePayPalButtons() {
        const PAYPAL_CLIENT_ID = 'AXWfRwPPgPCoOBZzqI-r4gce1HuWZXDnFqUdES0bP8boKSv5KkkPvZrMFwcCDShXjC3aTdChUjOhwxhW'; // Stelle sicher, dass diese Variable definiert ist

        if (!PAYPAL_CLIENT_ID) {
            showErrorAlert('PayPal Client ID ist nicht gesetzt.');
            return;
        }

        if (window.paypal) {
            renderPayPalButtons();
        } else {
            const script = document.createElement('script');
            script.src = `https://www.paypal.com/sdk/js?client-id=${PAYPAL_CLIENT_ID}&currency=EUR`;
            script.addEventListener('load', () => {
                if (!window.paypal) {
                    showErrorAlert('PayPal SDK konnte nicht geladen werden.');
                    return;
                }
                renderPayPalButtons();
            });
            script.addEventListener('error', () => {
                showErrorAlert('PayPal SDK Fehler.');
            });
            document.body.appendChild(script);
        }
    }

    function renderPayPalButtons() {
        if (!paypalContainer) {
            showErrorAlert('PayPal Container nicht gefunden.');
            return;
        }

        window.paypal.Buttons({
            style: {
                layout: 'vertical',
                color: 'blue',
                shape: 'rect',
                label: 'paypal'
            },
            createOrder: async () => {
                if ($cart.length === 0) {
                    showErrorAlert('Bitte wähle mindestens einen Sitzplatz aus.');
                    throw new Error('Keine Sitzplätze ausgewählt');
                }

                const token = get(authStore).token;
                if (!token) throw new Error('Nicht authentifiziert');

                try {
                    const response = await createPayPalOrder(showtime_id, $cart, token);
                    return response.orderID;
                } catch (err) {
                    console.error('Fehler beim Erstellen der PayPal-Order:', err);
                    showErrorAlert('Problem beim Erstellen der Zahlung.');
                    throw err;
                }
            },
            onApprove: async (data: any) => {
                const token = get(authStore).token;
                if (!token) throw new Error('Nicht authentifiziert');
                
                try {
                    const captureResult = await capturePayPalOrder(data.orderID, token);
                    if (captureResult.status === 'COMPLETED') {
                        await confirmBooking(data.orderID);
                    } else {
                        throw new Error('Zahlung nicht abgeschlossen');
                    }
                } catch (err) {
                    console.error('Fehler beim Abschließen der Zahlung:', err);
                    showErrorAlert('Problem beim Abschließen der Zahlung.');
                }
            },
            onCancel: () => {
                showSuccessAlert('Zahlung abgebrochen.');
            },
            onError: (err: any) => {
                console.error('PayPal Fehler:', err);
                showErrorAlert('Problem mit der Zahlung.');
            }
        }).render(paypalContainer);
    }

    async function confirmBooking(orderID: string) {
        if ($cart.length === 0) {
            showErrorAlert('Bitte füge mindestens einen Sitzplatz zum Warenkorb hinzu.');
            return;
        }

        try {
            const token = get(authStore).token;
            const seatIds = $cart.map(seat => seat.seat_id);
            await createBooking(showtime_id, seatIds, token, orderID);
            showSuccessAlert('Tickets gebucht.').then(() => {
                clearCart();
                navigate('/');
            });
        } catch (err: any) {
            console.error('Fehler bei der Buchung:', err);
            showErrorAlert('Problem bei der Buchung.');
        }
    }

    function showWarning() {
        showWarningAlert('Achtung!', 'Ihre Reservierung läuft in weniger als einer Minute ab.', 3000);
    }

    function formatTime(seconds: number) {
        const min = Math.floor(seconds / 60);
        const sec = seconds % 60;
        return `${min}:${sec < 10 ? '0' : ''}${sec}`;
    }
</script>

<main class="booking-container">
    {#if isLoading}
        <p>Lade Sitzplätze...</p>
    {:else if error}
        <p class="error-message">{error}</p>
    {:else}
        <h1 class="booking-title">Wähle deine Plätze für Vorstellung #{showtime_id}</h1>

        <div class="legend">
            <div class="legend-item">
                <div class="legend-box selected"></div>
                <span>Dein Platz</span>
            </div>
            <div class="legend-item">
                <div class="legend-box unavailable"></div>
                <span>Belegt</span>
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
                    <span>{`${seatType.name}  ${seatType.lowestPrice.toFixed(2)}€ - ${seatType.price.toFixed(2)}€`}</span>
                </div>
            {/each}
        </div>

        <!-- Integriere die Timer-Komponente nur, wenn Sitze im Warenkorb sind -->
        {#if $cart.length > 0}
            <Timer mode="inline" />
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

        <div class="info-bar">
            <p class="total-price">Gesamtpreis: {totalPrice.toFixed(2)}€</p>
            <div class="button-group">
                <button class="cart-button" on:click={() => navigate('/warenkorb')}>
                    <i class="fas fa-shopping-cart"></i> Warenkorb ansehen
                </button>
                <button class="home-button" on:click={() => navigate('/')}>
                    <i class="fas fa-home"></i> Zur Startseite
                </button>
            </div>
        </div>

        <div class="paypal-section">
            <p>Sichere Zahlung mit PayPal</p>
            <div id="paypal-button-container" bind:this={paypalContainer}></div>
        </div>
    {/if}
</main>

<style>
    .booking-container {
        padding: 2rem;
        font-family: Arial, sans-serif;
        max-width: 800px;
        margin: 0 auto;
     
        border-radius: 20px;
       
        position: relative;
        color: #fff;
        margin-top: 4rem;
    }

    h1.booking-title {
        text-align: center;
        color: #2ecc71;
        text-shadow: 0 0 10px #2ecc71;
        margin-bottom: 2rem;
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
        font-size: 0.9rem;
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

    .legend-box.available {
        background-color: #3498db;
    }

    .legend-box.selected {
        background-color: #2ecc71;
    }
    .legend-box.selected::before {
        content: "\f007";
        font-family: "Font Awesome 5 Free";
        font-weight: 900;
    }

    .legend-box.unavailable {
        background-color: rgb(186, 186, 186);
    }

    .legend-box.unavailable::before {
        content: "\f007";
        font-family: "Font Awesome 5 Free";
        font-weight: 900;
    }

    .legend-box.type {
        box-shadow: 0 0 5px #2ecc71;
    }

    p.reservation-time {
        text-align: center;
        margin-bottom: 1rem;
        font-size: 1.1rem;
    }

    .time-highlight {
        color: #e74c3c;
        font-weight: bold;
    }

    .seating-chart {
        /* Nicht ändern! */
        display: flex;
        flex-direction: column;
        gap: 10px;
        justify-items: center;
        margin-bottom: 2rem;
    }

    .seat-row {
        /* Nicht ändern! */
        display: flex;
        justify-content: center;
        gap: 5px;
        align-items: center;
    }

    .seat {
        /* Nicht ändern! */
        width: 40px;
        height: 40px;
        background-color: rgb(103, 139, 224);
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
        /* Nicht ändern! */
        background-color: #2ecc71 !important;
    }

    .seat.selected::before {
        /* Nicht ändern! */
        content: "\f007";
        font-family: "Font Awesome 5 Free";
        font-weight: 900;
    }

    .seat.vip {
        /* Nicht ändern! */
        background-color: rgb(140, 76, 140);
    }

    .seat.wheelchair {
        /* Nicht ändern! */
        font-size: 24px;
    }

    .seat.placeholder {
        /* Nicht ändern! */
        background-color: transparent;
        pointer-events: none;
        width: 40px;
        height: 40px;
    }

    .seat:hover.available {
        /* Nicht ändern! */
        transform: scale(1.1);
    }

    .row-label {
        /* Nicht ändern! */
        width: 20px;
        text-align: right;
        margin-right: 5px;
        font-weight: bold;
        color: #ddd;
    }

    .seat.unavailable {
        /* Nicht ändern! */
        background-color: #7f8c8d !important;
        cursor: not-allowed;
    }

    .error-message {
        color: red;
        font-weight: bold;
        text-align: center;
    }

    .info-bar {
        margin: 2rem 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1rem;
    }

    .total-price {
        font-size: 1.2rem;
        color: #2ecc71;
        text-shadow: 0 0 5px #2ecc71;
    }

    .button-group {
        display: flex;
        gap: 1rem;
    }

    .cart-button, .home-button {
        background: #2ecc71;
        color: #000;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 1.2rem;
        cursor: pointer;
        font-weight: bold;
        font-size: 1rem;
        box-shadow: 0 0 10px #2ecc71;
        transition: transform 0.3s;
    }

    .cart-button:hover, .home-button:hover {
        transform: scale(1.05);
        opacity: 0.9;
    }

    .paypal-section {
        text-align: center;
        margin-top: 2rem;
    }

    .paypal-section p {
        margin-bottom: 1rem;
    }

    #paypal-button-container {
        margin: 0 auto;
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
