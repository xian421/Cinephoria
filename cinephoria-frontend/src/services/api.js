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


export const fetchNowPlayingMovies = async () => {
    const response = await fetch(`${API_BASE_URL}/movies/now_playing`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    });

    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'Fehler beim Abrufen der Filme');
    }
    return data;
};


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


export const fetchShowtimesPublic = async (screenId = null) => {
    let url = `${API_BASE_URL}/showtimes`;
    if (screenId) {
        url += `?screen_id=${screenId}`;
    }

    const response = await fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    });

    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'Fehler beim Abrufen der Showtimes');
    }
    return data;
};


export const fetchMovieDetails = async (movie_ID) => {
    const response = await fetch(`${API_BASE_URL}/movies/${movie_ID}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    });

    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'Fehler beim Abrufen des Films');
    }
    return data;
};



export const fetchMovieFSK = async (movie_id) => {
    const response = await fetch(`${API_BASE_URL}/movie/${movie_id}/release_dates`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    });
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'Fehler beim Abrufen des FSK');
    }
    return data;
};


export const fetchShowtimesByMovie = async (movieId) => {
    const url = `${API_BASE_URL}/showtimes?movie_id=${movieId}`;

    const response = await fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    });

    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'Fehler beim Abrufen der Showtimes');
    }
    return data;
};


export const fetchSeatsForShowtime = async (showtimeId, token) => {
    const url = `${API_BASE_URL}/showtimes/${showtimeId}/seats`;

    const response = await fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
        },
    });

    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'Fehler beim Abrufen der Sitzplätze.');
    }
    return data;
};

// Funktion zum Erstellen einer Buchung
export const createBooking = async (showtime_id, seatIds, token, orderID) => {
    const response = await fetch(`${API_BASE_URL}/bookings`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
            showtime_id,
            seat_ids: seatIds,
            order_id: orderID // Neue Feld für PayPal Order ID
        }),
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Fehler beim Erstellen der Buchung.');
    }
    return await response.json();
};


// Funktion zum Erstellen einer PayPal-Order
export const createPayPalOrder = async (showtime_id, selectedSeats, token) => {
    const response = await fetch(`${API_BASE_URL}/paypal/order/create`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
            showtime_id,
            selected_seats: selectedSeats
        }),
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Fehler beim Erstellen der PayPal-Order');
    }

    const data = await response.json();
    return data; // { orderID: '...' }
};

// Funktion zum Erfassen einer PayPal-Order
export const capturePayPalOrder = async (orderID, token) => {
    const response = await fetch(`${API_BASE_URL}/paypal/order/capture`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
            orderID
        }),
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Fehler beim Erfassen der PayPal-Order');
    }

    const data = await response.json();
    return data; // { status: 'COMPLETED' }
};
export const fetchProfile = async (token) => {
    try {
        const response = await fetch(`${API_BASE_URL}/profile`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Fehler beim Abrufen des Profils');
        }
        return data;
    } catch (error) {
        console.error('Error fetching profile:', error);
        throw error;
    }
};

// Funktion zum Aktualisieren des Profilbildes
export const updateProfileImage = async (token, profileImage) => {
    try {
        const response = await fetch(`${API_BASE_URL}/profile/image`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ profile_image: profileImage })
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Fehler beim Aktualisieren des Profilbildes');
        }
        return data;
    } catch (error) {
        console.error('Error updating profile image:', error);
        throw error;
    }
};

// Funktion zum Abrufen der verfügbaren Profilbilder
export const fetchAvailableProfileImages = async (token) => {
    try {
        const response = await fetch(`${API_BASE_URL}/profile/images`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Fehler beim Abrufen der Profilbilder');
        }
        return data.images;
    } catch (error) {
        console.error('Error fetching available profile images:', error);
        throw error;
    }
};

// src/services/api.js

export const batchUpdateSeats = async (screenId, seatsToAdd, seatsToDelete, seatsToUpdate) => {
    try {
        const token = get(authStore).token;
        const response = await fetch(`${API_BASE_URL}/seats/batch_update`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify({
                screen_id: screenId,
                seats_to_add: seatsToAdd,       // Array von {row: 'A', number: 1, type: 'standard'}
                seats_to_delete: seatsToDelete, // Array von {row: 'B', number: 2}
                seats_to_update: seatsToUpdate, // Array von {row: 'C', number: 3, type: 'vip'}

            }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Fehler beim Aktualisieren der Sitze');
        }

        return data;
    } catch (error) {
        console.error('Error updating seats:', error);
        throw error;
    }
};
