// src/stores/authStore.js
import { writable } from 'svelte/store';

// Authentifizierungs-Status (Svelte Store)
export const authStore = writable({
    isLoggedIn: !!localStorage.getItem('token'),
    userFirstName: '',
    userLastName: '',
    initials: '',
    isAdmin: false,
});
