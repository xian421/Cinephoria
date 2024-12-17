<!-- src/routes/orders.svelte -->
<script>
    import { onMount } from 'svelte';
    import { get } from 'svelte/store';
    import { authStore } from '../stores/authStore';
    import Swal from 'sweetalert2';

    let orders = [];
    let totalWatchtime = 0;
    let totalPoints = 0;
    let isLoading = true;
    let error = null;

    // Funktionen zur Berechnung
    function calculateWatchtime() {
        return orders.reduce((sum, order) => sum + (order.runtime || 0), 0); // Laufzeiten summieren
    }

    function calculatePoints() {
        return orders.reduce((sum, order) => sum + Math.floor((order.total_price || 0) / 10), 0); // 1 Punkt pro 10€
    }

    onMount(async () => {
        const token = get(authStore).token;
        if (!token) {
            error = 'Nicht authentifiziert';
            isLoading = false;
            return Swal.fire({ title: "Fehler", text: error, icon: "error" });
        }

        try {
        
            
            totalWatchtime = calculateWatchtime();
            totalPoints = calculatePoints();
        } catch (err) {
            console.error('Fehler beim Laden der Bestellungen:', err);
            error = err.message || 'Fehler beim Laden der Bestellungen';
        } finally {
            isLoading = false;
        }
    });
</script>

<style>
    .orders-container {
        max-width: 900px;
        margin: 2rem auto;
        padding: 2rem;
        background: #fdfdfd;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        font-family: 'Roboto', sans-serif;
    }

    .summary-cards {
        display: flex;
        gap: 1rem;
        justify-content: space-between;
        margin-bottom: 2rem;
        flex-wrap: wrap;
    }

    .card {
        flex: 1;
        min-width: 250px;
        background: #ffffff;
        border-radius: 12px;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
        padding: 1.5rem;
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .card:hover {
        transform: translateY(-10px);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
    }

    .card h3 {
        font-size: 1.5rem;
        margin: 0;
        color: #3498db;
    }

    .card p {
        font-size: 1rem;
        color: #555;
    }

    .orders-list {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .order-item {
        background: #f9f9f9;
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        padding: 1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: transform 0.3s;
    }

    .order-item:hover {
        transform: translateY(-5px);
    }

    .order-details {
        flex-grow: 1;
    }

    .order-details h4 {
        margin: 0;
        font-size: 1.2rem;
        color: #34495e;
    }

    .order-details p {
        margin: 0.3rem 0;
        color: #777;
    }

    .price {
        font-weight: bold;
        color: #2ecc71;
    }

    .error-message, .loading {
        text-align: center;
        font-size: 1.2rem;
        margin-top: 3rem;
        color: #e74c3c;
    }
</style>

<main class="orders-container">
    {#if isLoading}
        <p class="loading">Bestellungen werden geladen...</p>
    {:else if error}
        <p class="error-message">{error}</p>
    {:else}
        <!-- Zusammenfassende Karten -->
        <div class="summary-cards">
            <div class="card">
                <h3>{totalWatchtime} Min</h3>
                <p>Gesamte Watchtime</p>
            </div>
            <div class="card">
                <h3>{totalPoints}</h3>
                <p>Gesammelte Punkte</p>
            </div>
            <div class="card">
                <h3>{orders.length}</h3>
                <p>Gesamte Bestellungen</p>
            </div>
        </div>

        <!-- Liste der Bestellungen -->
        <h2>Deine Bestellungen</h2>
        <div class="orders-list">
            {#each orders as order}
                <div class="order-item">
                    <div class="order-details">
                        <h4>{order.movie_title}</h4>
                        <p><strong>Datum:</strong> {new Date(order.date).toLocaleDateString()}</p>
                        <p><strong>Uhrzeit:</strong> {new Date(order.date).toLocaleTimeString()}</p>
                        <p><strong>Watchtime:</strong> {order.runtime} Min</p>
                    </div>
                    <p class="price">{order.total_price.toFixed(2)} €</p>
                </div>
            {/each}
        </div>
    {/if}
</main>
