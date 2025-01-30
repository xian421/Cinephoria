// src/stores/pfandStore.js
import { writable } from 'svelte/store';

/**
 * Store für Pfand-Optionen.
 */
export const pfandStore = writable([]);

/**
 * Funktion zum Setzen der Pfand-Optionen.
 * @param {Array} newPfandOptions - Neue Liste von Pfand-Optionen.
 */
export function setPfandOptions(newPfandOptions) {
    pfandStore.set(newPfandOptions);
}
