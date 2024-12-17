import { writable } from 'svelte/store';
import { authStore } from './authStore';
import { get } from 'svelte/store';
import {
    fetchUserCart,
    addToUserCart,
    removeFromUserCart,
    clearUserCart,
    fetchSeatById,
    fetchShowtimeDetails,
    fetchMovieDetails
} from '../services/api';

const localStorageKey = 'persistedCart';

const cart = writable(loadCartFromStorage()); // Initial lade aus localStorage
const cartError = writable(null);

export { cart, cartError };

// Funktion zum Laden des Warenkorbs aus localStorage
function loadCartFromStorage() {
    try {
        const storedCart = localStorage.getItem(localStorageKey);
        return storedCart ? JSON.parse(storedCart) : [];
    } catch (error) {
        console.error("Fehler beim Laden des Warenkorbs aus localStorage:", error);
        return [];
    }
}

// Persistiere den Warenkorb in localStorage bei jeder Änderung
cart.subscribe(value => {
    try {
        localStorage.setItem(localStorageKey, JSON.stringify(value));
    } catch (error) {
        console.error("Fehler beim Speichern des Warenkorbs in localStorage:", error);
    }
});

// Warenkorb vom Server laden (eingeloggte Benutzer)
export async function loadCart() {
    const token = get(authStore).token;
    cartError.set(null);
    try {
        let items = [];
        if (token) {
            // Benutzer ist eingeloggt - lade Warenkorb vom Server
            items = await fetchUserCart(token);
        } else {
            // Gast
            items = await fetchGuestCart();
        }

        // Konvertiere 'reserved_until' von ISO-Strings zu Date-Objekten
        items = items.map(item => ({
            ...item,
            reserved_until: new Date(item.reserved_until)
        }));

        // Nachladen der Sitzdetails und Showtimes für jeden Sitz im Warenkorb
        const enrichedItems = await Promise.all(items.map(async (item) => {
            try {
                const seatDetails = await fetchSeatById(item.seat_id);
                const showtimeDetails = await fetchShowtimeDetails(item.showtime_id);
                const movieDetails = showtimeDetails 
                    ? await fetchMovieDetails(showtimeDetails.movie_id)
                    : null;
                console.log('seatDetails:', seatDetails);
                console.log('showtimeDetails:', showtimeDetails);
                console.log('movieDetails:', movieDetails);
                console.log('seatDetails:', seatDetails);
                return {
                    ...item,
                    ...seatDetails, // Fügt 'row', 'number', 'type' und 'price' hinzu und jetzt auch noch discount und so (siehedef get_seat(seat_id) bei app.py)
                    showtime: showtimeDetails,
                    movie: movieDetails
                };
            } catch (error) {
                console.error(`Fehler beim Abrufen der Details für seat_id ${item.seat_id}:`, error);
                // Rückgabe des ursprünglichen Items, falls Details fehlen
                return {
                    ...item,
                    row: null,
                    number: null,
                    type: null,
                    price: item.price || 0.00,
                    discount_name : null,
                    discount_amount: null,
                    discount_percentage: null,
                    showtime: null,
                    movie: null
                };
            }
        }));

            cart.set(enrichedItems);
        } else {
            // Gast - lade Warenkorb aus localStorage
            cart.set(loadCartFromStorage());
        }
    } catch (error) {
        console.error('Fehler beim Laden des Warenkorbs:', error);
        cartError.set(error.message || 'Fehler beim Laden des Warenkorbs.');
    }
}

// Sitzplatz hinzufügen
export async function addToCart(seat, showtime_id) {
    const token = get(authStore).token;
    cartError.set(null);
    try {
        if (token) {
            await addToUserCart(token, seat.seat_id, seat.price, showtime_id);
            await loadCart();
        } else {
            const currentCart = get(cart);
            const newCart = [...currentCart, { ...seat, showtime_id }];
            cart.set(newCart);
        }
    } catch (error) {
        console.error('Fehler beim Hinzufügen zum Warenkorb:', error);
        cartError.set(error.message || 'Fehler beim Hinzufügen zum Warenkorb.');
        throw error; // Fehler weiterwerfen
    }
}

// Sitzplatz entfernen
export async function removeFromCart(seat_id, showtime_id) {
    const token = get(authStore).token;
    cartError.set(null);
    try {
        if (token) {
            await removeFromUserCart(token, showtime_id, seat_id);
            await loadCart();
        } else {
            const updatedCart = get(cart).filter(
                seat => !(seat.seat_id === seat_id && seat.showtime_id === showtime_id)
            );
            cart.set(updatedCart);
        }
    } catch (error) {
        console.error('Fehler beim Entfernen aus dem Warenkorb:', error);
        cartError.set(error.message || 'Fehler beim Entfernen aus dem Warenkorb.');
    }
}

// Warenkorb leeren
export async function clearCart() {
    const token = get(authStore).token;
    cartError.set(null);
    try {
        if (token) {
            await clearUserCart(token);
            await loadCart();
        } else {
            cart.set([]);
        }
    } catch (error) {
        console.error('Fehler beim Leeren des Warenkorbs:', error);
        cartError.set(error.message || 'Fehler beim Leeren des Warenkorbs.');
    }
}

// Aktualisiere Warenkorb, wenn der Auth-Status sich ändert
authStore.subscribe(() => {
    loadCart();
});
