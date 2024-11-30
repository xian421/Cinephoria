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
    return response.json();
};

export const validateToken = async (token) => {
    const response = await fetch(`${API_BASE_URL}/validate-token`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
    });
    return response.json();
};

export const fetchCinemas = async () => {
    const response = await fetch(`${API_BASE_URL}/cinemas`);
    return response.json();
};

export const fetchScreens = async (token) => {
    const response = await fetch(`${API_BASE_URL}/screens`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    return response.json();
};


