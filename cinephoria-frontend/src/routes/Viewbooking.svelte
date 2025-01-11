<!-- src/routes/ViewBooking.svelte -->
<script lang="ts">
    import { onMount } from 'svelte';
    import { navigate } from 'svelte-routing';
    import QRCode from 'qrcode';
    import Swal from 'sweetalert2';
    // import { fetchQRCodeData, verifyDiscount } from '../services/api'; // Nicht benötigt für das Beispiel

    export let token: string;

    // Beispiel-JSON-Daten
    let bookingData = {
        "booking_id": 123,
        "user_id": 456,
        "booking_time": "2025-01-09T14:30:00Z",
        "payment_status": "completed",
        "total_amount": 29.99,
        "created_at": "2025-01-09T14:30:00Z",
        "paypal_order_id": "PAYPAL123456789",
        "email": "max.mustermann@example.com",
        "nachname": "Mustermann",
        "vorname": "Max",
        "cinema_hall": "Kinosaal 1",
        "showtime": {
            "movie_title": "Harry Potter und der Stein der Weisen",
            "start_time": "2025-01-10T15:00:00Z",
            "end_time": "2025-01-10T16:00:00Z"
        },
        "seats": [
            {
                "seat_id": "A1",
                "showtime_id": 789,
                "seat_type_discount_id": 101
            },
            {
                "seat_id": "A2",
                "showtime_id": 789,
                "seat_type_discount_id": 102
            }
        ],
        "discounts": [
            {
                "id": 101,
                "type": "Student",
                "requires_verification": true,
                "verified": false
            },
            {
                "id": 102,
                "type": "Senior",
                "requires_verification": false,
                "verified": true
            }
        ]
    };

    let qrCodeDataUrl: string | null = null;
    let qrError: string | null = null;

    // Funktion zur Generierung des QR-Codes basierend auf dem Token
    async function generateQRCode(token: string) {
        try {
            const qrContent = `http://localhost:5173/view-booking/${token}`;
            qrCodeDataUrl = await QRCode.toDataURL(qrContent);
        } catch (error) {
            console.error('QR-Code Generierung fehlgeschlagen:', error);
            qrError = 'QR-Code konnte nicht generiert werden.';
            Swal.fire({
                title: 'Fehler',
                text: 'Der QR-Code konnte nicht generiert werden.',
                icon: 'error'
            });
        }
    }

    // Funktion zur Verifizierung des Discounts
    async function handleVerifyDiscount(discountId: number) {
        try {
            // Hier könntest du eine Funktion aufrufen, um den Rabatt zu verifizieren
            // Da wir kein Backend verwenden, simulieren wir dies:
            // Beispiel: Setze 'verified' auf true
            const discount = bookingData.discounts.find(d => d.id === discountId);
            if (discount) {
                discount.verified = true;
                Swal.fire({
                    title: 'Erfolg',
                    text: 'Rabatt erfolgreich verifiziert!',
                    icon: 'success'
                });
            }
        } catch (error) {
            console.error('Fehler bei der Rabatt-Verifizierung:', error);
            Swal.fire({
                title: 'Fehler',
                text: 'Rabatt konnte nicht verifiziert werden.',
                icon: 'error'
            });
        }
    }

    // Funktion zur Überprüfung des Showtime-Status
    function getShowtimeStatus(showtime) {
        const now = new Date();
        const start = new Date(showtime.start_time);
        const end = new Date(showtime.end_time);

        if (now < start && (start.getTime() - now.getTime()) <= 30 * 60 * 1000) {
            return { icon: '✔️', color: 'green', text: 'Vorstellung beginnt in weniger als 30 Minuten' };
        } else if (now >= start && now <= end) {
            return { icon: '⚠️', color: 'yellow', text: 'Vorstellung läuft' };
        } else if (now > end) {
            return { icon: '❗', color: 'red', text: 'Vorstellung ist beendet' };
        } else {
            return { icon: 'ℹ️', color: 'blue', text: 'Vorstellung ist geplant' };
        }
    }

    // Beim Mounten der Komponente den QR-Code generieren
    onMount(async () => {
        if (token) {
            try {
                await generateQRCode(token);
            } catch (error) {
                Swal.fire({
                    title: 'Fehler',
                    text: 'Ihre Buchung konnte nicht gefunden werden.',
                    icon: 'error'
                }).then(() => {
                    navigate('/');
                });
            }
        } else {
            console.log('Ungültiger QR-Code');
            Swal.fire({
                title: 'Fehler',
                text: 'Ungültiger QR-Code.',
                icon: 'error'
            }).then(() => {
                navigate('/');
            });
        }
    });
</script>

