<script lang="ts">
    import { onMount } from 'svelte';
    import { navigate } from 'svelte-routing';
    import QRCode from 'qrcode';
    import Swal from 'sweetalert2';
    import { tweened } from 'svelte/motion';
    import { cubicOut } from 'svelte/easing';
    import { fetchQRCodeData, fetchMovieDetails } from '../services/api';

    export let token: string;

    let bookingData: any = null;
    let qrCodeDataUrl: string | null = null;
    let qrError: string | null = null;

    let headerOpacity = tweened(0, { duration: 1000, easing: cubicOut });
    let taglineOpacity = tweened(0, { duration: 1500, easing: cubicOut, delay: 500 });

    let movies: Array<{
        movie_id: number;
        title: string;
        description: string;
        kinosaal: string;
        start_time: string;
        end_time: string;
        seats: Array<{
            nummer: string;
            reihe: string;
            type: string;
            type_icon?: string;
            farbe: string;
            discount_infos?: string;
        }>;
    }> = [];

    async function fetchBooking(token: string) {
        try {
            const data = await fetchQRCodeData(token);
            bookingData = data;
            console.log('Buchungsdaten:', bookingData);
            const moviesData = bookingData.movies;

            movies = await Promise.all(
                moviesData.map(async (movie: any) => {
                    try {
                        const movieDetails = await fetchMovieDetails(movie.movie_id);
                        return { ...movieDetails, ...movie };
                    } catch {
                        return { ...movie, title: 'Unbekannter Titel' };
                    }
                })
            );
        } catch (error) {
            console.error('Fehler:', error);
            throw error;
        }
    }

    async function generateQRCode(bookingData: any) {
        try {
            const qrContent = JSON.stringify(bookingData);
            qrCodeDataUrl = await QRCode.toDataURL(qrContent);
        } catch {
            qrError = 'QR-Code konnte nicht generiert werden.';
        }
    }

    onMount(async () => {
        if (token) {
            try {
                await fetchBooking(token);
                await generateQRCode(bookingData);
                headerOpacity.set(1);
                taglineOpacity.set(1);
            } catch {
                Swal.fire({ title: 'Fehler', text: 'Buchung nicht gefunden.', icon: 'error' }).then(() =>
                    navigate('/')
                );
            }
        }
    });
</script>

