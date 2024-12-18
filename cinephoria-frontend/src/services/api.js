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
        // Stellen Sie sicher, dass 'data.seats' die Felder 'type' und 'price' enthält
        return data; 
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

export const fetchMovieDetails = async (movie_id) => {
    try {
        const response = await fetch(`${API_BASE_URL}/movies/${movie_id}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Fehler beim Abrufen des Films');
        }
        return data; // TMDB Movie details
    } catch (error) {
        console.error('Fehler beim Abrufen der Filmdetails:', error);
        throw error;
    }
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
    // 'data.seats' enthält jetzt 'type' und 'price'
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

// Funktion zum Aktualisieren des Profils
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

// Funktion zum Abrufen aller Sitztypen
export const fetchSeatTypes = async (token) => {
    try {
        const response = await fetch(`${API_BASE_URL}/seat_types`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Fehler beim Abrufen der Sitztypen');
        }
        return data.seat_types; // Hier wird das Array direkt zurückgegeben
    } catch (error) {
        console.error('Error fetching seat types:', error);
        throw error;
    }
};


// Funktion zum Hinzufügen eines neuen Sitztyps
export const addSeatType = async (token, name, price, color, icon) => {
    try {
        const response = await fetch(`${API_BASE_URL}/seat_types`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({name, price, color, icon})
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Fehler beim Hinzufügen des Sitztyps');
        }
        return data; // Gibt die Nachricht und seat_type_id zurück
    } catch (error) {
        console.error('Error adding seat type:', error);
        throw error;
    }
};

// Funktion zum Aktualisieren eines bestehenden Sitztyps
export const updateSeatType = async (token, seatTypeId, updates) => {
    try {
        const response = await fetch(`${API_BASE_URL}/seat_types/${seatTypeId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(updates) // updates enthält { name, price }
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Fehler beim Aktualisieren des Sitztyps');
        }
        return data; // Gibt die Nachricht zurück
    } catch (error) {
        console.error('Error updating seat type:', error);
        throw error;
    }
};



// Hilfsfunktion, um guest_id zu holen
function getGuestId() {
    let guest_id = localStorage.getItem('guest_id');
    if (!guest_id) {
        guest_id = crypto.randomUUID();
        localStorage.setItem('guest_id', guest_id);
    }
    return guest_id;
}

export async function fetchUserCart(token) {
    const response = await fetch(`${API_BASE_URL}/user/cart`, {
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        }
    });
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'Fehler beim Abrufen des User-Warenkorbs');
    }
    return data; // Rückgabe von { valid_until, cart_items }
}

export async function addToUserCart(token, seat_id, price, showtime_id) {
    const response = await fetch(`${API_BASE_URL}/user/cart`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ seat_id, price, showtime_id }) // showtime_id hinzufügen
    });

    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'Fehler beim Hinzufügen zum User-Warenkorb');
    }
    return data;
}

export async function removeFromUserCart(token, showtime_id, seat_id) {
    const response = await fetch(`${API_BASE_URL}/user/cart/${showtime_id}/${seat_id}`, {
        method: "DELETE",
        headers: {
            "Authorization": `Bearer ${token}`
        },
    });
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'Fehler beim Entfernen aus dem User-Warenkorb');
    }
    return data;
}

export async function clearUserCart(token) {
    const response = await fetch(`${API_BASE_URL}/user/cart`, {
        method: "DELETE",
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'Fehler beim Leeren des User-Warenkorbs');
    }
    return data;
}

export async function fetchGuestCart() {
    const guest_id = getGuestId();
    const response = await fetch(`${API_BASE_URL}/guest/cart?guest_id=${guest_id}`);
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'Fehler beim Abrufen des Guest-Warenkorbs');
    }
    return data; // Rückgabe von { valid_until, cart_items }
}



export async function addToGuestCart(seat_id, price, showtime_id) {
    const guest_id = getGuestId();
    const response = await fetch(`${API_BASE_URL}/guest/cart`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ guest_id, seat_id, price, showtime_id }) // showtime_id hinzufügen
    });
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'Fehler beim Hinzufügen zum Guest-Warenkorb');
    }
    return data;
}

