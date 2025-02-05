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
        console.log(data);

        if (Array.isArray(data)) {
            // Filtere Duplikate basierend auf booking_id
            const uniqueData = data.filter((order, index, self) =>
                index === self.findIndex(o => o.booking_id === order.booking_id)
            );

            orders = uniqueData.map(order => ({
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
    margin: 4rem auto;
    padding: 2rem;
    position: relative;
    display: flex;
    flex-direction: column;
    gap: 3rem;
    text-align: left;
}

h2 {
    font-size: 2.5rem;
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

.orders-list {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.order-item {
    background: rgba(0,0,0,0.4);
    border-radius: 12px;
    box-shadow: 0 0 20px rgba(0,0,0,0.5);
    padding: 1rem;
    display: flex;
    position: relative;
    justify-content: space-between;
    align-items: center;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    cursor: pointer;
}

.order-item:hover {
    transform: translateY(-5px);
    box-shadow: 0 0 25px #2ecc71;
}

.order-details h4 {
    margin: 0;
    font-size: 1.5rem;
    color: #2ecc71;
    text-shadow: 0 0 5px #2ecc71;
}

.order-details p {
    margin: 0.3rem 0;
    color: #ddd;
    font-size: 1rem;
    text-shadow: 0 0 2px #fff;
}

.price {
    font-weight: bold;
    font-size: 1.2rem;
    color: #fff;
    background: #2ecc71;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    text-shadow: 0 0 5px #fff;
}

/* Tooltip */
.tooltip-info {
    position: absolute;
    top: 50%;
    left: 105%;
    transform: translateY(-50%);
    width: 280px;
    background: rgba(0,0,0,0.7);
    color: #fff;
    padding: 1rem;
    border-radius: 12px;
    box-shadow: 0 0 20px #2ecc71;
    font-size: 0.9rem;
    text-align: left;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    animation: fadeIn 0.3s ease forwards;
    z-index: 10;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-50%) scale(0.95); }
  to { opacity: 1; transform: translateY(-50%) scale(1); }
}

.tooltip-info h5 {
    margin: 0;
    font-size: 1.2rem;
    color: #2ecc71;
    text-shadow: 0 0 5px #2ecc71;
    border-bottom: 1px solid #2ecc71;
    padding-bottom: 0.3rem;
}

.tooltip-info p {
    margin: 0.3rem 0;
    color: #ddd;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Kleine Icons für Sitze und Saal */
.tooltip-info .info-icon {
    color: #f1c40f;
    text-shadow: 0 0 5px #f1c40f;
}

/* Fehler- und Lade-Anzeige */
.error-message, .loading {
    text-align: center;
    font-size: 1.2rem;
    margin-top: 3rem;
    color: #e74c3c;
    text-shadow: 0 0 5px #e74c3c;
}

/* Responsives Verhalten */
@media (max-width: 600px) {
    .tooltip-info {
        left: 50%;
        top: 110%;
        transform: translate(-50%, 0);
        width: 90%;
    }

    .order-details h4 {
        font-size: 1.2rem;
    }
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
 