// src/stores/profileStore.js
import { writable } from 'svelte/store';
import { get } from 'svelte/store';
import { authStore, updateAuth } from './authStore.js'; // Importiere updateAuth
import { fetchProfile } from '../services/api.js'; // Stelle sicher, dass fetchProfile exportiert wird

export const profileStore = writable({
    vorname: '',
    nachname: '',
    email: '',
    role: '',
    profile_image: 'default.png',
    nickname: ''
});

// Funktion zum Laden der Profildaten
export async function loadProfile() {
    const token = get(authStore).token;
    if (!token) {
        // Falls kein Token vorhanden ist, setze den Store auf Standardwerte
        profileStore.set({
            vorname: '',
            nachname: '',
            email: '',
            role: '',
            profile_image: 'default.png',
            nickname: ''
        });
        return;
    }

    try {
        const data = await fetchProfile(token);
        profileStore.set(data);

        // Aktualisiere den authStore mit den Profildaten
        updateAuth(current => ({
            ...current,
            userFirstName: data.vorname,
            userLastName: data.nachname,
            initials: getInitials(data.vorname, data.nachname),
            isAdmin: data.role.toLowerCase() === 'admin',
            email: data.email,
            role: data.role,
            nickname: data.nickname,
            profile_image: data.profile_image || 'default.png',
        }));
    } catch (error) {
        console.error('Fehler beim Laden des Profils:', error);
        // Optional: Fehlerbehandlung, z.B. Nutzer ausloggen oder Standardwerte setzen
    }
}

// Hilfsfunktion zur Generierung von Initialen
function getInitials(vorname, nachname) {
    const vorInitial = vorname ? vorname.charAt(0).toUpperCase() : '';
    const nachInitial = nachname ? nachname.charAt(0).toUpperCase() : '';
    return `${vorInitial}${nachInitial}`;
}
