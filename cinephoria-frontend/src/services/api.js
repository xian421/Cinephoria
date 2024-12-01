// src/services/api.js
import { get } from 'svelte/store';
import { authStore } from '../stores/authStore'; 

const API_BASE_URL = 'https://cinephoria-backend-c53f94f0a255.herokuapp.com';

export const login = async (email, password) => {
    const response = await fetch(`${API_BASE_URL}/login`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
    });
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'Ein unbekannter Fehler ist aufgetreten.');
    }
    return data;
};

export const validateToken = async (token) => {
    const response = await fetch(`${API_BASE_URL}/validate-token`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
    });
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'Token ist ungültig.');
    }
    return data;
};

export const fetchCinemas = async () => {
    const response = await fetch(`${API_BASE_URL}/cinemas`);
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'Fehler beim Laden der Kinos.');
    }
    return data;
};

export const fetchScreens = async (token) => {
    const response = await fetch(`${API_BASE_URL}/screens`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'Fehler beim Laden der Kinosäle.');
    }
    return data;
};

export async function fetchSeats(screen_id, token) {
    try {
        const response = await fetch(`${API_BASE_URL}/seats?screen_id=${screen_id}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            throw new Error('Fehler beim Abrufen der Sitze');
        }

        const data = await response.json();
        return data; // Stelle sicher, dass data das Feld 'seats' enthält
    } catch (error) {
        console.error('Error fetching seats:', error);
        throw error;
    }
}

// Funktion zum Erstellen eines neuen Sitzes
export const createSeat = async (screen_id, row, number, type = 'standard') => {
    try {
        const token = get(authStore).token;
        const response = await fetch(`${API_BASE_URL}/seats`, { // POST zum Erstellen eines Sitzes
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ screen_id, row, number, type }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Fehler beim Erstellen des Sitzes');
        }

        return data;
    } catch (error) {
        console.error('Error creating seat:', error);
        throw error;
    }
};

// Funktion zum Löschen eines Sitzes
export const deleteSeat = async (seatId) => {
    try {
        const token = get(authStore).token;
        const response = await fetch(`${API_BASE_URL}/seats/${seatId}`, { // DELETE zum Löschen eines Sitzes
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            },
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Fehler beim Löschen des Sitzes');
        }

        return data;
    } catch (error) {
        console.error('Error deleting seat:', error);
        throw error;
    }
};


export async function deleteAllSeats(screenId, token) {
    const response = await fetch(`${API_BASE_URL}/seats?screen_id=${screenId}`, {
        method: 'DELETE',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Fehler beim Löschen aller Sitze');
    }

    return await response.json();
}


export async function fetchNowPlayingMovies(token) {
    const response = await fetch(`${API_BASE_URL}/movies/now_playing`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Fehler beim Abrufen der Filme');
    }

    return await response.json();
}


export async function createShowtime(showtimeData, token) {
    const response = await fetch(`${API_BASE_URL}/showtimes`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(showtimeData),
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Fehler beim Erstellen des Showtimes');
    }

    return await response.json();
}

export const fetchShowtimes = async (screenId, token) => {
    const url = screenId 
        ? `${API_BASE_URL}/showtimes?screen_id=${screenId}` 
        : `${API_BASE_URL}/showtimes`;
    const response = await fetch(url, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });

    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'Fehler beim Abrufen der Showtimes');
    }
    return data;
};

// Funktion zum Aktualisieren einer Showtime
export const updateShowtime = async (showtimeId, showtimeData, token) => {
    const response = await fetch(`${API_BASE_URL}/showtimes/${showtimeId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(showtimeData),
    });

    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'Fehler beim Aktualisieren des Showtimes');
    }
    return data;
};