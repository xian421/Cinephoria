<!-- src/components/Warenkorb.svelte -->
<script>
    import { navigate } from 'svelte-routing';
    import { showErrorAlert, showSuccessAlert, showConfirmationDialog } from '../utils/notifications.js'; // Importiere die Benachrichtigungsfunktionen
    import "@fortawesome/fontawesome-free/css/all.min.css";
    import { derived } from 'svelte/store';
    import { onMount } from 'svelte';
    import { cart, cartError, removeFromCart, clearCart, loadCart, updateCartDiscount } from '../stores/cartStore.js';
    import { tweened } from 'svelte/motion';
    import { cubicOut } from 'svelte/easing';
    import { authStore } from '../stores/authStore.js';
    import { get } from 'svelte/store';

    let headerOpacity = tweened(0, { duration: 1000, easing: cubicOut });
    let taglineOpacity = tweened(0, { duration: 1500, easing: cubicOut, delay: 500 });

    let loading = false; // Ladezustand hinzufügen

    onMount(async () => {
        await loadCart(); 
        headerOpacity.set(1);
        taglineOpacity.set(1);
    });

    // Reaktive Berechnung des Gesamtpreises unter Berücksichtigung der Rabatte
    $: totalPrice = $cart.reduce((sum, seat) => {
        let seatPrice = seat.price;
        if (seat.selectedDiscount) {
            if (seat.selectedDiscount.discount_percentage) {
                seatPrice -= seat.price * (seat.selectedDiscount.discount_percentage / 100);
            }
            if (seat.selectedDiscount.discount_amount) {
                seatPrice -= seat.selectedDiscount.discount_amount;
            }
        }
        return sum + Math.max(seatPrice, 0); 
    }, 0);

    // Reaktive Fehlerbehandlung mit Zurücksetzen von cartError
    $: if ($cartError) {
        showErrorAlert($cartError).then(() => {
            cartError.set(null);
        });
    }

    // Gruppieren der Sitzplätze nach showtime_id
    const groupedCart = derived(cart, $cart => {
        const groups = {};
        $cart.forEach(seat => {
            const key = seat.showtime_id;
            if (!groups[key]) {
                groups[key] = {
                    showtime: seat.showtime,
                    movie: seat.movie,
                    seats: []
                };
            }
            groups[key].seats.push(seat);
        });
        return Object.values(groups);
    });

    // Funktion zum Entfernen eines Sitzplatzes aus dem Warenkorb
    async function handleRemove(seat_id, showtime_id) {
        const result = await showConfirmationDialog('Sitzplatz entfernen', 'Möchtest du diesen Sitzplatz wirklich aus dem Warenkorb entfernen?');

        if (result.isConfirmed) {
            try {
                await removeFromCart(seat_id, showtime_id);
                showSuccessAlert("Der Sitzplatz wurde aus dem Warenkorb entfernt.");
            } catch (error) {
                console.error('Fehler beim Entfernen des Sitzplatzes:', error);
                showErrorAlert("Beim Entfernen des Sitzplatzes ist ein Fehler aufgetreten.");
            }
        }
    }

    // Funktion zum Leeren des gesamten Warenkorbs
    async function handleClearCart() {
        if ($cart.length === 0) return;

        const result = await showConfirmationDialog('Warenkorb leeren', 'Möchtest du alle Sitzplätze aus dem Warenkorb entfernen?');

        if (result.isConfirmed) {
            try {
                await clearCart();
                showSuccessAlert("Der Warenkorb wurde geleert.");
            } catch (error) {
                console.error('Fehler beim Leeren des Warenkorbs:', error);
                showErrorAlert("Beim Leeren des Warenkorbs ist ein Fehler aufgetreten.");
            }
        }
    }

    // Funktion zum Fortsetzen des Buchungsprozesses
    function proceedToCheckout() {
        if ($cart.length === 0) {
            showErrorAlert("Bitte füge mindestens einen Sitzplatz zum Warenkorb hinzu.");
            return;
        }
        navigate('/checkout'); // Passe den Pfad entsprechend an
    }

    // Funktion zum Aktualisieren des Rabatts eines Sitzplatzes
    async function handleDiscountChange(seat, selectedDiscount) {
        try {
            loading = true; // Ladezustand aktivieren

            console.log('handleDiscountChange aufgerufen mit seat:', {
                seat_id: seat.seat_id,
                showtime_id: seat.showtime_id,
                currentSelectedDiscount: seat.selectedDiscount
            }, 'selectedDiscount:', selectedDiscount);
            
            // Ermitteln der richtigen seat_type_discount_id oder null
            const seat_type_discount_id = selectedDiscount && selectedDiscount.seat_type_discount_id !== 'none' ? selectedDiscount.seat_type_discount_id : null;
            console.log('Ermittelte seat_type_discount_id:', seat_type_discount_id);
            
            await updateCartDiscount(seat, seat_type_discount_id);
            await loadCart(); 

            console.log('Rabatt erfolgreich aktualisiert für seat_id:', seat.seat_id, 'mit seat_type_discount_id:', seat_type_discount_id);

            showSuccessAlert("Der Rabatt wurde aktualisiert.");
        } catch (error) {
            console.error('Fehler beim Aktualisieren des Rabatts:', error);
            showErrorAlert("Beim Aktualisieren des Rabatts ist ein Fehler aufgetreten.");
        } finally {
            loading = false; // Ladezustand deaktivieren
        }
    }

    // Funktion zur Ermittlung des passenden Icons basierend auf dem Discount
    function getDiscountIcon(discount) {
        console.log('getDiscountIcon aufgerufen mit discount:', discount);
        if (!discount) return 'fas fa-times-circle'; 

        switch (discount.name.toLowerCase()) {
            case 'rentner':
                return 'fas fa-user';
            case 'student':
                return 'fas fa-user-graduate';
            case 'kind':
                return 'fas fa-child';
            case 'mitglied':
                return 'fas fa-id-card';
            case 'mitarbeiter':
                return 'fas fa-briefcase';
            // Füge weitere Fälle je nach Discount-Name hinzu
            default:
                return 'fas fa-tag'; // Standard-Icon
        }
    }

    // Lokaler Zustand für sichtbare Rabatt-Auswahl
    let visibleDiscountSeat = null;

    function toggleDiscountSelection(seat) {
        if (visibleDiscountSeat && visibleDiscountSeat.seat_id === seat.seat_id && visibleDiscountSeat.showtime_id === seat.showtime_id) {
            visibleDiscountSeat = null;
        } else {
            visibleDiscountSeat = seat;
        }
        console.log('visibleDiscountSeat geändert:', visibleDiscountSeat ? { seat_id: visibleDiscountSeat.seat_id, showtime_id: visibleDiscountSeat.showtime_id } : null);
    }
