<!-- src/components/ProductForm.svelte -->
<script>
    import { createEventDispatcher } from 'svelte';

    export let product = { barcode: '', item_name: '', price: '', category: '', pfand_id: null };
    export let pfandOptions = [];
    export let isEditing = false;
    export let isSubmitting = false;

    const dispatch = createEventDispatcher();

    function handleSubmit() {
        // Dispatch das Submit-Event mit dem Produkt
        dispatch('submit', { product });
    }
</script>

<div class="form-container">
    <label for="barcode">Barcode:</label>
    <input id="barcode" type="text" bind:value={product.barcode} />

    <label for="item_name">Name:</label>
    <input id="item_name" type="text" bind:value={product.item_name} />

    <label for="price">Preis (€):</label>
    <input id="price" type="number" step="0.01" bind:value={product.price} />

    <label for="category">Kategorie:</label>
    <input id="category" type="text" bind:value={product.category} />

    <label for="pfand_id">Pfand:</label>
    <select 
        id="pfand_id" 
        bind:value={product.pfand_id}
        on:change={e => product.pfand_id = e.target.value ? parseInt(e.target.value) : null}
    >
        <option value="">Kein Pfand</option>
        {#each pfandOptions as pfand}
            <option value={pfand.pfand_id}>{pfand.name} ({pfand.amount}€)</option>
        {/each}
    </select>

    <button on:click={handleSubmit} disabled={isSubmitting}>
        {isSubmitting ? (isEditing ? 'Aktualisieren...' : 'Hinzufügen...') : (isEditing ? 'Aktualisieren' : 'Hinzufügen')}
    </button>
</div>

<style>
    .form-container {
        display: flex;
        flex-direction: column;
        gap: 15px;
    }

    .form-container label {
        font-size: 1rem;
        font-weight: bold;
    }

    .form-container input[type="text"],
    .form-container input[type="number"],
    .form-container select {
        padding: 10px;
        font-size: 1rem;
        border: 1px solid #ddd;
        border-radius: 5px;
    }

    .form-container input[type="checkbox"] {
        margin-right: 10px;
    }

    .form-container button {
        padding: 10px;
        font-size: 1rem;
        background-color: #007bff;
        color: #fff;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-weight: bold;
        transition: background-color 0.3s;
    }

    .form-container button:hover {
        background-color: #0056b3;
    }
</style>
