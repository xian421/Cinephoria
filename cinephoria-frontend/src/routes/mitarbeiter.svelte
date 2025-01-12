<script>
import { navigate } from 'svelte-routing';

    const handleSupermarktKasse = () => {
        navigate('/mitarbeiter/supermarkt');        
         };

    const handleKinoTicket = () => {
         navigate('/mitarbeiter/kino');
    };
</script>

<style>
    .container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh; /* Vollbildhöhe */
    }

    h1 {
        margin-bottom: 40px;
        font-size: 2.5rem;
        color: #333;
        text-align: center;
    }

    .buttons {
        display: flex;
        gap: 20px;
    }

    .button {
        padding: 20px 40px;
        font-size: 1.5rem;
        font-weight: bold;
        border: none;
        border-radius: 10px;
        cursor: pointer;
        transition: transform 0.2s, background-color 0.3s;
    }

    .button-supermarkt {
        background-color: #4caf50; /* Grün */
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .button-supermarkt:hover {
        background-color: #45a049;
        transform: translateY(-3px);
    }

    .button-kino {
        background-color: #2196f3; /* Blau */
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .button-kino:hover {
        background-color: #1e88e5;
        transform: translateY(-3px);
    }
</style>

<div class="container">
    <h1>Mitarbeiterbereich</h1>
    <div class="buttons">
        <button class="button button-supermarkt" on:click={handleSupermarktKasse}>
            Supermarkt-Kasse
        </button>
        <button class="button button-kino" on:click={handleKinoTicket}>
            Kino-Ticket
        </button>
    </div>
</div>
