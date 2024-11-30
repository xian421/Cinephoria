// src/stores/authStore.js
import { writable } from 'svelte/store';

const initialState = {
    isLoggedIn: false,
    userFirstName: '',
    userLastName: '',
    initials: '',
    isAdmin: false,
};

const authStore = writable(initialState);

const setAuth = (authData) => {
    authStore.set({
        ...initialState,
        ...authData
    });
};

const updateAuth = (updateFn) => {
    authStore.update(current => ({
        ...current,
        ...updateFn(current)
    }));
};

export { authStore, setAuth, updateAuth };
