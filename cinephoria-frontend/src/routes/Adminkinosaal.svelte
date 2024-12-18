<!-- src/routes/Adminkinosaal.svelte -->
<script>
    import { onMount } from "svelte";
    import { Link } from "svelte-routing";
    import { fetchScreens } from '../services/api.js'; // Importiere die fetchScreens Funktion aus api.js
    import Swal from 'sweetalert2';
    import { authStore } from '../stores/authStore.js';
    import { get } from 'svelte/store';

    let screens = [];

    onMount(async () => {
        const auth = get(authStore);
        const token = auth.token;

        if (!token) {
            Swal.fire({
                title: "Token fehlt",
                text: "Bitte loggen Sie sich ein.",
                icon: "error",
                confirmButtonText: "OK",
            });
            navigate('/login'); // Oder den entsprechenden Login-Pfad
            return;
        }

        try {
            const data = await fetchScreens(token);
            if (data.screens) {
                screens = data.screens;
                console.log('Screens data:', screens);
            } else {
                console.error("Fehler beim Laden der Kinosäle:", data.error);
                Swal.fire({
                    title: "Fehler",
                    text: data.error || "Fehler beim Laden der Kinosäle.",
                    icon: "error",
                    confirmButtonText: "OK",
                });
                navigate('/unauthorized'); // Oder einen anderen geeigneten Pfad
            }
        } catch (error) {
            console.error("Fehler beim Laden der Kinosäle:", error);
            Swal.fire({
                title: "Fehler",
                text: "Ein Fehler ist aufgetreten. Bitte versuche es erneut.",
                icon: "error",
                confirmButtonText: "OK",
            });
            navigate('/unauthorized'); // Oder einen anderen geeigneten Pfad
        }
    });
</script>

<div class="admin-page">
    {#if screens.length > 0}
        {#each screens as screen}
            <Link to={`/adminseats/${screen.screen_id}`}>
                <div class="card">
                    <div class="image-container">
                        <img src="/cinema-hall.webp" alt="Kinosaal" />
                        <h3 class="card-name">{screen.name}</h3>
                    </div>
                    <div class="card-overlay">
                        <div class="card-info">
                            <p>Kapazität: {screen.capacity}</p>
                            <p>Typ: {screen.type || "Standard"}</p>
                            <p>Erstellt: {new Date(screen.created_at).toLocaleDateString()}</p>
                        </div>
                    </div>
                </div>
            </Link>
        {/each}
    {:else}
        <p>Keine Kinosäle gefunden.</p>
    {/if}
</div>

<style>
body {
    margin: 0;
    font-family: 'Roboto', sans-serif;
    background: linear-gradient(135deg, #000428, #004e92);
    color: #fff;
    overflow-x: hidden;
    max-width: 100%;
}

.admin-page {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    padding: 40px;
    max-width: 1200px;
    margin: 0 auto;
    margin-top: 6rem;
}

.card {
    position: relative;
    background: rgba(0,0,0,0.4);
    border-radius: 12px;
    overflow: hidden;
    text-align: center;
    transition: transform 0.3s, box-shadow 0.3s;
    cursor: pointer;
    box-shadow: 0 0 20px rgba(0,0,0,0.5);
}

.card:hover {
    transform: translateY(-10px);
    box-shadow: 0 0 25px #2ecc71;
}

.image-container {
    position: relative;
    width: 100%;
    aspect-ratio: 16 / 9;
    overflow: hidden;
}

.image-container img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s;
}

.card:hover .image-container img {
    transform: scale(1.1);
}

.card-name {
    position: absolute;
    bottom: 10px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 1.5rem;
    font-weight: bold;
    color: #2ecc71;
    text-shadow: 0 0 10px #2ecc71;
    background: rgba(0,0,0,0.5);
    padding: 5px 10px;
    border-radius: 8px;
}

.card-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(to bottom, transparent, rgba(0,0,0,0.8));
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 20px;
    opacity: 0;
    transition: opacity 0.3s ease-in-out;
}

.card:hover .card-overlay {
    opacity: 1;
}

.card-info p {
    margin: 5px 0;
    font-size: 1rem;
    color: #ddd;
}

</style>
