<script lang="ts">
    import { navigate } from 'svelte-routing';
    import Swal from 'sweetalert2';
    import { fetchEmployeeQRCodeData, fetchMovieDetails } from '../services/api';
    import { onMount, onDestroy } from 'svelte';
    import QrScanner from 'qr-scanner'; // Importiere qr-scanner

    // TypeScript Schnittstellen
    interface Seat {
        nummer: string;
        reihe: string;
        type: string;
        type_icon?: string;
        farbe: string;
        discount_infos?: string;
    }

    interface Movie {
        movie_id: number;
        title: string;
        description: string;
        kinosaal: string;
        start_time: string;
        end_time: string;
        seats: Seat[];
    }

    interface BookingData {
        movies: Movie[];
        // Weitere Felder nach Bedarf
    }

    let qrToken: string = '';
    let bookingData: BookingData | null = null;
    let qrError: string | null = null;
    let isLoading: boolean = false;

    // Status: 'green', 'yellow', 'red' oder null
    let status: 'green' | 'yellow' | 'red' | null = null;

    // Dark Mode
    let darkMode: boolean = false;

    // Referenz für das Videoelement (für QR-Scanner)
    let videoElement: HTMLVideoElement;

    // Scanner-Instanz
    let qrScannerInstance: QrScanner | null = null;

    // State zur Steuerung des Scannens
    let isScanning: boolean = true;

    // Funktion zum Abrufen der Buchungsdetails
    async function fetchBookingDetails(token: string) {
        try {
            const data = await fetchEmployeeQRCodeData(token);
            bookingData = data;
            console.log('Buchungsdaten:', bookingData);
            const moviesData = bookingData.movies;

            const moviesWithDetails = await Promise.all(
                moviesData.map(async (movie: Movie) => {
                    try {
                        const movieDetails = await fetchMovieDetails(movie.movie_id);
                        return { ...movieDetails, ...movie };
                    } catch (error) {
                        console.error(`Fehler beim Abrufen der Details für Film ID ${movie.movie_id}:`, error);
                        return { ...movie, title: 'Unbekannter Titel', description: 'Keine Beschreibung verfügbar.' };
                    }
                })
            );

            bookingData.movies = moviesWithDetails;
            determineStatus();
        } catch (error: any) {
            console.error('Fehler beim Abrufen der Buchungsdetails:', error);
            qrError = error.message || 'Ein unbekannter Fehler ist aufgetreten.';
            status = 'red';
        }
    }

    // Funktion zur Bestimmung des Status basierend auf den Buchungsdetails
    function determineStatus() {
        if (!bookingData || bookingData.movies.length === 0) {
            status = 'red';
            return;
        }

        // Prüfe, ob irgendeine Buchung einen Rabatt enthält
        const hasDiscount = bookingData.movies.some(movie => 
            movie.seats.some(seat => seat.discount_infos)
        );

        if (hasDiscount) {
            status = 'yellow';
        } else {
            status = 'green';
        }
    }

    // Handle Submit Funktion zum Scannen des QR-Codes
    async function handleSubmit() {
        if (typeof qrToken !== 'string' || !qrToken.trim()) {
            Swal.fire({
                title: 'Fehler',
                text: 'Bitte geben Sie einen gültigen QR-Code Token ein.',
                icon: 'error',
                timer: 1500,
                showConfirmButton: false
            });
            return;
        }

        qrError = null;
        bookingData = null;
        status = null;
        isLoading = true;

        try {
            await fetchBookingDetails(qrToken.trim());

            if (status === 'green') {
                await Swal.fire({
                    icon: 'success',
                    title: 'Erfolgreich',
                    text: 'Buchung ist gültig.',
                    timer: 1500,
                    showConfirmButton: false
                });
            } else if (status === 'yellow') {
                await Swal.fire({
                    icon: 'warning',
                    title: 'Rabatt angewendet',
                    text: 'Diese Buchung enthält einen Rabatt.',
                    timer: 1500,
                    showConfirmButton: false
                });
            } else {
                await Swal.fire({
                    icon: 'error',
                    title: 'Ungültige Buchung',
                    text: 'QR-Code nicht gefunden oder ungültig.',
                    timer: 1500,
                    showConfirmButton: false
                });
            }
        } catch {
            // Fehlerfall: Status bereits auf 'red' gesetzt
            await Swal.fire({
                icon: 'error',
                title: 'Ungültige Buchung',
                text: 'QR-Code nicht gefunden oder ungültig.',
                timer: 1500,
                showConfirmButton: false
            });
        } finally {
            isLoading = false;
        }
    }

    // QR-Code-Scanner mit Kamera
    function initializeQrScanner() {
        if (videoElement && isScanning) {
            qrScannerInstance = new QrScanner(videoElement, result => {
                console.log('QR Scan Result:', result); // Debugging

                // Sicherstellen, dass qrToken immer ein String ist
                if (typeof result === 'string') {
                    qrToken = result;
                } else if (typeof result === 'object' && result.data) {
                    qrToken = result.data.toString();
                } else {
                    qrToken = JSON.stringify(result);
                }

                console.log('QR Token:', qrToken); // Debugging

                qrScannerInstance?.stop();
                qrScannerInstance = null;
                isScanning = false;
                handleSubmit();
            }, {
                onDecodeError: error => {
                    console.warn('QR Decode Error:', error);
                },
                highlightScanRegion: true,
                highlightCodeOutline: true
            });
            qrScannerInstance.start().catch(error => {
                console.error('Kamera-Fehler:', error);
                Swal.fire({
                    title: 'Kamera-Fehler',
                    text: 'Kamera konnte nicht gestartet werden. Bitte überprüfen Sie die Berechtigungen und versuchen Sie es erneut.',
                    icon: 'error',
                    timer: 3000,
                    showConfirmButton: false
                });
            });
        }
    }

    // Funktion zum Neustarten des Scanners
    function startNewScan() {
        qrToken = '';
        bookingData = null;
        qrError = null;
        status = null;
        isScanning = true;
        initializeQrScanner();
    }

    // Beim Mounten initialisieren
    onMount(() => {
        initializeQrScanner();
    });

    // Beim Zerstören den Scanner stoppen
    onDestroy(() => {
        qrScannerInstance?.stop();
    });
