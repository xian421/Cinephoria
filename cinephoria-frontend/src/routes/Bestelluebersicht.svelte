<script>
    import { onMount } from 'svelte';
    import { get } from 'svelte/store';
    import { authStore } from '../stores/authStore';
    import Swal from 'sweetalert2';
    import { fetchBookings } from '../services/api';
  
    

    let orders = [];
    let totalWatchtime = 0;
    let totalPoints = 0;
    let isLoading = true;
    let error = null;

    // Hover-Zustand für jedes Order-Item
    let hoveredOrder = null;

    // Funktionen zur Berechnung
    function calculateWatchtime() {
        return orders.reduce((sum, order) => sum + (order.runtime || 0), 0);
    }

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
                    runtime: order.start_time && order.end_time
                        ? Math.floor((new Date(order.end_time) - new Date(order.start_time)) / (1000 * 60))
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

    function handleMouseEnter(index) {
        hoveredOrder = index;
    }

    function handleMouseLeave() {
        hoveredOrder = null;
    }


   
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
        text-align: left;
        max-width: 1200px;
    }

    .summary-cards {
        display: flex;
        gap: 1rem;
        justify-content: space-between;
        margin-bottom: 2rem;
        flex-wrap: wrap;
        max-width: 800px;
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
        position: relative;
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

    .tooltip-info {
    position: absolute;
    left: 700px;
    top: 50%;
    transform: translateY(-50%);
    width: 300px;
    background: #f9f9f9;
    color: #333;
    padding: 0.75rem;
    border-radius: 8px;
  
    font-size: 0.9rem;
    text-align: left; /* Zentriert horizontal den Text */

    /* Flexbox für vertikale und horizontale Zentrierung */
    display: flex;
    justify-content: center; /* Horizontal zentrieren */
    align-items: center; /* Vertikal zentrieren */

    /* Scrollbar bei Bedarf */
    max-height: 110px;
}


.tooltip-info p {
    margin: 0.5rem 0; /* Abstand zwischen Zeilen */
}

.tooltip-info .info-group {
    display: flex;
    justify-content: space-between; /* Trennung von Titel und Inhalt */
    border-bottom: 1px solid #eaeaea; /* Dezente Trennlinie */
    padding-bottom: 0.3rem;
    margin-bottom: 0.3rem;
}

.tooltip-info .info-group:last-child {
    border-bottom: none; /* Keine Linie für das letzte Element */
}

/* Sicherstellen, dass Elterncontainer kein Scroll-Verhalten blockieren */
.order-item {
    position: relative; /* Wichtig für absolute Positionierung der Tooltip-Box */
    overflow: visible;
}

    .error-message, .loading {
        text-align: center;
        font-size: 1.2rem;
        margin-top: 3rem;
        color: #e74c3c;
    }
</style>

<main class="orders-container">

        <!-- Liste der Bestellungen -->
        <h2>Deine Bestellungen</h2>
        <div class="orders-list">
            {#each orders as order, index}
                <!-- svelte-ignore a11y_no_static_element_interactions -->
                <div
                    class="order-item"
                    on:mouseenter={() => handleMouseEnter(index)}
                    on:mouseleave={handleMouseLeave}
                >
                    <!-- Tooltip-Infos -->
                    {#if hoveredOrder === index}
                        <div class="tooltip-info">
                            
                            <ul class="seats-list">
                                <p>
                                    <strong>Sitz: </strong>
                                    {order.seats.map(seat => `${seat.row}${seat.number}`).join(', ')}
                                </p>
                               
                                <p><strong>Kinosaal: </strong> {order.screen_name}</p>
                                <p><strong>Start: </strong> Am {new Date(order.start_time).toLocaleDateString()} um {new Date(order.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}Uhr</p>



                            </ul>
                        </div>
                    {/if}
        
                    <div class="order-details">
                        <h4>{order.movie_title}</h4>
                        <p><strong>Datum:</strong> {new Date(order.date).toLocaleDateString()}</p>
                        <p><strong>Uhrzeit:</strong> {new Date(order.date).toLocaleTimeString()}</p>
                        <p><strong>Watchtime:</strong> {order.runtime} Min</p>
                    </div>
                    <p class="price">{order.total_amount.toFixed(2)} €</p>
                </div>
            {/each}
        </div>

</main>
 