export async function removeFromGuestCart(showtime_id, seat_id) {
    const guest_id = getGuestId();
    const response = await fetch(`${API_BASE_URL}/guest/cart/${showtime_id}/${seat_id}?guest_id=${guest_id}`, {
        method: "DELETE"
    });
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'Fehler beim Entfernen aus dem Guest-Warenkorb');
    }
    return data;
}

export async function clearGuestCart() {
    const guest_id = getGuestId();
    const response = await fetch(`${API_BASE_URL}/guest/cart?guest_id=${guest_id}`, {
        method: "DELETE"
    });
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'Fehler beim Leeren des Guest-Warenkorbs');
    }
    return data;
}

export async function fetchSeatsWithReservation(showtime_id, token = null, guest_id = null) {
    const urlParams = token ? '' : `?guest_id=${guest_id}`;
    const headers = {
        'Content-Type': 'application/json',
    };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}/showtimes/${showtime_id}/seats${urlParams}`, {
        headers,
    });

    if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.error || 'Fehler beim Laden der Sitzplätze');
    }

    const data = await response.json();
    return data;
}

export async function fetchSeatById(seat_id) {
    try {
        const response = await fetch(`${API_BASE_URL}/seats/${seat_id}`);
        if (!response.ok) {
            throw new Error(`Error: ${response.statusText}`);
        }
        const data = await response.json();
        return data.seat;
    } catch (error) {
        console.error('Fehler beim Abrufen des Sitzes:', error);
        throw error;
    }
}

export const fetchShowtimeDetails = async (showtime_id) => {
    try {
        const response = await fetch(`${API_BASE_URL}/showtimes?showtime_id=${showtime_id}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Fehler beim Abrufen der Showtime-Details');
        }
        return data.showtimes.find(st => st.showtime_id === showtime_id); // Passe dies an die Antwortstruktur an
    } catch (error) {
        console.error('Fehler beim Abrufen der Showtime-Details:', error);
        throw error;
    }
};





export const fetchDiscounts = async () => {
    try {
        const token = get(authStore).token;
        const response = await fetch(`${API_BASE_URL}/discounts`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Fehler beim Abrufen der Discounts');
        }
        return data; // Erwartet { discounts: [...] }
    } catch (error) {
        console.error('Error fetching discounts:', error);
        throw error;
    }
};
// Funktion zum Hinzufügen eines neuen Discounts
export const addDiscount = async (token, name, description) => {
    try {
        const response = await fetch(`${API_BASE_URL}/discounts`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ name, description })
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Fehler beim Hinzufügen des Discounts');
        }
        return data; // { message: 'Discount hinzugefügt', discount_id: ... }
    } catch (error) {
        console.error('Error adding discount:', error);
        throw error;
    }
};


// Funktion zum Aktualisieren eines Discounts
export const updateDiscount = async (token, discountId, name, description) => {
    try {
        const response = await fetch(`${API_BASE_URL}/discounts/${discountId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ name, description })
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Fehler beim Aktualisieren des Discounts');
        }
        return data; // { message: 'Discount aktualisiert' }
    } catch (error) {
        console.error('Error updating discount:', error);
        throw error;
    }
};


// Funktion zum Löschen eines Discounts
export const deleteDiscount = async (token, discountId) => {
    try {
        const response = await fetch(`${API_BASE_URL}/discounts/${discountId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Fehler beim Löschen des Discounts');
        }
        return data; // { message: 'Discount gelöscht' }
    } catch (error) {
        console.error('Error deleting discount:', error);
        throw error;
    }
};


// Funktion zum Zuweisen eines Discounts zu einem Sitztyp
export const assignDiscountToSeatType = async (token, seatTypeId, discountId, discountAmount = null, discountPercentage = null) => {
    try {
        const response = await fetch(`${API_BASE_URL}/seat_type_discounts`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                seat_type_id: seatTypeId,
                discount_id: discountId,
                discount_amount: discountAmount,
                discount_percentage: discountPercentage
            })
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Fehler beim Zuweisen des Discounts zu Sitztyp');
        }
        return data; // { message: 'Discount dem Sitztyp zugewiesen' }
    } catch (error) {
        console.error('Error assigning discount to seat type:', error);
        throw error;
    }
};


