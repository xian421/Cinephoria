<script>
    import { navigate } from 'svelte-routing';
</script>

<style>
    main {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 20px;
        font-family: Arial, sans-serif;
    }

    h1 {
        margin-bottom: 20px;
    }

    .card-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 20px;
    }

    .card {
        background-color: #f9f9f9;
        width: 250px;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        transition: transform 0.3s, box-shadow 0.3s;
        cursor: pointer;
    }

    .card:hover {
        transform: translateY(-10px);
        box-shadow: 0 6px 10px rgba(0, 0, 0, 0.15);
    }

    .card h2 {
        margin-bottom: 15px;
        font-size: 1.5rem;
        color: #333;
    }

    .card p {
        font-size: 1rem;
        color: #666;
        margin-bottom: 20px;
    }

    .card button {
        background-color: #1976d2;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-size: 1rem;
        cursor: pointer;
        transition: background-color 0.3s;
    }

    .card button:hover {
        background-color: #1565c0;
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
</main>
