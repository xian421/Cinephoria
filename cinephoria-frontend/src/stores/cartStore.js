// src/stores/cartStore.js
import { writable } from 'svelte/store';
import { authStore } from './authStore';
import { get } from 'svelte/store';
import {
    fetchUserCart,
    addToUserCart,
    removeFromUserCart,
    clearUserCart,
    fetchGuestCart,
    addToGuestCart,
    removeFromGuestCart,
    clearGuestCart,
    fetchSeatById,
    fetchShowtimeDetails,
    fetchMovieDetails
} from '../services/api.js';

const cart = writable([]);
const cartError = writable(null);
const validUntil = writable(null); // Neuer Store für valid_until

export { cart, cartError, validUntil };

export async function loadCart() {
    const token = get(authStore).token;
    cartError.set(null);
    try {
        let response = {};
        if (token) {
            // Benutzer ist eingeloggt
            response = await fetchUserCart(token);
        } else {
            // Gast
            response = await fetchGuestCart();
        }

        const { cart_items, valid_until: validUntilStr } = response;

        if (validUntilStr) {
            validUntil.set(new Date(validUntilStr));
        } else {
            validUntil.set(null);
        }

        // Konvertiere 'reserved_until' von ISO-Strings zu Date-Objekten
        let items = cart_items.map(item => ({
            ...item,
            reserved_until: item.reserved_until ? new Date(item.reserved_until) : null
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
                return {
                    ...item,
                    ...seatDetails, // Fügt 'row', 'number', 'type' und 'price' hinzu
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
                    showtime: null,
                    movie: null
                };
            }
        }));

        cart.set(enrichedItems);
    } catch (error) {
        console.error('Fehler beim Laden des Warenkorbs:', error);
        cartError.set(error.message || 'Fehler beim Laden des Warenkorbs.');
    }
}

loadCart();

authStore.subscribe(() => {
    loadCart();
});

export async function addToCart(seat, showtime_id) {
    const token = get(authStore).token;
    cartError.set(null);
    try {
        if (token) {
            await addToUserCart(token, seat.seat_id, seat.price, showtime_id);
        } else {
            await addToGuestCart(seat.seat_id, seat.price, showtime_id);
        }
        await loadCart();
    } catch (error) {
        console.error('Fehler beim Hinzufügen zum Warenkorb:', error);
        // Spezifische Fehlerbehandlung
        if (error.message === 'Der Sitzplatz ist bereits reserviert.') {
            cartError.set('Der gewählte Sitzplatz ist bereits reserviert.');
        } else {
            cartError.set(error.message || 'Fehler beim Hinzufügen zum Warenkorb.');
        }
        throw error; // Fehler weiterwerfen
    }
}

export async function removeFromCart(seat_id, showtime_id) {
    const token = get(authStore).token;
    cartError.set(null);
    try {
        if (token) {
            await removeFromUserCart(token, showtime_id, seat_id);
        } else {
            await removeFromGuestCart(showtime_id, seat_id);
        }
        await loadCart();
    } catch (error) {
        console.error('Fehler beim Entfernen aus dem Warenkorb:', error);
        cartError.set(error.message || 'Fehler beim Entfernen aus dem Warenkorb.');
    }
}

export async function clearCart() {
    const token = get(authStore).token;
    cartError.set(null);
    try {
        if (token) {
            await clearUserCart(token);
        } else {
            await clearGuestCart();
        }
        await loadCart();
    } catch (error) {
        console.error('Fehler beim Leeren des Warenkorbs:', error);
        cartError.set(error.message || 'Fehler beim Leeren des Warenkorbs.');
    }
}
