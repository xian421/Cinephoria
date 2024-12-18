<script>
    import Swal from 'sweetalert2';
    import { onMount } from 'svelte';
    import { pointsStore, fetchUserPointsStore, redeemUserPointsStore } from '../stores/pointsStore';

    // Beispielhafte Belohnungen, jedes Objekt hat ein `image`-Attribut
    const rewards = [
        { id: 1, title: 'Popcorn-Gutschein', points: 50, description: 'Ein mittelgroßer Popcorn-Gutschein.', image: '/popcorn.webp' },
        { id: 2, title: 'Freikarte', points: 100, description: 'Eine kostenlose Kinokarte für einen Film deiner Wahl.', image: '/freikarte.webp' },
        { id: 3, title: 'VIP-Lounge Zugang', points: 200, description: 'Ein exklusiver Zugang zur VIP-Lounge.', image: '/vip.webp' },
        { id: 4, title: 'Softdrink-Gutschein', points: 30, description: 'Ein Softdrink deiner Wahl.', image: '/trinken.webp' },
        { id: 5, title: 'Nacho-Gutschein', points: 70, description: 'Eine Portion leckere Nachos.', image: '/nachos.webp' },
        { id: 6, title: 'Premium-Upgrade', points: 150, description: 'Upgraden zu Premium-Sitzen.', image: '/premium.webp' }
    ];

    let userPoints = 0;
    let errorMessage = '';

    // Abrufen des Tokens (angepasst an deine Authentifizierungslogik)
    const token = localStorage.getItem('token'); // Stelle sicher, dass der Token korrekt gespeichert ist

    onMount(async () => {
        if (!token) {
            errorMessage = 'Kein Authentifizierungs-Token gefunden.';
            console.error(errorMessage);
            return;
        }

        try {
            const points = await fetchUserPointsStore(token);
            console.log(`Aktuelle Punkte: ${points}`);
        } catch (error) {
            errorMessage = error.message || 'Fehler beim Abrufen der Punkte.';
            console.error('Fehler beim Abrufen der Punkte:', errorMessage);
        }
    });

    // Abonniere den Store, um den Punktestand zu aktualisieren
    pointsStore.subscribe(value => {
        userPoints = value;
        console.log(`Store Points Updated: ${userPoints}`);
    });

    async function redeemReward(reward) {
        if (userPoints >= reward.points) {
            try {
                const message = await redeemUserPointsStore(token, reward.points);
                console.log(`Belohnung eingelöst: ${reward.title}, verbleibende Punkte: ${userPoints}`);
                Swal.fire({
                    title: 'Erfolg!',
                    text: `Du hast die Belohnung "${reward.title}" eingelöst!`,
                    icon: 'success'
                });
            } catch (error) {
                Swal.fire({
                    title: 'Fehler',
                    text: error.message,
                    icon: 'error'
                });
            }
        } else {
            Swal.fire({
                title: 'Nicht genug Punkte',
                text: `Du benötigst ${reward.points - userPoints} weitere Punkte für diese Belohnung.`,
                icon: 'error'
            });
        }
    }
</script>

<style>
    .rewards-container {
        max-width: 1200px;
        margin: 2rem auto;
        padding: 2rem;
        background: #fdfdfd;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        font-family: 'Roboto', sans-serif;
        max-width: 1200px;
    }

    .rewards-header {
        text-align: center;
        margin-bottom: 2rem;
    }

    .rewards-header h1 {
        font-size: 2rem;
        color: #3498db;
    }

    .summary-points {
        text-align: center;
        margin-bottom: 2rem;
        font-size: 1.2rem;
        color: #2ecc71;
    }

    .rewards-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.5rem;
    }

    .reward-card {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: space-between;
        background: #ffffff;
        border-radius: 12px;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
        padding: 1rem;
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        cursor: pointer;
        max-width: 300px;
    }

    .reward-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
    }

    .reward-card img {
        width: 150px;
        height: 150px;
        object-fit: cover;
        border-radius: 5%;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }

    .reward-card h3 {
        font-size: 1.2rem;
        color: #3498db;
        margin: 0.5rem 0;
    }

    .reward-card p {
        font-size: 0.9rem;
        color: #777;
        margin: 0.5rem 0;
    }

    .reward-points {
        font-weight: bold;
        color: #e74c3c;
    }
</style>

<main class="rewards-container">
    <div class="rewards-header">
        <h1>Belohnungen einlösen</h1>
        <p>Wähle eine Belohnung aus und löse deine gesammelten Punkte ein!</p>
    </div>

    <!-- Fehlernachricht anzeigen -->
    {#if errorMessage}
        <div class="error-message">
            <p>{errorMessage}</p>
        </div>
    {/if}

    <!-- Benutzerpunkte anzeigen -->
    <div class="summary-points">
        Du hast <strong>{userPoints}</strong> Punkte gesammelt.
    </div>

    <!-- Belohnungen in einem Grid -->
    <div class="rewards-grid">
        {#each rewards as reward}
            <div class="reward-card" on:click={() => redeemReward(reward)}>
                <img src="{reward.image}" alt="{reward.title}" />
                <h3>{reward.title}</h3>
                <p>{reward.description}</p>
                <p class="reward-points">{reward.points} Punkte</p>
            </div>
        {/each}
    </div>
</main>
