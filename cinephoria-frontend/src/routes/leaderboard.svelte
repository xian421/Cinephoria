<script>
    import { onMount } from 'svelte';
    import { fetchLeaderboard } from '../services/api.js';
    
    // Beispielhafte Benutzerdaten für das Leaderboard
    let leaderboard = []; 
    
    // Lade die Rangliste beim Laden der Seite
    onMount(async () => {
        try {
            // Lade die Rangliste von der API
            const data = await fetchLeaderboard();
    
            // Aktualisiere die lokale Rangliste
            leaderboard = data.leaderboard;
            console.log('Rangliste geladen:', leaderboard);
        } catch (error) {
            console.error('Fehler beim Laden der Rangliste:', error);
        }
    });
    
    // Funktion zur Ermittlung der Initialen aus dem Namen
    function getInitials(name) {
        const names = name.trim().split(' ');
        if (names.length === 1) {
            return names[0].charAt(0).toUpperCase();
        } else {
            return (names[0].charAt(0) + names[names.length - 1].charAt(0)).toUpperCase();
        }
    }
    </script>
    
    <style>
        /* Container-Styling */
        .leaderboard-container {
            max-width: 900px;
            margin: 2rem auto;
            padding: 2rem;
            border-radius: 20px;
            font-family: 'Roboto', sans-serif;
            max-width: 1200px;
            background: rgba(0,0,0,0.6); /* Optional: Hintergrund für bessere Lesbarkeit */
        }
    
        .leaderboard-header {
            font-size: 20px;
            margin: 0;
            color: #2ecc71;
            text-shadow: 0 0 20px #2ecc71, 0 0 40px #2ecc71;
            animation: glow 2s infinite alternate;
        }
    
        /* Rangliste */
        .leaderboard-list {
            display: flex;
            flex-wrap: wrap;
            gap: 1.5rem;
            justify-content: center;
        }
    
        .leaderboard-card {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(0,0,0,0.4);
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            padding: 1rem 1.5rem;
            transition: transform 0.3s ease;
            position: relative;
            width: 100%;
            max-width: 350px; /* Optional: Begrenzung der maximalen Breite */
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
    
        .profile-info img, .profile-initials {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            border: 3px solid #ddd;
            object-fit: cover;
            box-sizing: border-box;
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
    
        /* Styling für die Initialen */
        .profile-initials {
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: #1abc9c;
            color: #fff;
            font-size: 1rem;
            font-weight: bold;
            border: 3px solid #ddd;
        }
    
        .profile-initials:hover {
            background-color: #16a085;
            transform: scale(1.05);
            box-shadow: 0 0 10px #2ecc71;
        }
    
        /* Responsive Design */
        @media (max-width: 768px) {
            .leaderboard-card {
                flex: 0 0 calc(50% - 1rem);
            }
        }
    
        @media (max-width: 480px) {
            .leaderboard-card {
                flex: 0 0 100%;
            }
        }
    
        @keyframes glow {
            from {
                text-shadow: 0 0 10px #2ecc71, 0 0 20px #2ecc71;
            }
            to {
                text-shadow: 0 0 20px #2ecc71, 0 0 40px #2ecc71;
            }
        }
    </style>
    
    <main class="leaderboard-container">
        <div class="leaderboard-header">
            <h1>🏆 Leaderboard 🏆</h1>
            <p>Die User mit der meisten Watchtime!</p>
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
                        {#if user.profile_image && user.profile_image !== 'default.png'}
                            <img src={`/Profilbilder/${user.profile_image}`} alt="{user.nickname}" />
                        {:else}
                            <div class="profile-initials">{getInitials(user.nickname)}</div>
                        {/if}
                        <div>
                            <h3>{user.nickname}</h3>
                            <p class="leaderboard-points">{Math.round(user.total_duration)} Minuten</p>
                        </div>
                    </div>
                </div>
            {/each}
        </div>
    </main>
    