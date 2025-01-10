<!-- src/routes/Ticketanzeige.svelte -->
<script lang="ts">
    import { navigate } from 'svelte-routing';
</script>

        <h1 >Danke für Ihre Bestellung</h1>
        <h2>Ihre Tickets haben Sie per Mail bekommen.</h2>
        <button class="button" on:click={() => navigate('/')}> Zur Startseite </button>
<style>

    .button {
      font-size: 1rem;
      font-weight: bold;
      border: none;
      border-radius: 10px;
      padding: 0.7rem 1.2rem;
      cursor: pointer;
      transition: transform 0.3s ease;
      background-color: #2ecc71;
      color: #000;
      box-shadow: 0 0 10px #2ecc71;
    }
</style>