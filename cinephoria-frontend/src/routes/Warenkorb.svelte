<script>
    import { navigate } from 'svelte-routing';
    import { cart, cartError, removeFromCart, clearCart } from '../stores/cartStore.js';
    import Swal from 'sweetalert2';
    import "@fortawesome/fontawesome-free/css/all.min.css";

    import { derived } from 'svelte/store';

    // Reaktive Berechnung des Gesamtpreises
    $: totalPrice = $cart.reduce((sum, seat) => sum + (seat.price || 0), 0);

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
</script>

<style>
    .cart-container {
        padding: 2rem;
        font-family: Arial, sans-serif;
        max-width: 800px;
        margin: 0 auto;
    }

    h1 {
        text-align: center;
        margin-bottom: 2rem;
    }

    .cart-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 2rem;
    }

    .cart-table th, .cart-table td {
        border: 1px solid #ddd;
        padding: 1rem;
        text-align: center;
    }

    .cart-table th {
        background-color: #f2f2f2;
    }

    .cart-item {
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    .cart-item i {
        color: white;
    }

    .button-group {
        display: flex;
        justify-content: space-between;
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

    .remove-btn {
        background-color: #e74c3c;
        color: white;
    }

    .remove-btn:hover {
        background-color: #c0392b;
    }

    .proceed-btn {
        background-color: #2ecc71;
        color: white;
    }

    .proceed-btn:hover {
        background-color: #27ae60;
    }

    .clear-btn {
        background-color: #95a5a6;
        color: white;
    }

    .clear-btn:hover {
        background-color: #7f8c8d;
    }

    @media (max-width: 600px) {
        .cart-table th, .cart-table td {
            padding: 0.5rem;
        }

        button {
            font-size: 0.9rem;
            padding: 0.5rem;
        }
    }

    .showtime-details {
        margin-bottom: 1rem;
        padding: 1rem;
        background-color: #f9f9f9;
        border: 1px solid #ddd;
        border-radius: 5px;
    }

    .showtime-details h2 {
        margin: 0 0 0.5rem 0;
    }

    .showtime-details p {
        margin: 0.25rem 0;
    }
</style>

<main class="cart-container">
    <h1>Warenkorb</h1>

    {#if $cart.length === 0}
        <p>Dein Warenkorb ist leer.</p>
    {:else}
        {#each $groupedCart as group}
            <!-- Anzeige der Film- und Vorstellungsdetails -->
            <div class="showtime-details">
                <h2>{group.movie.title}</h2>
                <p>Startzeit: {new Date(group.showtime.start_time).toLocaleString('de-DE', { hour: '2-digit', minute: '2-digit' })}</p>
                <p>Kinosaal: {group.showtime.screen_id}</p> <!-- Optional: Kinosaal-Name hinzufügen -->
            </div>

            <!-- Anzeige der Sitzplätze für diese Gruppe -->
            <table class="cart-table">
                <thead>
                    <tr>
                        <th>Sitzplatz</th>
                        <th>Typ</th>
                        <th>Preis</th>
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
                            <td>{seat.price.toFixed(2)} €</td>
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