</script>

<div class="background">
    <header class="header-section">
        <h1 class="header-text" style:opacity={$headerOpacity}>CINEPHORIA - Dein Warenkorb</h1>
        <p class="tagline" style:opacity={$taglineOpacity}>Ein futuristisches Einkaufserlebnis!</p>
    </header>

    <main class="cart-container">
        {#if loading}
            <div class="loading-overlay">
                <div class="spinner"></div>
            </div>
        {/if}

        <h1>Warenkorb: {totalPrice.toFixed(2)} €</h1>

        {#if $cart.length === 0}
            <p>Dein Warenkorb ist leer.</p>
        {:else}
            {#each $groupedCart as group}
                <div class="showtime-details">
                    <h2>Film: {group.movie.title}</h2>
                    <p>
                        Startzeit: {new Date(group.showtime.start_time).toLocaleString('de-DE', { hour: '2-digit', minute: '2-digit' })}, 
                        {group.showtime.screen_name}
                    </p>
                </div>

                <table class="cart-table">
                    <thead>
                        <tr>
                            <th>Sitzplatz</th>
                            <th>Typ</th>
                            <th>Preis</th>
                            <th>Ermäßigung</th>
                            <th>Aktion</th>
                        </tr>
                    </thead>
                    <tbody>
                        {#each group.seats as seat ( `${seat.seat_id}-${seat.showtime_id}` )}
                            <tr>
                                <td>
                                    <div class="cart-item">
                                        {#if seat.type === 'wheelchair'}
                                            <i class="fas fa-wheelchair" aria-hidden="true"></i>
                                            <span>{seat.row}-{seat.number}</span>
                                        {:else if seat.type === 'vip'}
                                            <i class="fas fa-star" aria-hidden="true"></i>
                                            <span>{seat.row}-{seat.number}</span>
                                        {:else}
                                            {#if seat.row && seat.number}
                                                {seat.row}-{seat.number}
                                            {:else}
                                                <span>-</span>
                                            {/if}
                                        {/if}
                                    </div>
                                </td>
                                <td>{seat.type ? seat.type.charAt(0).toUpperCase() + seat.type.slice(1) : 'Standard'}</td>
                                <td>
                                    {seat.price.toFixed(2)} €
                                    {#if seat.selectedDiscount}
                                        {#if seat.selectedDiscount.discount_amount}
                                            (-{seat.selectedDiscount.discount_amount} €)
                                        {:else if seat.selectedDiscount.discount_percentage}
                                            (-{seat.selectedDiscount.discount_percentage} %)
                                        {/if}
                                    {/if}
                                </td>
                                <td>
                                    <!-- Aktuell ausgewählter Rabatt als Kärtchen -->
                                    <div class="discount-section">
                                        <div class="discount-selected" on:click={() => toggleDiscountSelection(seat)} disabled={loading}>
                                            <i class={getDiscountIcon(seat.selectedDiscount)}></i>
                                            <span>{seat.selectedDiscount ? seat.selectedDiscount.name : 'Kein Rabatt'}</span>
                                            {#if seat.selectedDiscount && seat.selectedDiscount.discount_amount}
                                                <small>(-{seat.selectedDiscount.discount_amount} €)</small>
                                            {/if}
                                            {#if seat.selectedDiscount && seat.selectedDiscount.discount_percentage}
                                                <small>(-{seat.selectedDiscount.discount_percentage} %)</small>
                                            {/if}
                                        </div>

                                        {#if visibleDiscountSeat && visibleDiscountSeat.seat_id === seat.seat_id && visibleDiscountSeat.showtime_id === seat.showtime_id}
                                            <div class="discount-options-wrapper">
                                                <!-- Option "Kein Rabatt" -->
                                                <div 
                                                    class="discount-option { !seat.selectedDiscount ? 'selected' : '' }"
                                                    on:click={() => {
                                                        handleDiscountChange(seat, { id: 'none', name: 'Kein Rabatt', discount_amount: 0, discount_percentage: 0 });
                                                        toggleDiscountSelection(seat);
                                                    }}
                                                    disabled={loading}
                                                >
                                                    <i class="fas fa-times-circle"></i>
                                                    <span>Kein Rabatt</span>
                                                </div>
                                                <!-- Dynamische Discount-Optionen -->
                                                {#each seat.discounts as discount}
                                                    <div 
                                                        class="discount-option { seat.selectedDiscount?.discount_id === discount.discount_id ? 'selected' : '' }"
                                                        on:click={() => {
                                                            handleDiscountChange(seat, discount);
                                                            toggleDiscountSelection(seat);
                                                        }}
                                                        disabled={loading}
                                                    >
                                                        <i class={getDiscountIcon(discount)}></i>
                                                        <span>{discount.name}</span>
                                                        {#if discount.discount_amount}
                                                            <small>(-{discount.discount_amount} €)</small>
                                                        {/if}
                                                        {#if discount.discount_percentage}
                                                            <small>(-{discount.discount_percentage} %)</small>
                                                        {/if}
                                                    </div>
                                                {/each}
                                            </div>
                                        {/if}
                                    </div>
                                </td>
                                <td>
                                    <button class="remove-btn" on:click={() => handleRemove(seat.seat_id, seat.showtime_id)} disabled={loading}>
                                        <i class="fas fa-trash"></i> Entfernen
                                    </button>
                                </td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
                
            {/each}

            <div class="button-group">
                <button class="clear-btn" on:click={handleClearCart} disabled={loading}>
                    <i class="fas fa-ban"></i> Warenkorb leeren
                </button>
                <button class="proceed-btn" on:click={proceedToCheckout} disabled={loading}>
                    <i class="fas fa-arrow-right"></i> Zur Buchung
                </button>
            </div>

            <h2>Gesamtpreis: {totalPrice.toFixed(2)} €</h2>
        {/if}

        <button class="clear-btn" on:click={() => navigate('/')} disabled={loading}>Home</button>
    </main>
</div>

<style>
    /* Lade-Overlay Styling */
    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }

    .spinner {
        border: 8px solid #f3f3f3; /* Light grey */
        border-top: 8px solid #2ecc71; /* Green */
        border-radius: 50%;
        width: 60px;
        height: 60px;
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    @import url('https://use.fontawesome.com/releases/v5.15.4/css/all.css');
    
    .background {
      position: relative;
      min-height: 100vh;
      padding: 2rem;
      overflow: hidden;
    }
    
    .header-section {
      text-align: center;
      margin-top: 4rem;
    }
    
    .header-text {
      font-size: 3rem;
      margin: 0;
      color: #2ecc71;
      text-shadow: 0 0 20px #2ecc71, 0 0 40px #2ecc71;
      animation: glow 2s infinite alternate;
    }
    
    .tagline {
      font-size: 1.5rem;
      color: #fff;
      margin-top: 1rem;
      text-shadow: 0 0 10px #fff;
    }
    
    @keyframes glow {
      from {
        text-shadow: 0 0 10px #2ecc71, 0 0 20px #2ecc71;
      }
      to {
        text-shadow: 0 0 20px #2ecc71, 0 0 40px #2ecc71;
      }
    }
    
    .cart-container {
      border-radius: 20px;
      margin: 2rem auto;
      padding: 2rem;
      max-width: 1200px;
      position: relative;
      background: #1a1a1a; /* Dunkler Hintergrund für den Warenkorb */
      box-shadow: 0 0 20px rgba(0, 0, 0, 0.7);
    }
    
    .cart-container h1, .cart-container h2 {
      text-align: center;
      color: #2ecc71;
      text-shadow: 0 0 10px #2ecc71;
    }
    
    .showtime-details {
      background: rgba(0,0,0,0.6); /* Angepasst für besseren Kontrast im Dark Mode */
      border: 1px solid #2ecc71;
      border-radius: 16px;
      padding: 1.5rem;
      margin-bottom: 1rem;
      box-shadow: 0 0 15px rgba(0, 0, 0, 0.5);
      text-align: center;
    }
    
    .cart-table {
      width: 100%;
      border-collapse: separate;
      border-spacing: 0;
      margin-bottom: 2rem;
      border-radius: 20px;
    }
    
    .cart-table th, .cart-table td {
      padding: 1rem;
      text-align: center;
      border-bottom: 1px solid #2ecc71;
      font-size: 1rem;
    }
    
    .cart-table th {
        background-color: rgba(0,0,0,0.7); /* Angepasst für besseren Kontrast */
        color: #fff;
      font-weight: bold;
      text-shadow: none;
    }
    
    .cart-table td {
      background-color: rgba(0,0,0,0.7); /* Angepasst für besseren Kontrast */
      color: #fff;
    }
    
    .cart-table tr:hover {
      background-color: rgba(0,0,0,0.9);
    }
    
    .remove-btn, .clear-btn, .proceed-btn {
      font-size: 1rem;
      font-weight: bold;
      border: none;
      border-radius: 10px;
      padding: 0.7rem 1.2rem;
      cursor: pointer;
      transition: transform 0.3s ease;
      background-color: #2ecc71;
      color: #000;
      box-shadow: 0 0 10px #2ecc71;
    }
    
    .remove-btn:hover, .clear-btn:hover, .proceed-btn:hover {
      transform: translateY(-3px) scale(1.05);
      opacity: 0.9;
    }
    
    .button-group {
      display: flex;
      justify-content: center;
      gap: 1rem;
      margin-top: 2rem;
    }
    
    .discount-section {
      position: relative;
    }
    
    .discount-selected {
      display: flex;
      gap: 0.5rem;
      align-items: center;
      justify-content: center;
      background: #2ecc71;
      border-radius: 12px;
      padding: 0.5rem 1rem;
      cursor: pointer;
      font-size: 0.9rem;
      color: #000;
      transition: background 0.3s, transform 0.3s;
      margin: 0 auto;
      width: fit-content;
      box-shadow: 0 0 10px #2ecc71;
    }
    
    .discount-selected i {
      font-size: 1.2rem;
    }
    
    .discount-options-wrapper {
      position: absolute;
      top: 100%;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(0,0,0,0.9);
      border: 1px solid #2ecc71;
      border-radius: 16px;
      padding: 1rem;
      margin-top: 0.5rem;
      box-shadow: 0 0 15px #2ecc71;
      display: flex;
      gap: 1rem;
      max-width: 220px; 
      overflow-x: auto;
      white-space: nowrap;
      z-index: 999; 
    }
    
    .discount-option {
      background: #2ecc71;
      border-radius: 12px;
      padding: 0.5rem 1rem;
      cursor: pointer;
      font-size: 0.9rem;
      color: #000;
      transition: background 0.3s, transform 0.3s;
      display: inline-block; 
      text-align: center;
      min-width: 100px;
      vertical-align: middle;
      box-shadow: 0 0 5px #2ecc71;
    }
    
    .discount-option i {
      font-size: 1.5rem;
      margin-bottom: 0.5rem;
      display: block;
    }
    
    .discount-option:hover {
      background: #27ae60;
      transform: scale(1.05);
    }
    
    .discount-option.selected {
      background: #3498db;
      color: #fff;
      box-shadow: 0 0 10px #3498db;
    }
    
    @media (max-width: 768px) {
      .cart-table th, .cart-table td {
        padding: 0.5rem;
        font-size: 0.9rem;
      }
      
      .discount-options-wrapper {
        max-width: 180px; 
      }
    }
</style>
