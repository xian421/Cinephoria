<script>
    import { navigate } from 'svelte-routing';
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

main {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 40px;
    max-width: 1200px;
    margin: 0 auto;
}

h1 {
    margin-bottom: 40px;
    font-size: 3rem;
    color: #2ecc71;
    text-shadow: 0 0 20px #2ecc71, 0 0 40px #2ecc71;
    animation: glow 2s infinite alternate;
}

@keyframes glow {
  from {
    text-shadow: 0 0 10px #2ecc71, 0 0 20px #2ecc71;
  }
  to {
    text-shadow: 0 0 20px #2ecc71, 0 0 40px #2ecc71;
  }
}

.card-container {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 30px;
}

.card {
    background: rgba(0,0,0,0.4);
    width: 250px;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 0 20px rgba(0,0,0,0.5);
    text-align: center;
    transition: transform 0.3s, box-shadow 0.3s;
    cursor: pointer;
}

.card:hover {
    transform: translateY(-10px);
    box-shadow: 0 0 25px #2ecc71;
}

.card h2 {
    margin-bottom: 15px;
    font-size: 1.5rem;
    color: #2ecc71;
    text-shadow: 0 0 10px #2ecc71;
}

.card p {
    font-size: 1rem;
    color: #ddd;
    margin-bottom: 20px;
}

.card button {
    background-color: #2ecc71;
    color: #000;
    border: none;
    padding: 10px 20px;
    border-radius: 8px;
    font-size: 1rem;
    cursor: pointer;
    box-shadow: 0 0 10px #2ecc71;
    transition: background-color 0.3s, transform 0.3s;
}

.card button:hover {
    background-color: #27ae60;
    transform: translateY(-3px) scale(1.05);
    box-shadow: 0 0 15px #27ae60;
}

@media (max-width: 600px) {
    .card {
        width: 100%;
        max-width: 300px;
    }
}

</style>

<main>
    <h1>Adminbereich</h1>

    <div class="card-container">
        <!-- Karte für Kinosaal -->
        <div class="card" on:click={() => navigate('/adminkinosaal')}>
            <h2>Kinosaal verwalten</h2>
            <p>Säle erstellen, bearbeiten und Sitzpläne verwalten.</p>
            <button>Zum Kinosaal</button>
        </div>

        <!-- Karte für Vorstellung erstellen -->
        <div class="card" on:click={() => navigate('/adminshowtime')}>
            <h2>Vorstellungen</h2>
            <p>Neue Vorstellungen hinzufügen und planen.</p>
            <button>Vorstellung erstellen</button>
        </div>

        <!-- Karte für Preise -->
        <div class="card" on:click={() => navigate('/adminpreise')}>
            <h2>Preise festlegen</h2>
            <p>Preise für verschiedene Sitztypen festlegen.</p>
            <button>Preise verwalten</button>
        </div>

        <!-- Karte für Discounts -->
        <div class="card" on:click={() => navigate('/admindiscount')}>
            <h2>Discounts</h2>
            <p>Neue Discounts hinzufügen und verwalten.</p>
            <button>Discounts verwalten</button>
        </div>

        <!-- Karte für Rewards -->
        <div class="card" on:click={() => navigate('/adminrewards')}>
            <h2>Belohnungen</h2>
            <p>Neue Belohnungen hinzufügen und verwalten.</p>
            <button>Belohnungen verwalten</button>
        </div>
    </div>
</main>
