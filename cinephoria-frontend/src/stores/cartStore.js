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
    fetchDiscountsForSeatType,
    updateUserCart as apiUpdateUserCart, 
    updateGuestCart as apiUpdateGuestCart,
    getGuestId
} from '../services/api.js';

import { showErrorAlert, showSuccessToast, showCustomAlert } from '../utils/notifications.js'; // Importiere die Benachrichtigungsfunktionen

const cart = writable([]);
const cartError = writable(null);
const validUntil = writable(null);

export { cart, cartError, validUntil };

// Cache für Discounts pro seat_type_id
const discountsCache = {};

// Funktion zum Laden des Warenkorbs
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
        } else {
            // Entferne validUntil, wenn der Warenkorb leer ist
            validUntil.set(null);
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

                let discounts;
                if (discountsCache[seatTypeId]) {
                    // Verwenden des gecachten Discounts
                    discounts = discountsCache[seatTypeId];
                } else {
                    // Abrufen der Discounts und Cachen
                    discounts = await fetchDiscountsForSeatType(seatTypeId);
                    discountsCache[seatTypeId] = discounts;
                }

                // Finden des ausgewählten Discounts basierend auf seat_type_discount_id
                const selectedDiscount = item.seat_type_discount_id 
                    ? discounts.find(d => d.seat_type_discount_id === item.seat_type_discount_id) 
                    : null;

                return {
                    ...item,
                    ...seatDetails, 
                    showtime: showtimeDetails,
                    movie: movieDetails,
                    discounts, // Hinzufügen der Discounts zum Cart-Item
                    selectedDiscount, // Vollständiges Discount-Objekt
                };
            } catch (error) {
                console.error(`Fehler beim Abrufen der Details für seat_id ${item.seat_id}:`, error);
                showErrorAlert(`Fehler beim Abrufen der Details für Sitzplatz ${item.seat_id}.`);
                return {
                    ...item,
                    row: null,
                    number: null,
                    type: null,
                    price: item.price || 0.00,
                    showtime: null,
                    movie: null,
                    discounts: [], // Sicherstellen, dass Discounts auch bei Fehlern vorhanden sind
                    selectedDiscount: null,
                };
            }
        }));

        // Überprüfen der enrichedItems
        enrichedItems.forEach(item => {
            if (!item.seat_id) {
                console.warn('Ein Cart-Item hat keine seat_id:', item);
            }
            if (!item.showtime_id) {
                console.warn('Ein Cart-Item hat keine showtime_id:', item);
            }
        });

        cart.set(enrichedItems);
    } catch (error) {
        console.error('Fehler beim Laden des Warenkorbs:', error);
        cartError.set(error.message || 'Fehler beim Laden des Warenkorbs.');
        showErrorAlert(error.message || 'Fehler beim Laden des Warenkorbs.');
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
        showSuccessToast(`Sitzplatz ${seat.row}${seat.number} wurde zum Warenkorb hinzugefügt.`);
    } catch (error) {
       // console.error('Fehler beim Hinzufügen zum Warenkorb:', error);
       console.log('HIIIIIER: ', error.message);
        if (error.message === 'Der Sitzplatz ist bereits reserviert') {
            console.log('Der Sitzplatz ist beredsadsadsadits reserviert.');
            showCustomAlert(
                'Sitzplatz bereits reserviert',
                'Der Sitzplatz ist bereits reserviert. Bitte wähle einen anderen Sitzplatz.',
                'warning',
                'Neu laden',
                {},
                () => {
                    window.location.reload();
                }
            );
        } else {
            showErrorAlert(error.message || 'Fehler beim Hinzufügen zum Warenkorb.');
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
        showSuccessToast(`Sitzplatz wurde aus dem Warenkorb entfernt.`);
    } catch (error) {
        console.error('Fehler beim Entfernen aus dem Warenkorb:', error);
        showErrorAlert(error.message || 'Fehler beim Entfernen aus dem Warenkorb.');
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
        showSuccessToast('Warenkorb wurde geleert.');
    } catch (error) {
        console.error('Fehler beim Leeren des Warenkorbs:', error);
        showErrorAlert(error.message || 'Fehler beim Leeren des Warenkorbs.');
    }
}

// Funktion zum Aktualisieren des Rabatts eines Sitzplatzes im Warenkorb
export async function updateCartDiscount(seat, discount_id = null) {
    const token = get(authStore).token;
    cartError.set(null);
    const guestId = getGuestId(); // Stelle sicher, dass du eine Methode hast, um die guest_id zu erhalten
    console.log('Hier startet updateCartDiscount in der CartStore Komponente mit discount_id:', discount_id);
    try {
        if (token) {
            console.log('Aktualisieren des Rabatts für seat_id:', seat.seat_id, 'mit discount_id:', discount_id, 'für showtime_id:', seat.showtime_id);
            await apiUpdateUserCart(token, seat.seat_id, seat.showtime_id, discount_id);
        } else {
            console.log('Aktualisieren des Rabatts für seat_id:', seat.seat_id, 'mit discount_id:', discount_id, 'für showtime_id:', seat.showtime_id);
            await apiUpdateGuestCart(guestId, seat.seat_id, seat.showtime_id, discount_id);
        }
        await loadCart();
        showSuccessToast(`Rabatt für Sitzplatz ${seat.row}${seat.number} wurde aktualisiert.`);
        console.log('updateCartDiscount abgeschlossen für seat_id:', seat.seat_id);
    } catch (error) {
        console.error('Fehler beim Aktualisieren des Rabatts:', error);
        showErrorAlert(error.message || 'Fehler beim Aktualisieren des Rabatts.');
        throw error;
    }
}
