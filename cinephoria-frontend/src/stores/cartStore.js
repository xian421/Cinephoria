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
const validUntil = writable(null);

export { cart, cartError, validUntil };

export async function loadCart() {
    const token = get(authStore).token;
    cartError.set(null);

    try {
        let response;
        if (token) {
            response = await fetchUserCart(token);
        } else {
            response = await fetchGuestCart();
        }

        const { cart_items, valid_until: validUntilStr } = response;

        validUntil.set(validUntilStr ? new Date(validUntilStr) : null);

        // 'reserved_until' wird noch ausgelesen, falls es künftig relevant ist.
        let items = cart_items.map(item => ({
            ...item,
            reserved_until: item.reserved_until ? new Date(item.reserved_until) : null
        }));

        const enrichedItems = await Promise.all(items.map(async (item) => {
            try {
                const seatDetails = await fetchSeatById(item.seat_id);
                const showtimeDetails = await fetchShowtimeDetails(item.showtime_id);
                const movieDetails = showtimeDetails 
                    ? await fetchMovieDetails(showtimeDetails.movie_id)
                    : null;
                    console.log('showtimesdetail', showtimeDetails);
                return {
                    ...item,
                    ...seatDetails, 
                    showtime: showtimeDetails,
                    movie: movieDetails
                };
            } catch (error) {
                console.error(`Fehler beim Abrufen der Details für seat_id ${item.seat_id}:`, error);
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
        if (error.message === 'Der Sitzplatz ist bereits reserviert.') {
            cartError.set('Der gewählte Sitzplatz ist bereits reserviert.');
        } else {
            cartError.set(error.message || 'Fehler beim Hinzufügen zum Warenkorb.');
        }
        throw error;
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
