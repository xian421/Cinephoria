<script>
    import { onMount } from 'svelte';
    import { get } from 'svelte/store';
    import { authStore } from '../stores/authStore';
    import Swal from 'sweetalert2';
    import { fetchBookings } from '../services/api';
    import { navigate } from 'svelte-routing';

    let orders = [];
    let totalWatchtime = 0;
    let totalPoints = 0;
    let isLoading = true;
    let error = null;

    // Berechnung der Watchtime inklusive Sitzanzahl
    function calculateWatchtime() {
        return orders.reduce((sum, order) => sum + (order.runtime || 0), 0);
    }

    // Beispiel-Punkteberechnung (Falls nötig anpassen!)
    function calculatePoints() {
        return orders.reduce((sum, order) => sum + Math.floor((order.total_amount || 0) / 1), 0);
    }

    onMount(async () => {
        const token = get(authStore).token;
        if (!token) {
            error = 'Nicht authentifiziert';
            isLoading = false;
            await Swal.fire({ title: "Fehler", text: error, icon: "error" });
            return;
        }

        try {
            const data = await fetchBookings(token);

            if (Array.isArray(data)) {
                orders = data.map(order => ({
                    ...order,
                    // Laufzeit in Minuten (end_time - start_time) 
                    // multipliziert mit der Anzahl Sitze (order.seats.length)
                    runtime: order.start_time && order.end_time
                        ? Math.floor(
                            (new Date(order.end_time) - new Date(order.start_time)) 
                            / (1000 * 60)
                          ) * (order.seats?.length ?? 1)
                        : 0,
                    date: order.created_at,
                    seat: order.seat || 'Keine Angaben',
                    screen: order.screen || 'Unbekannt'
                }));
            } else {
                throw new Error('Unerwartetes Antwortformat');
            }

            totalWatchtime = calculateWatchtime();
            totalPoints = calculatePoints();
        } catch (err) {
            console.error('Fehler beim Laden der Bestellungen:', err);
            error = err.message || 'Fehler beim Laden der Bestellungen';
            await Swal.fire({ title: "Fehler", text: error, icon: "error" });
        } finally {
            isLoading = false;
        }
    });
</script>

<style>
    body {
        margin: 0;
        font-family: 'Roboto', sans-serif;
        background: linear-gradient(135deg, #000428, #004e92);
        color: #fff;
        overflow-x: hidden;
        max-width: 100%;
    }

    main.orders-container {
        max-width: 1200px;
        margin: 2rem auto;
        padding: 2rem;
        position: relative;
        display: flex;
        flex-direction: column;
        gap: 3rem;
        margin-top: 4rem;
    }

    h1 {
        font-size: 3rem;
        color: #2ecc71;
        text-shadow: 0 0 20px #2ecc71, 0 0 40px #2ecc71;
        text-align: center;
        animation: glow 2s infinite alternate;
        margin: 0;
    }

    @keyframes glow {
      from {
        text-shadow: 0 0 10px #2ecc71, 0 0 20px #2ecc71;
      }
      to {
        text-shadow: 0 0 20px #2ecc71, 0 0 40px #2ecc71;
      }
    }

    .summary-cards {
        display: flex;
        gap: 1rem;
        justify-content: center;
        flex-wrap: wrap;
    }

    .card {
        flex: 1;
        min-width: 250px;
        background: rgba(0,0,0,0.4);
        border-radius: 12px;
        box-shadow: 0 0 20px rgba(0,0,0,0.5);
        padding: 1.5rem;
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        cursor: pointer;
    }

    .card:hover {
        transform: translateY(-10px);
        box-shadow: 0 0 25px #2ecc71;
    }

    .card h3 {
        font-size: 2rem;
        margin: 0;
        color: #2ecc71;
        text-shadow: 0 0 10px #2ecc71;
    }

    .card p {
        font-size: 1rem;
        color: #ddd;
        margin-top: 0.5rem;
    }

    /* Fehlermeldungen oder Ladezustände */
    .error-message, .loading {
        text-align: center;
        font-size: 1.2rem;
        margin-top: 3rem;
        color: #e74c3c;
        text-shadow: 0 0 5px #e74c3c;
    }
</style>

<main class="orders-container">
    {#if isLoading}
        <p class="loading">Bestellungen werden geladen...</p>
    {:else if error}
        <p class="error-message">{error}</p>
    {:else if orders.length === 0}
        <p class="error-message">Keine Bestellungen gefunden.</p>
    {:else}
        <!-- Zusammenfassende Karten -->
        <h1>Deine Statistiken</h1>
        <div class="summary-cards">
            <div class="card" on:click={() => navigate('/leaderboard')}>
                <h3>{totalWatchtime} Min</h3>
                <p>Gesamte Watchtime</p>
            </div>
            <div class="card" on:click={() => navigate('/belohnung')}>
                <h3>{totalPoints}</h3>
                <p>Gesammelte Punkte</p>
            </div>
            <div class="card" on:click={() => navigate('/bestelluebersicht')}>
                <h3>{orders.length}</h3>
                <p>Gesamte Bestellungen</p>
            </div>
        </div>
    {/if}
</main>