<main class="ticket-container">
    <h1>Danke für Ihre Bestellung</h1>
    <h2>Ihre Tickets haben Sie per Mail bekommen.</h2>

    {#if bookingData}
        <div class="booking-details">
            <h3>Buchungsdetails:</h3>
            <p><strong>Buchungs-ID:</strong> {bookingData.booking_id}</p>
            <p><strong>Name:</strong> {bookingData.vorname} {bookingData.nachname}</p>
            <p><strong>E-Mail:</strong> {bookingData.email}</p>
            <p><strong>Totalbetrag:</strong> {bookingData.total_amount.toFixed(2)} €</p>
            <p><strong>PayPal Order ID:</strong> {bookingData.paypal_order_id}</p>
            <p><strong>Kinosaal:</strong> {bookingData.cinema_hall}</p>
            <p><strong>Datum und Uhrzeit der Vorstellung:</strong> {new Date(bookingData.showtime.start_time).toLocaleString()}</p>
            
            {#if bookingData.showtime}
                <div class="showtime-status">
                    <strong>Status der Vorstellung:</strong>
                    <span class="status {getShowtimeStatus(bookingData.showtime).color}">
                        {getShowtimeStatus(bookingData.showtime).icon} {getShowtimeStatus(bookingData.showtime).text}
                    </span>
                </div>
            {/if}

            <h4>Sitzplätze:</h4>
            <ul>
                {#each bookingData.seats as seat}
                    <li>Sitz-ID: {seat.seat_id}, Showtime-ID: {seat.showtime_id}, Rabatt-ID: {seat.seat_type_discount_id}</li>
                {/each}
            </ul>

            {#if bookingData.discounts.length > 0}
                <h4>Rabatte:</h4>
                <ul>
                    {#each bookingData.discounts as discount}
                        <li>
                            {discount.type}
                            {#if discount.requires_verification}
                                {#if discount.verified}
                                    <span class="status success">✔️ Verifiziert</span>
                                {:else}
                                    <span class="status warning">⚠️ Verifizierung erforderlich</span>
                                    <button on:click={() => handleVerifyDiscount(discount.id)} class="verify-btn">Verifizieren</button>
                                {/if}
                            {/if}
                        </li>
                    {/each}
                </ul>
            {/if}
        </div>
    {/if}

    {#if qrCodeDataUrl}
        <div class="qr-code-section">
            <h3>Ihr Ticket QR-Code:</h3>
            <img src="{qrCodeDataUrl}" alt="QR Code" />
            <p>Scannen Sie den QR-Code, um diese Buchungsseite zu öffnen.</p>
            <a href="{qrCodeDataUrl}" download="ticket_qrcode.png" class="download-btn">QR-Code herunterladen</a>
        </div>
    {:else if qrError}
        <p class="error">{qrError}</p>
    {:else}
        <p>QR-Code wird generiert...</p>
    {/if}

    <button class="button" on:click={() => navigate('/')}>Zur Startseite</button>
</main>

<style>
    .ticket-container {
        text-align: center;
        padding: 2rem;
        background: #f9f9f9;
        border-radius: 10px;
        max-width: 800px;
        margin: 2rem auto;
        box-shadow: 0 0 15px rgba(0, 0, 0, 0.2);
    }

    h1 {
        color: #2ecc71;
        margin-bottom: 1rem;
    }

    h2 {
        color: #555;
        margin-bottom: 2rem;
    }

    .booking-details {
        margin: 2rem 0;
        padding: 1rem;
        background: rgba(0, 0, 0, 0.05);
        border: 1px solid #2ecc71;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        text-align: left;
    }

    .booking-details h3 {
        color: #2ecc71;
        margin-bottom: 1rem;
    }

    .booking-details p {
        color: #555;
        margin-bottom: 0.5rem;
    }

    .booking-details ul {
        list-style-type: none;
        padding: 0;
    }

    .booking-details li {
        background: rgba(0, 0, 0, 0.03);
        margin: 0.3rem 0;
        padding: 0.5rem;
        border-radius: 5px;
    }

    .showtime-status {
        margin-top: 1rem;
    }

    .status {
        margin-left: 0.5rem;
        font-weight: bold;
    }

    .status.green {
        color: green;
    }

    .status.red {
        color: red;
    }

    .status.yellow {
        color: orange;
    }

    .status.success {
        color: green;
    }

    .status.warning {
        color: orange;
    }

    .verify-btn {
        margin-left: 1rem;
        padding: 0.3rem 0.6rem;
        background-color: #f1c40f;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        color: #fff;
        transition: background-color 0.3s ease;
    }

    .verify-btn:hover {
        background-color: #d4ac0d;
    }

    .qr-code-section {
        margin: 2rem 0;
        padding: 1rem;
        background: rgba(0, 0, 0, 0.05);
        border: 1px solid #2ecc71;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    }

    .qr-code-section h3 {
        color: #2ecc71;
        margin-bottom: 1rem;
    }

    .qr-code-section img {
        max-width: 200px;
        height: auto;
        margin-bottom: 1rem;
    }

    .qr-code-section p {
        color: #555;
        margin-bottom: 1rem;
    }

    .download-btn {
        display: inline-block;
        margin-top: 1rem;
        padding: 0.5rem 1rem;
        background-color: #27ae60;
        color: #fff;
        text-decoration: none;
        border-radius: 5px;
        transition: background-color 0.3s ease;
    }

    .download-btn:hover {
        background-color: #1e8449;
    }

    .button {
        font-size: 1rem;
        font-weight: bold;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 1.2rem;
        cursor: pointer;
        transition: transform 0.3s ease;
        background-color: #2ecc71;
        color: #000;
        box-shadow: 0 0 10px #2ecc71;
        margin-top: 2rem;
    }

    .button:hover {
        transform: translateY(-3px) scale(1.05);
        opacity: 0.9;
    }

    .error {
        color: red;
        font-weight: bold;
    }
</style>
