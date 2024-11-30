// src/services/api.js
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
        const response = await fetch(`${API_BASE_URL}/seats?&screen_id=${screen_id}`, {
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












