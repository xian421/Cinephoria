<script>
    import { navigate } from 'svelte-routing';
    import Swal from 'sweetalert2';
    import "@fortawesome/fontawesome-free/css/all.min.css";
    import { derived } from 'svelte/store';

    import { onMount } from 'svelte';
import { cart, cartError, removeFromCart, clearCart, loadCart } from '../stores/cartStore.js';

onMount(() => {
    loadCart(); // Lade den Warenkorb beim Neuladen der Seite
});
    
    // Rabattoptionen
    const discountOptions = [
        { id: 'none', label: 'Kein Rabatt', amount: 0 },
        { id: 'student', label: 'Student', amount: 5 }, // 5 Euro Rabatt
        { id: 'senior', label: 'Senior', amount: 3 }    // 3 Euro Rabatt
    ];

    // Reaktive Berechnung des Gesamtpreises unter Berücksichtigung der Rabatte
    $: totalPrice = $cart.reduce((sum, seat) => sum + (seat.price - (seat.discount?.amount || 0)), 0);

    // Reaktive Fehlerbehandlung mit Zurücksetzen von cartError
    $: if ($cartError) {
        Swal.fire({
            title: "Fehler",
            text: $cartError,
            icon: "error",
            confirmButtonText: "OK"
        }).then(() => {
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
        const result = await Swal.fire({
            title: 'Sitzplatz entfernen',
            text: 'Möchtest du diesen Sitzplatz wirklich aus dem Warenkorb entfernen?',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Ja, entfernen',
            cancelButtonText: 'Abbrechen'
        });

        if (result.isConfirmed) {
            try {
                await removeFromCart(seat_id, showtime_id);
                await Swal.fire(
                    'Entfernt!',
                    'Der Sitzplatz wurde aus dem Warenkorb entfernt.',
                    'success'
                );
            } catch (error) {
                console.error('Fehler beim Entfernen des Sitzplatzes:', error);
                Swal.fire({
                    title: 'Fehler',
                    text: 'Beim Entfernen des Sitzplatzes ist ein Fehler aufgetreten.',
                    icon: 'error',
                    confirmButtonText: 'OK'
                });
            }
        }
    }

    // Funktion zum Leeren des gesamten Warenkorbs
    async function handleClearCart() {
        if ($cart.length === 0) return;

        const result = await Swal.fire({
            title: 'Warenkorb leeren',
            text: 'Möchtest du alle Sitzplätze aus dem Warenkorb entfernen?',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Ja, leeren',
            cancelButtonText: 'Abbrechen'
        });

        if (result.isConfirmed) {
            try {
                await clearCart();
                await Swal.fire(
                    'Gelöscht!',
                    'Der Warenkorb wurde geleert.',
                    'success'
                );
            } catch (error) {
                console.error('Fehler beim Leeren des Warenkorbs:', error);
                Swal.fire({
                    title: 'Fehler',
                    text: 'Beim Leeren des Warenkorbs ist ein Fehler aufgetreten.',
                    icon: 'error',
                    confirmButtonText: 'OK'
                });
            }
        }
    }

    // Funktion zum Fortsetzen des Buchungsprozesses
    function proceedToCheckout() {
        if ($cart.length === 0) {
            Swal.fire({
                title: "Warenkorb leer",
                text: "Bitte füge mindestens einen Sitzplatz zum Warenkorb hinzu.",
                icon: "warning",
                confirmButtonText: "OK",
            });
            return;
        }
        navigate('/checkout'); // Passe den Pfad entsprechend an
    }

    // Funktion zum Aktualisieren des Rabatts eines Sitzplatzes
    function handleDiscountChange(seat, event) {
        const selectedId = event.target.value;
        const selectedDiscount = discountOptions.find(d => d.id === selectedId) || { id: 'none', label: 'Kein Rabatt', amount: 0 };

        // Update des Sitzplatzes mit dem ausgewählten Rabatt
        const updatedSeat = { ...seat, discount: selectedId !== 'none' ? selectedDiscount : null };

        // Aktualisieren des Stores immutabel
        const updatedCart = $cart.map(s => s.seat_id === seat.seat_id && s.showtime_id === seat.showtime_id ? updatedSeat : s);
        cart.set(updatedCart);

        // Optional: Anzeige einer Bestätigung
        if (selectedId !== 'none') {
            Swal.fire({
                title: "Rabatt angewendet",
                text: `Du hast einen Rabatt von ${selectedDiscount.amount} € für diesen Sitzplatz ausgewählt. Bitte bringe deinen ${selectedDiscount.label}-Ausweis mit.`,
                icon: "success",
                timer: 2000,
                showConfirmButton: false
            });
        } else {
            Swal.fire({
                title: "Rabatt entfernt",
                text: `Der Rabatt für diesen Sitzplatz wurde entfernt.`,
                icon: "info",
                timer: 2000,
                showConfirmButton: false
            });
        }
    }
</script>

<style>
    .cart-container {
    max-width: 900px;
    margin: 2rem auto;
    padding: 2rem;
    background: #fdfdfd;
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    font-family: 'Roboto', sans-serif;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.cart-container:hover {
    transform: translateY(-10px);
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
}

h1, h2 {
    text-align: center;
    color: #2c3e50;
}

.cart-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    margin-bottom: 2rem;
}

.cart-table th, .cart-table td {
    padding: 1rem;
    text-align: center;
    border-bottom: 1px solid #ddd;
}

.cart-table th {
    background-color: #ecf0f1;
    color: #34495e;
    font-weight: bold;
}

.cart-table tr:hover {
    background-color: #f9f9f9;
    transform: scale(1.01);
    transition: transform 0.3s ease;
}

.remove-btn, .clear-btn, .proceed-btn {
    font-size: 1rem;
    font-weight: bold;
    border: none;
    border-radius: 10px;
    padding: 0.7rem 1.2rem;
    cursor: pointer;
    transition: background-color 0.3s ease, transform 0.2s;
}

.remove-btn {
    background-color: #e74c3c;
    color: #fff;
}

.clear-btn {
    background-color: #95a5a6;
    color: white;
}

.proceed-btn {
    background-color: #3498db;
    color: #fff;
}

.remove-btn:hover, .clear-btn:hover, .proceed-btn:hover {
    transform: translateY(-3px);
    opacity: 0.9;
}

.showtime-details {
    background: #f9f9f9;
    border: 1px solid #ddd;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
}

.discount-select {
    padding: 0.5rem;
    border-radius: 8px;
    border: 1px solid #ccc;
    transition: border-color 0.3s ease;
}

.discount-select:focus {
    border-color: #3498db;
    outline: none;
}


/* Responsive Design */
@media (max-width: 768px) {
    .cart-table th, .cart-table td {
        padding: 0.5rem;
        font-size: 0.9rem;
    }
    button {
        font-size: 0.9rem;
        background: #3498db;
    }
}

</style>

<main class="cart-container">
    <h1>Warenkorb: {totalPrice.toFixed(2)} €</h1>

    {#if $cart.length === 0}
        <p>Dein Warenkorb ist leer.</p>
    {:else}
        {#each $groupedCart as group}
            <!-- Anzeige der Film- und Vorstellungsdetails -->
            <div class="showtime-details">
                <h2>Film: {group.movie.title}</h2>
                <p>Startzeit: {new Date(group.showtime.start_time).toLocaleString('de-DE', { hour: '2-digit', minute: '2-digit' })}, Kinosaal: {group.showtime.screen_id}</p>
                
            </div>

            <!-- Anzeige der Sitzplätze für diese Gruppe -->
            <table class="cart-table">
                <thead>
                    <tr>
                        <th>Sitzplatz</th>
                        <th>Typ</th>
                        <th>Preis</th>
                        <th>Ermäßigung auswählen</th>
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
                            <td>{seat.price.toFixed(2)} € {seat.discount ? `(-${seat.discount.amount} €)` : ''}</td>
                            <td>
                                <select class="discount-select" value={seat.discount?.id || 'none'} on:change={(e) => handleDiscountChange(seat, e)}>
                                    {#each discountOptions as discount}
                                        <option value="{discount.id}">{discount.label}</option>
                                    {/each}
                                </select>
                            </td>
                            <td>
                                <button class="remove-btn" on:click={() => handleRemove(seat.seat_id, seat.showtime_id)}>
                                    <i class="fas fa-trash"></i> Entfernen
                                </button>
                            </td>
                        </tr>
                    {/each}
                </tbody>
            </table>
        {/each}

        <div class="button-group">
            <button class="clear-btn" on:click={handleClearCart}>
                <i class="fas fa-ban"></i> Warenkorb leeren
            </button>
            <button class="proceed-btn" on:click={proceedToCheckout}>
                <i class="fas fa-arrow-right"></i> Zur Buchung
            </button>
        </div>

        <h2>Gesamtpreis: {totalPrice.toFixed(2)} €</h2>
    {/if}

    <button on:click={() => navigate('/')}>Home</button>
</main>
