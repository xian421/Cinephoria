// src/stores/pointsStore.js
import { writable } from 'svelte/store';
import { getUserPoints, redeemPoints, getPointsTransactions } from '../services/api';

// Initialer Punktestand
export const pointsStore = writable(0);

// Punkte-Transaktionen Store
export const transactionsStore = writable([]);

// Funktion zum Abrufen der aktuellen Punkte vom Backend
export async function fetchUserPointsStore(token) {
    try {
        const points = await getUserPoints(token);
        pointsStore.set(points);
        return points;
    } catch (error) {
        console.error('Fehler beim Abrufen der Punkte:', error);
        throw error;
    }
}

// Funktion zum Einlösen von Punkten
export async function redeemUserPointsStore(token, points) {
    try {
        const message = await redeemPoints(token, points);
        // Aktualisiere den Store nach erfolgreichem Einlösen
        pointsStore.update(currentPoints => currentPoints - points);
        // Transaktionshistorie abrufen (optional)
        await fetchUserTransactionsStore(token);
        return message;
    } catch (error) {
        console.error('Fehler beim Einlösen der Punkte:', error);
        throw error;
    }
}

// Funktion zum Abrufen der Punkte-Transaktionshistorie
export async function fetchUserTransactionsStore(token) {
    try {
        const transactions = await getPointsTransactions(token);
        transactionsStore.set(transactions);
        return transactions;
    } catch (error) {
        console.error('Fehler beim Abrufen der Transaktionen:', error);
        throw error;
    }
}