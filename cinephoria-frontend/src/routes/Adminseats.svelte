<!-- src/routes/Adminseats.svelte -->
<script>
    import { onMount } from "svelte";
    import { fetchSeats } from '../services/api.js';
    import { navigate } from "svelte-routing";
    import { get } from 'svelte/store';
    import { authStore } from '../stores/authStore.js';
    import Swal from 'sweetalert2';

    export let screenId; 

    let seats = [];
    let error = "";
    let loading = true;

    onMount(async () => {
    const auth = get(authStore);
    const token = auth.token;
    const isAdmin = auth.isAdmin;

    console.log('Adminseats mounted with screenId:', screenId);
    console.log('Token:', token);
    console.log('Is Admin:', isAdmin);

    try {
        const data = await fetchSeats(screenId, token);
        console.log('Fetched seats data:', data);

        if (data && data.seats) {
            seats = data.seats;
        } else {
            error = "Fehler beim Laden der Sitze.";
        }
    } catch (err) {
        console.error("Fehler beim Abrufen der Sitze:", err);
        error = err.message || "Ein Fehler ist aufgetreten. Bitte versuche es erneut.";
    } finally {
        loading = false;
    }
});
</script>

<main>
    {#if error}
        <p class="error">{error}</p>
    {:else if loading}
        <p>Lade Sitze...</p>
    {:else}
        <h1>Kinositze für Screen {screenId}</h1>
        <div class="seat-grid">
            {#each seats as seat}
                <div class="seat-card {seat.type}">
                    <p>Reihe: {seat.row}</p>
                    <p>Sitz: {seat.number}</p>
                    <p>Typ: {seat.type}</p>
                </div>
            {/each}
        </div>
    {/if}


    <button on:click={() => navigate('/adminkinosaal')}>Zurück zu Überblick der Kinosäle</button>
</main>






















<style>
    main {
        padding: 20px;
        font-family: Arial, sans-serif;
        text-align: center;
    }

    .seat-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
        gap: 20px;
        margin-top: 20px;
    }

    .seat-card {
        padding: 15px;
        border: 1px solid #ddd;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s, box-shadow 0.2s;
    }

    .seat-card:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 10px rgba(0, 0, 0, 0.15);
    }

    .seat-card.standard {
        background-color: #f0f8ff;
    }

    .seat-card.vip {
        background-color: #ffd700;
    }

    .seat-card.disabled {
        background-color: #d3d3d3;
        color: #888;
    }

    .error {
        color: red;
        font-weight: bold;
    }
</style>
