// src/services/api.js
const API_BASE_URL = 'https://cinephoria-backend-c53f94f0a255.herokuapp.com';

/**
 * Ruft alle Supermarktkassenartikel ab.
 * @param {String} token - Das Authentifizierungs-Token.
 * @returns {Promise<Object>} - Ein Array von Produktobjekten.
 * @throws {Error} - Bei HTTP-Fehlern.
 */

export async function fetchSupermarketitems(token) {
    const response = await fetch(`${API_BASE_URL}/supermarkt/items`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    if (!response.ok) {
        throw new Error('Netzwerkantwort war nicht ok');
    }
    return response.json();
}

export async function fetchPfandOptions(token) {
    const response = await fetch(`${API_BASE_URL}/supermarkt/pfand`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    if (!response.ok) {
        throw new Error('Netzwerkantwort war nicht ok');
    }
    return response.json();
}

export async function addSupermarketItem(token, barcode, item_name, price, category, pfand_id) {
    const response = await fetch(`${API_BASE_URL}/supermarkt/items`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ barcode, item_name, price, category, pfand_id })
    });
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Netzwerkantwort war nicht ok');
    }
    return response.json();
}

export async function updateSupermarketItem(token, item_id, barcode, item_name, price, category, pfand_id) {
    const response = await fetch(`${API_BASE_URL}/supermarkt/items/${item_id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ barcode, item_name, price, category, pfand_id: pfand_id !== null ? pfand_id : null })
    });
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Netzwerkantwort war nicht ok');
    }
    return response.json();
}

export async function fetchProductByBarcode(token, barcode) {
    const response = await fetch(`${API_BASE_URL}/supermarkt/items/barcode/${barcode}`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Netzwerkantwort war nicht ok');
    }

    return response.json();
}


export async function deleteSupermarketItem(token, item_id) {
    const response = await fetch(`${API_BASE_URL}/supermarkt/items/${item_id}`, {
        method: 'DELETE',
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Netzwerkantwort war nicht ok');
    }
    return response.json();
}