<div class="background">
    <header class="header-section">
        <h1 class="header-text" style:opacity={$headerOpacity}>Danke für Ihre Bestellung</h1>
        <p class="tagline" style:opacity={$taglineOpacity}>Ihre Tickets haben Sie per Mail bekommen!</p>
    </header>

    <main class="ticket-container">
        <h2>Ihre Bestätigung und Details sehen Sie hier:</h2>
        {#if bookingData}
            <div class="booking-details">
                <h2>Bestätigungsdetails</h2>
                <p class="total-price"><strong>Gesamtpreis:</strong> {bookingData.total_amount.toFixed(2)} €</p>

                <h3>Alle Filme:</h3>
                <ul class="movie-list">
                    {#each movies as movie}
                        <li class="movie-item">
                            <h3>{movie.title}</h3>
                            <p>Kinosaal: {movie.kinosaal}</p>
                            <p>
                                Startzeit: {new Date(movie.start_time).toLocaleDateString('de-DE', {
                                    day: '2-digit',
                                    month: '2-digit',
                                    year: 'numeric',
                                    hour: '2-digit',
                                    minute: '2-digit',
                                }).replace(',', ' Uhr')}
                            </p>

                            <h4>Sitzplätze:</h4>
                            <ul class="seat-list">
                                {#each movie.seats as seat}
                                    <li
                                        class="seat-item"
                                        style="background-color: {seat.farbe}"
                                        title={seat.type || ''}
                                    >
                                        {#if seat.type_icon}
                                            <i class="{seat.type_icon} seat-icon"></i>
                                        {/if}
                                        {seat.reihe}{seat.nummer}
                                        {#if seat.discount_infos}
                                            <br><small>{seat.discount_infos}</small>
                                        {/if}
                                    </li>
                                {/each}
                            </ul>
                        </li>
                    {/each}
                </ul>
            </div>
        {/if}

        {#if qrCodeDataUrl}
            <div class="qr-code-section">
                <h3>Ihr QR-Code:</h3>
                <img src="{qrCodeDataUrl}" alt="QR Code" class="qr-code">
                <p>Scannen Sie den QR-Code für Details.</p>
                <a href="{qrCodeDataUrl}" download="ticket_qrcode.png" class="download-link">QR-Code herunterladen</a>
            </div>
        {:else if qrError}
            <p class="error">{qrError}</p>
        {/if}

        <button on:click={() => navigate('/')} class="back-btn">Zurück zur Startseite</button>
    </main>
</div>


<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

    .background {
        min-height: 100vh;
        padding: 2rem;
        background: linear-gradient(135deg, #081229, #0b274a);
        color: #fff;
    }

    .header-section {
        text-align: center;
        margin: 4rem 0;
    }

    .header-text {
        font-size: 3rem;
        color: #2ecc71;
        text-shadow: 0 0 20px #2ecc71, 0 0 40px #2ecc71;
        animation: glow 2s infinite alternate;
    }

    .tagline {
        font-size: 1.5rem;
        color: #ddd;
    }

    .ticket-container {
        max-width: 1200px;
        margin: 2rem auto;
        padding: 2rem;
        background: rgba(26, 26, 26, 0.9);
        border-radius: 20px;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.7);
    }

    .booking-details h2,
    .booking-details h3 {
        color: #2ecc71;
        margin-bottom: 1rem;
    }

    .total-price {
        font-size: 1.2rem;
        color: #e8e8e8;
    }

    .movie-list {
        list-style: none;
        padding: 0;
    }

    .movie-item {
        background: rgba(0, 0, 0, 0.8);
        border: 1px solid #2ecc71;
        border-radius: 15px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 0 15px rgba(0, 0, 0, 0.5);
    }

    .seat-list {
        list-style: none;
        padding: 0;
    }

    .seat-item {
        background: rgba(0, 0, 0, 0.7);
        border-radius: 10px;
        padding: 0.5rem;
        margin-bottom: 0.5rem;
    }

    .qr-code-section {
        text-align: center;
        margin-top: 2rem;
    }

    .qr-code {
        border: 4px solid #2ecc71;
        border-radius: 10px;
        max-width: 200px;
        height: auto;
        margin: 1rem auto;
        display: block;
        box-shadow: 0 0 10px #2ecc71;
        transition: transform 0.3s;
    }

    .qr-code:hover {
        transform: scale(1.1);
    }

    .download-link {
        display: inline-block;
        margin-top: 1rem;
        padding: 0.7rem 1.2rem;
        background-color: #2ecc71;
        color: #000;
        text-decoration: none;
        border-radius: 10px;
        box-shadow: 0 0 10px #2ecc71;
        transition: background 0.3s ease, transform 0.3s;
    }

    .download-link:hover {
        background-color: #27ae60;
        transform: scale(1.05);
    }

    .back-btn {
        display: block;
        margin: 2rem auto;
        padding: 1rem 2rem;
        background: #2ecc71;
        color: #000;
        border: none;
        border-radius: 10px;
        box-shadow: 0 0 10px #2ecc71;
        cursor: pointer;
        transition: transform 0.3s ease;
    }

    .back-btn:hover {
        transform: scale(1.05);
    }

    .error {
        color: red;
        text-align: center;
        font-weight: bold;
    }

    @keyframes glow {
        from {
            text-shadow: 0 0 10px #2ecc71, 0 0 20px #2ecc71;
        }
        to {
            text-shadow: 0 0 20px #2ecc71, 0 0 40px #2ecc71;
        }
    }
</style>