// Funktion zum Entfernen eines Discounts von einem Sitztyp
export const removeDiscountFromSeatType = async (token, seatTypeId, discountId) => {
    try {
        const response = await fetch(`${API_BASE_URL}/seat_type_discounts`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                seat_type_id: seatTypeId,
                discount_id: discountId
            })
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Fehler beim Entfernen des Discounts von Sitztyp');
        }
        return data; // { message: 'Discount vom Sitztyp entfernt' }
    } catch (error) {
        console.error('Error removing discount from seat type:', error);
        throw error;
    }
};


// Funktion zum Abrufen von Sitztypen mit ihren Discounts
export const fetchSeatTypesWithDiscounts = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/seat_types_with_discounts`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Fehler beim Abrufen der Sitztypen mit Discounts');
        }
        return data.seat_types; // Array von Sitztypen mit Discounts
    } catch (error) {
        console.error('Error fetching seat types with discounts:', error);
        throw error;
    }
};


// // Funktion zum Abrufen von Discounts für einen Sitztyp
// export const fetchDiscountsForSeatType = async (seatTypeId) => {
//     try {
//         const response = await fetch(`${API_BASE_URL}/seat_type_discounts?seat_type_id=${seatTypeId}`, {
//             method: 'GET',
//             headers: {
//                 'Content-Type': 'application/json',
//             }
//         });

//         const data = await response.json();
//         if (!response.ok) {
//             throw new Error(data.error || 'Fehler beim Abrufen der Discounts für Sitztyp');
//         }
//         return data.discounts; // Array von Discounts
//     } catch (error) {
//         console.error('Error fetching discounts for seat type:', error);
//         throw error;
//     }
// };


export async function deleteSeatType(token, seat_type_id) {
    const response = await fetch(`${API_BASE_URL}/seat_types/${seat_type_id}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
        },
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Fehler beim Löschen des Sitztyps');
    }

    return response.json();
}


export async function fetchMovieTrailerUrl(token, movie_id) {
    const response = await fetch(`${API_BASE_URL}/movie/${movie_id}/trailer_url`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`, // Falls benötigt
        },
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Fehler beim Abrufen der Trailer-URL');
    }

    const data = await response.json();
    return data.trailer_url;
}

export async function  fetchBookings(token) {
    const response = await fetch(`${API_BASE_URL}/bookings`, {
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`,
        },
    });
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'Fehler beim Laden der Buchungen.');
    }
    return data.bookings;
}


// Funktion zum Abrufen der aktuellen Punkte
export async function getUserPoints(token) {
    const response = await fetch(`${API_BASE_URL}/user/points`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    });
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'Fehler beim Laden der Punkte.');
    }
    return data.points;
}

// Funktion zum Einlösen von Punkten
export async function redeemPoints(token, points) {
    const response = await fetch(`${API_BASE_URL}/user/points/redeem`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ points })
    });
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'Fehler beim Einlösen von Punkten.');
    }
    return data;
}

// Funktion zum Abrufen der Punkte-Transaktionshistorie
export async function getPointsTransactions(token) {
    const response = await fetch(`${API_BASE_URL}/user/points/transactions`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    });
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'Fehler beim Laden der Punkte-Transaktionen.');
    }
    return data.transactions;
}

// Funktion zum Abrufen der Belohnungen
export async function fetchRewards(token) {
    const response = await fetch(`${API_BASE_URL}/rewards`, {
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`,
        },
    });
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'Fehler beim Laden der rewards.');
    }
    return data.rewards;
}

//Function to add rewards
export async function addReward(token, title, points, description, image) {
    const response = await fetch(`${API_BASE_URL}/rewards`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ title, points, description, image })
    });
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'Fehler beim Hinzufügen der Belohnung');
    }
    return data;
}

//Function to update rewards
export async function updateReward(token, reward_id, title, points, description, image) {
    const response = await fetch(`${API_BASE_URL}/rewards/${reward_id}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ title, points, description, image })
    });
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'Fehler beim Aktualisieren der Belohnung');
    }
    return data;
}

//Function to delete rewards
export async function deleteReward(token, reward_id) {
    const response = await fetch(`${API_BASE_URL}/rewards/${reward_id}`, {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`,
        },
    });
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'Fehler beim Löschen der Belohnung');
    }
    return data;
}

