<script>
    import Swal from 'sweetalert2';
    import { onMount } from 'svelte';
    import { pointsStore, fetchUserPointsStore, redeemUserPointsStore } from '../stores/pointsStore';
    import { fetchRewards } from '../services/api';

    // Beispielhafte Belohnungen, jedes Objekt hat ein `image`-Attribut
    let rewards = [];

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

        try {
            rewards = await fetchRewards();
        } catch (error) {
            errorMessage = error.message || 'Fehler beim Abrufen der Belohnungen.';
            console.error('Fehler beim Abrufen der Belohnungen:', errorMessage);
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
    body {
    margin: 0;
    font-family: 'Roboto', sans-serif;
    background: linear-gradient(135deg, #000428, #004e92);
    color: #fff;
    overflow-x: hidden;
    max-width: 100%;
}

.rewards-container {
    max-width: 1200px;
    margin: 4rem auto;
    padding: 2rem;
    position: relative;
    display: flex;
    flex-direction: column;
    gap: 3rem;
    text-align: center;
}

.rewards-header h1 {
    font-size: 3rem;
    color: #2ecc71;
    text-shadow: 0 0 20px #2ecc71, 0 0 40px #2ecc71;
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

.rewards-header p {
    font-size: 1.2rem;
    color: #ddd;
    margin-top: 1rem;
}

.summary-points {
    font-size: 1.3rem;
    color: #2ecc71;
    text-shadow: 0 0 10px #2ecc71;
    margin-bottom: 2rem;
}

.summary-points strong {
    color: #fff;
    text-shadow: 0 0 5px #fff;
}

.error-message {
    color: #e74c3c;
    text-shadow: 0 0 5px #e74c3c;
    font-size: 1.2rem;
    margin-bottom: 2rem;
}

.rewards-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
}

.reward-card {
    background: rgba(0,0,0,0.4);
    border-radius: 12px;
    box-shadow: 0 0 20px rgba(0,0,0,0.5);
    padding: 1.5rem;
    text-align: center;
    transition: transform 0.3s, box-shadow 0.3s;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.reward-card:hover {
    transform: translateY(-10px);
    box-shadow: 0 0 25px #2ecc71;
}

.reward-card img {
    width: 150px;
    height: 150px;
    object-fit: cover;
    border-radius: 10%;
    margin-bottom: 1rem;
    box-shadow: 0 0 10px #2ecc71;
    transition: transform 0.3s;
}

.reward-card:hover img {
    transform: scale(1.1);
}

.reward-card h3 {
    font-size: 1.5rem;
    color: #2ecc71;
    margin: 0.5rem 0;
    text-shadow: 0 0 5px #2ecc71;
}

.reward-card p {
    font-size: 1rem;
    color: #ddd;
    margin: 0.5rem 0;
    text-shadow: 0 0 2px #fff;
}

.reward-points {
    font-weight: bold;
    color: #e74c3c;
    text-shadow: 0 0 5px #e74c3c;
    font-size: 1.2rem;
    margin-top: auto;
}

/* Responsive Anpassungen */
@media (max-width: 600px) {
    .rewards-container {
        padding: 2rem 1rem;
    }

    .reward-card img {
        width: 120px;
        height: 120px;
    }
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
