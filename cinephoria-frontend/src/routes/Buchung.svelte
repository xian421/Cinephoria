<!-- src/routes/Buchung.svelte -->
<script lang="ts">
    import { onMount, tick } from 'svelte';
    import { navigate } from 'svelte-routing';
    import { 
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

            // Funktion zur Berechnung des niedrigsten Preises
            function calculateLowestPrice(seatType) {
                const basePrice = seatType.price;
                let lowestPrice = basePrice;

                if (seatType.discounts && seatType.discounts.length > 0) {
                    seatType.discounts.forEach(discount => {
                        let discountedPrice = basePrice;

                        if (discount.discount_percentage) {
                            discountedPrice = basePrice * (1 - discount.discount_percentage / 100);
                        }

                        if (discount.discount_amount) {
                            discountedPrice = basePrice - discount.discount_amount;
                        }

                        discountedPrice = Math.max(discountedPrice, 0);

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
        background-color: #2ecc71 !important;
    }

    .seat.selected::before {
        content: "\f007";
        font-family: "Font Awesome 5 Free";
        font-weight: 900;
    }

    .seat.vip {
        background-color: rgb(140, 76, 140);
    }

    .seat.wheelchair {
        font-size: 24px;
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

    .row-label {
        width: 20px;
        text-align: right;
        margin-right: 5px;
        font-weight: bold;
        color: #ddd;
    }

    .seat.unavailable {
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
