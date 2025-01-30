// src/stores/sortStore.js
import { writable } from 'svelte/store';

/**
 * Store für Sortierinformationen.
 */
export const sortStore = writable({
    column: '',
    direction: 'asc'
});

/**
 * Funktion zum Aktualisieren der Sortierung.
 * @param {String} column - Die Spalte, nach der sortiert wird.
 */
export function updateSort(column) {
    sortStore.update(current => {
        if (current.column === column) {
            return {
                column,
                direction: current.direction === 'asc' ? 'desc' : 'asc'
            };
        } else {
            return {
                column,
                direction: 'asc'
            };
        }
    });
}
