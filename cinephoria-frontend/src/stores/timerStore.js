// src/stores/timerStore.js
import { writable, get } from 'svelte/store';
import { validUntil } from './cartStore';

const timeLeft = writable(0);
const warning = writable(false);

let timer = null;

// Funktion zur Berechnung der verbleibenden Zeit in Sekunden
function calculateTimeLeft(validUntilDate) {
    if (!validUntilDate) return 0;
    const now = new Date();
    const diff = validUntilDate.getTime() - now.getTime();
    return Math.max(0, Math.floor(diff / 1000));
}

// Abonniere Änderungen an validUntil
validUntil.subscribe(currentValidUntil => {
    // Timer stoppen, wenn er bereits läuft
    if (timer) {
        clearInterval(timer);
        timer = null;
        console.log('Timer gestoppt.');
    }

    if (currentValidUntil && get(validUntil) && get(validUntil).getTime() > new Date().getTime()) {
        // Initialisiere timeLeft
        const calculatedTimeLeft = calculateTimeLeft(currentValidUntil);
        timeLeft.set(calculatedTimeLeft);
        warning.set(false);
        console.log('Timer gestartet mit timeLeft:', calculatedTimeLeft);

        // Starte den Timer
        timer = setInterval(() => {
            const current = get(timeLeft);
            if (current > 0) {
                timeLeft.set(current - 1);
                if (current - 1 === 60) {
                    warning.set(true);
                    console.log('Warnung: weniger als eine Minute übrig.');
                }
                if (current - 1 <= 0) {
                    clearInterval(timer);
                    timer = null;
                    console.log('Timer beendet.');
                }
            }
        }, 1000);
    } else {
        timeLeft.set(0);
        warning.set(false);
        console.log('Timer nicht gestartet, timeLeft auf 0 gesetzt.');
    }
});

// Bereinige den Timer beim Laden der Seite
if (timer) {
    clearInterval(timer);
    timer = null;
    console.log('Initialer Timer gestoppt.');
}

export { timeLeft, warning };
