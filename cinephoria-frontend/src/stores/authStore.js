// src/stores/authStore.js
import { writable } from 'svelte/store';

export const authStore = writable({
    isLoggedIn: false,
    userFirstName: '',
    userLastName: '',
    initials: '',
    isAdmin: false,
    token: null,
    profile_image: 'default.png', // Standardprofilbild
    nickname: '',
    role: '',
});

export const setAuth = (auth) => {
    authStore.set(auth);
};

export const updateAuth = (updateFn) => {
    authStore.update(updateFn);
};