</script>

<div class="background {darkMode ? 'dark-mode' : ''}">
    <header class="header-section">
        <h1 class="header-text">Mitarbeiter-QR-Code-Scanner</h1>
        <p class="tagline">Scannen Sie den QR-Code, um die Buchungsdetails anzuzeigen.</p>
        <button on:click={() => darkMode = !darkMode} class="toggle-dark-btn">
            {#if darkMode}
                🌙 Dunkelmodus
            {:else}
                ☀️ Hellmodus
            {/if}
        </button>
    </header>

    <main class="scanner-container">
        <form on:submit|preventDefault={handleSubmit} class="scanner-form">
            <!-- Aktiviertes Video-Element für QR-Scanner -->
            <video bind:this={videoElement} class="qr-video" aria-label="QR-Code Kamera-Stream"></video>

            <input
                type="text"
                bind:value={qrToken}
                placeholder="QR-Code Token eingeben"
                class="qr-input"
                aria-label="QR-Code Token"
            />
            <button type="submit" class="submit-btn" disabled={isLoading}>
                {#if isLoading}
                    <span class="spinner"></span> Scannen...
                {:else}
                    Scannen
                {/if}
            </button>
        </form>

        {#if isLoading}
            <div class="progress-bar">
                <div class="progress"></div>
            </div>
            <div class="loading">Daten werden geladen...</div>
        {/if}

        {#if bookingData && !isLoading}
            <div class="booking-details">
                <div class="status-indicator {status}">
                    {#if status === 'green'}
                        ✅ Gültige Buchung
                    {:else if status === 'yellow'}
                        ⚠️ Buchung mit Rabatt
                    {:else}
                        ❌ Ungültige Buchung
                    {/if}
                </div>
                <h2>Ticket Informationen</h2>
                {#each bookingData.movies as movie}
                    <div class="movie-card">
                        <h3>{movie.title}</h3>
                        <p><strong>Datum & Uhrzeit:</strong> {new Date(movie.start_time).toLocaleDateString('de-DE', {
                            day: '2-digit',
                            month: '2-digit',
                            year: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit',
                        }).replace(',', ' um ')} Uhr</p>
                        <p><strong>Kinosaal:</strong> {movie.kinosaal}</p>
                        {#if movie.description}
                            <p><strong>Beschreibung:</strong> {movie.description}</p>
                        {/if}

                        <h4>Sitzplätze:</h4>
                        <ul class="seat-list">
                            {#each movie.seats as seat}
                                <li
                                    class="seat-item"
                                    style="background-color: {seat.farbe};"
                                    title={seat.type || ''}
                                >
                                    {#if seat.type_icon}
                                        <i class={`fas ${seat.type_icon} seat-icon`} aria-hidden="true"></i>
                                    {/if}
                                    <span>{seat.reihe}{seat.nummer}</span>
                                    {#if seat.discount_infos}
                                        <br><small>{seat.discount_infos}</small>
                                    {/if}
                                </li>
                            {/each}
                        </ul>
                    </div>
                {/each}
            </div>
        {:else if qrError && !isLoading}
            <div class="error">{qrError}</div>
        {/if}

        {#if !isScanning && !isLoading}
            <button on:click={startNewScan} class="new-scan-btn">Neuer Scan</button>
        {/if}

        <button on:click={() => navigate('/mitarbeiter')} class="back-btn">Zurück zur Startseite</button>
    </main>
</div>

<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

    /* Grundlegendes Layout */
    .background {
        min-height: 100vh;
        padding: 2rem;
        background-color: #ffffff; /* Weißer Hintergrund */
        color: #333333; /* Dunkelgraue Schriftfarbe für guten Kontrast */
        font-family: 'Roboto', sans-serif;
        display: flex;
        flex-direction: column;
        align-items: center;
        transition: background-color 0.3s, color 0.3s;
    }

    .dark-mode {
        background-color: #121212; /* Dunkler Hintergrund */
        color: #f1f1f1; /* Helle Schriftfarbe */
    }

    /* Header-Stile */
    .header-section {
        text-align: center;
        margin-bottom: 2rem;
        width: 100%;
        max-width: 600px;
    }

    .header-text {
        font-size: 2rem;
        color: inherit;
        margin-bottom: 0.5rem;
    }

    .tagline {
        font-size: 1rem;
        color: inherit;
    }

    .toggle-dark-btn {
        margin-top: 1rem;
        padding: 0.8rem 2rem;
        background: none;
        border: 2px solid currentColor;
        border-radius: 5px;
        cursor: pointer;
        font-size: 1rem;
        transition: background-color 0.3s, color 0.3s;
    }

    .toggle-dark-btn:hover {
        background-color: rgba(0, 0, 0, 0.1);
    }

    /* Scanner-Container */
    .scanner-container {
        width: 100%;
        max-width: 500px;
        padding: 2rem;
        background: #f9f9f9;
        border: 1px solid #dddddd;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        transition: background-color 0.3s, border-color 0.3s;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .dark-mode .scanner-container {
        background: #1e1e1e;
        border-color: #444444;
    }

    /* Scanner-Formular */
    .scanner-form {
        display: flex;
        flex-direction: column;
        align-items: stretch;
        width: 100%;
    }

    .qr-video {
        width: 100%;
        max-width: 400px;
        height: auto;
        border: 2px solid #2ecc71;
        border-radius: 5px;
        margin-bottom: 1rem;
    }

    .qr-input {
        width: 100%;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid #cccccc;
        border-radius: 5px;
        font-size: 1.2rem;
        outline: none;
        transition: border-color 0.3s;
    }

    .dark-mode .qr-input {
        background-color: #333333;
        color: #f1f1f1;
        border-color: #555555;
    }

    .qr-input:focus {
        border-color: #2ecc71;
    }

    .submit-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1rem;
        background-color: #2ecc71;
        color: #ffffff;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-size: 1.2rem;
        transition: background-color 0.3s, transform 0.3s;
    }

    .submit-btn:disabled {
        background-color: #95a5a6;
        cursor: not-allowed;
    }

    .submit-btn:hover:not(:disabled) {
        background-color: #27ae60;
        transform: scale(1.02);
    }

    /* Spinner */
    .spinner {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #ffffff;
        border-radius: 50%;
        width: 24px;
        height: 24px;
        animation: spin 1s linear infinite;
        margin-right: 0.5rem;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* Ladeindikator */
    .loading {
        text-align: center;
        font-size: 1.2rem;
        color: #666666;
        margin-top: 1rem;
    }

    .dark-mode .loading {
        color: #cccccc;
    }

    /* Fortschrittsanzeige */
    .progress-bar {
        width: 100%;
        background-color: #f3f3f3;
        border-radius: 5px;
        overflow: hidden;
        margin-top: 1rem;
    }

    .dark-mode .progress-bar {
        background-color: #444444;
    }

    .progress {
        width: 70%; /* Dynamisch anpassen */
        height: 12px;
        background-color: #2ecc71;
        animation: loading 2s infinite;
    }

    @keyframes loading {
        0% { width: 0%; }
        50% { width: 70%; }
        100% { width: 0%; }
    }

    /* Buchungsdetails */
    .booking-details {
        margin-top: 1.5rem;
        width: 100%;
    }

    .booking-details h2 {
        font-size: 1.8rem;
        margin-bottom: 1rem;
        color: inherit;
        text-align: center;
    }

    .movie-card {
        background: #ffffff;
        border: 1px solid #eeeeee;
        border-radius: 5px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        transition: background-color 0.3s, border-color 0.3s;
    }

    .dark-mode .movie-card {
        background: #2c2c2c;
        border-color: #555555;
    }

    .movie-card h3 {
        font-size: 1.5rem;
        color: #2ecc71;
        margin-bottom: 0.8rem;
    }

    .movie-card p {
        margin: 0.5rem 0;
        color: #555555;
        line-height: 1.6;
        font-size: 1rem;
    }

    .dark-mode .movie-card p {
        color: #dddddd;
    }

    .movie-card h4 {
        margin-top: 1rem;
        font-size: 1.1rem;
        color: #333333;
    }

    .dark-mode .movie-card h4 {
        color: #f1f1f1;
    }

    .seat-list {
        list-style: none;
        padding: 0;
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 0.5rem;
    }

    .seat-item {
        display: flex;
        align-items: center;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        color: #ffffff;
        font-size: 1rem;
        position: relative;
        min-width: 60px;
        justify-content: center;
        transition: transform 0.2s;
    }

    .seat-item:hover {
        transform: scale(1.05);
    }

    .seat-icon {
        margin-right: 0.3rem;
    }

    /* Status-Indikator */
    .status-indicator {
        padding: 0.8rem;
        border-radius: 5px;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
        color: #ffffff;
        font-size: 1.2rem;
    }

    .status-indicator.green {
        background-color: #2ecc71;
    }

    .status-indicator.yellow {
        background-color: #f1c40f;
    }

    .status-indicator.red {
        background-color: #e74c3c;
    }

    /* Fehlernachricht */
    .error {
        color: #dc3545;
        text-align: center;
        font-weight: bold;
        margin-top: 1rem;
        font-size: 1.2rem;
    }

    /* Zurück-Button */
    .back-btn {
        display: block;
        margin: 1.5rem auto 0;
        padding: 1rem 2rem;
        background: #dddddd;
        color: #333333;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-size: 1.2rem;
        transition: background-color 0.3s, transform 0.3s;
        width: 100%;
        max-width: 250px;
    }

    .dark-mode .back-btn {
        background: #555555;
        color: #f1f1f1;
    }

    .back-btn:hover {
        background-color: #cccccc;
        transform: scale(1.02);
    }

    .dark-mode .back-btn:hover {
        background-color: #666666;
    }

    /* Neuer Scan-Button */
    .new-scan-btn {
        display: block;
        margin: 1rem auto 0;
        padding: 1rem 2rem;
        background: #2ecc71;
        color: #ffffff;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-size: 1.2rem;
        transition: background-color 0.3s, transform 0.3s;
        width: 100%;
        max-width: 250px;
    }

    .new-scan-btn:hover {
        background-color: #27ae60;
        transform: scale(1.02);
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .header-text {
            font-size: 2.5rem;
        }

        .tagline {
            font-size: 1.2rem;
        }

        .toggle-dark-btn {
            padding: 0.8rem 2rem;
            font-size: 1.2rem;
        }

        .scanner-container {
            padding: 1.5rem;
        }

        .qr-video {
            max-width: 100%;
            height: auto;
        }

        .qr-input {
            padding: 1.2rem;
            font-size: 1.4rem;
        }

        .submit-btn {
            padding: 1.2rem;
            font-size: 1.4rem;
        }

        .spinner {
            width: 24px;
            height: 24px;
        }

        .loading {
            font-size: 1.4rem;
        }

        .progress {
            height: 14px;
        }

        .booking-details h2 {
            font-size: 2rem;
        }

        .movie-card {
            padding: 2rem;
        }

        .movie-card h3 {
            font-size: 1.8rem;
        }

        .movie-card p {
            font-size: 1.2rem;
        }

        .movie-card h4 {
            font-size: 1.3rem;
        }

        .seat-item {
            min-width: 70px;
            padding: 0.6rem 1.2rem;
            font-size: 1.1rem;
        }

        .status-indicator {
            font-size: 1.4rem;
        }

        .error {
            font-size: 1.4rem;
        }

        .back-btn,
        .new-scan-btn {
            padding: 1.2rem 2.5rem;
            font-size: 1.4rem;
            max-width: 300px;
        }
    }

    @media (max-width: 480px) {
        .header-text {
            font-size: 2rem;
        }

        .tagline {
            font-size: 1rem;
        }

        .toggle-dark-btn {
            padding: 0.6rem 1.5rem;
            font-size: 1rem;
        }

        .scanner-container {
            padding: 1rem;
        }

        .qr-input {
            padding: 1rem;
            font-size: 1.2rem;
        }

        .submit-btn {
            padding: 1rem;
            font-size: 1.2rem;
        }

        .loading {
            font-size: 1.2rem;
        }

        .booking-details h2 {
            font-size: 1.6rem;
        }

        .movie-card {
            padding: 1.5rem;
        }

        .movie-card h3 {
            font-size: 1.5rem;
        }

        .movie-card p {
            font-size: 1rem;
        }

        .movie-card h4 {
            font-size: 1.1rem;
        }

        .seat-item {
            min-width: 60px;
            padding: 0.5rem 1rem;
            font-size: 1rem;
        }

        .status-indicator {
            font-size: 1.2rem;
        }

        .error {
            font-size: 1.2rem;
        }

        .back-btn,
        .new-scan-btn {
            padding: 1rem 2rem;
            font-size: 1.2rem;
            max-width: 100%;
        }
    }
</style>
