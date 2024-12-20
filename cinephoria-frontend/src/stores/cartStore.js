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
    fetchMovieDetails,
    fetchDiscountsForSeatType
} from '../services/api.js';

const cart = writable([]);
const cartError = writable(null);
const validUntil = writable(null);

export { cart, cartError, validUntil };

// Cache für Discounts pro seat_type_id
const discountsCache = {};

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

        if (cart_items.length > 0) {
            // Setze validUntil nur, wenn der Warenkorb nicht leer ist
            validUntil.set(validUntilStr ? new Date(validUntilStr) : null);
            console.log('validUntil gesetzt:', validUntilStr ? new Date(validUntilStr) : null);
        } else {
            // Entferne validUntil, wenn der Warenkorb leer ist
            validUntil.set(null);
            console.log('validUntil entfernt, da der Warenkorb leer ist.');
        }

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
                
                const seatTypeId = seatDetails.seat_type_id;
                console.log(`Abrufen der Discounts für seat_type_id: ${seatTypeId}`);

                let discounts;
                if (discountsCache[seatTypeId]) {
                    // Verwenden des gecachten Discounts
                    discounts = discountsCache[seatTypeId];
                    console.log(`Verwenden des gecachten Discounts für seat_type_id ${seatTypeId}:`, discounts);
                } else {
                    // Abrufen der Discounts und Cachen
                    discounts = await fetchDiscountsForSeatType(seatTypeId);
                    discountsCache[seatTypeId] = discounts;
                    console.log(`Discounts für seat_type_id1111111111111 ${seatTypeId}:`, discounts);
                }

                return {
                    ...item,
                    ...seatDetails, 
                    showtime: showtimeDetails,
                    movie: movieDetails,
                    discounts // Hinzufügen der Discounts zum Cart-Item
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
                    movie: null,
                    discounts: [] // Sicherstellen, dass Discounts auch bei Fehlern vorhanden sind
                };
            }
        }));

        cart.set(enrichedItems);
        console.log('Warenkorb erfolgreich geladen:', enrichedItems);
    } catch (error) {
        console.error('Fehler beim Laden des Warenkorbs:', error);
        cartError.set(error.message || 'Fehler beim Laden des Warenkorbs.');
        validUntil.set(null); // Sicherstellen, dass validUntil entfernt wird bei Fehler
    }
}


// Initiales Laden des Warenkorbs
loadCart();

// Laden des Warenkorbs bei Änderungen der Authentifizierung
authStore.subscribe(() => {
    loadCart();
});

// Funktion zum Hinzufügen eines Sitzes zum Warenkorb
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

// Funktion zum Entfernen eines Sitzes aus dem Warenkorb
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

// Funktion zum Leeren des Warenkorbs
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