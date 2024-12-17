<script>
    // Beispielhafte Benutzerdaten für das Leaderboard
    const leaderboard = [
        { id: 1, name: 'Max Mustermann', points: 350, image: '/user1.webp' },
        { id: 2, name: 'Anna Müller', points: 300, image: '/user2.webp' },
        { id: 3, name: 'Lisa Schmidt', points: 250, image: '/user3.webp' },
        { id: 4, name: 'Tom Becker', points: 200, image: '/user4.webp' },
        { id: 5, name: 'Felix Weber', points: 150, image: '/user5.webp' },
        { id: 6, name: 'Julia Klein', points: 100, image: '/user6.webp' }
    ];
</script>

<style>
    /* Container-Styling */
    .leaderboard-container {
        max-width: 900px;
        margin: 2rem auto;
        padding: 2rem;
        background: linear-gradient(to bottom, #fdfdfd, #e9e9e9);
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
        font-family: 'Roboto', sans-serif;
    }

    .leaderboard-header {
        text-align: center;
        margin-bottom: 3rem;
    }

    .leaderboard-header h1 {
        font-size: 2.5rem;
        color: #f39c12;
        margin-bottom: 0.5rem;
    }

    .leaderboard-header p {
        font-size: 1.2rem;
        color: #555;
    }

    /* Rangliste */
    .leaderboard-list {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
    }

    .leaderboard-card {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #ffffff;
        border-radius: 12px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        padding: 1rem 1.5rem;
        transition: transform 0.3s ease;
        position: relative;
    }

    .leaderboard-card:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
    }

    /* Highlight für die Top-3 */
    .leaderboard-card.top-1 {
        background: #f1c40f;
        color: #ffffff;
        box-shadow: 0 10px 20px rgba(241, 196, 15, 0.5);
    }

    .leaderboard-card.top-2 {
        background: #95a5a6;
        color: #ffffff;
    }

    .leaderboard-card.top-3 {
        background: #cd7f32;
        color: #ffffff;
    }

    .rank-badge {
        font-size: 2rem;
        font-weight: bold;
        margin-right: 1rem;
    }

    .profile-info {
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    .profile-info img {
        width: 60px;
        height: 60px;
        object-fit: cover;
        border-radius: 50%;
        border: 3px solid #ddd;
    }

    .leaderboard-points {
        font-weight: bold;
        font-size: 1.2rem;
        color: #2ecc71;
    }

    /* Spezieller Stil für die Top-Ränge */
    .rank-icon {
        position: absolute;
        top: -10px;
        left: -10px;
        width: 40px;
        height: 40px;
    }
</style>

<main class="leaderboard-container">
    <div class="leaderboard-header">
        <h1>🏆 Leaderboard 🏆</h1>
        <p>Die besten Spieler und Punktesammler auf einen Blick!</p>
    </div>

    <!-- Rangliste anzeigen -->
    <div class="leaderboard-list">
        {#each leaderboard as user, index}
            <div class="leaderboard-card {index === 0 ? 'top-1' : index === 1 ? 'top-2' : index === 2 ? 'top-3' : ''}">
                <!-- Highlight-Icon für Top 3 -->
                {#if index === 0}
                    <img src="/rank1.png" alt="Gold Crown" class="rank-icon" />
                {:else if index === 1}
                    <img src="/rank2.png" alt="Silver Crown" class="rank-icon" />
                {:else if index === 2}
                    <img src="/rank3.png" alt="Bronze Crown" class="rank-icon" />
                {/if}

                <!-- Rangnummer -->
                <div class="rank-badge">#{index + 1}</div>

                <!-- Benutzerprofil -->
                <div class="profile-info">
                    <img src="{user.image}" alt="{user.name}" />
                    <div>
                        <h3>{user.name}</h3>
                        <p class="leaderboard-points">{user.points} Punkte</p>
                    </div>
                </div>
            </div>
        {/each}
    </div>
</main>
