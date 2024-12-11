<script>
    import { addDiscount } from '../services/api.js';
    import { authStore } from '../stores/authStore';
    import { get } from 'svelte/store';

    let name = '';
    let description = '';

    const handleAddDiscount = async () => {
        const token = get(authStore).token;
        try {
            const response = await addDiscount(token, name, description);
            alert(response.message);
            // Aktualisieren Sie die Liste der Discounts oder führen Sie weitere Aktionen durch
        } catch (error) {
            alert(error.message);
        }
    };
</script>

<div>
    <h2>Neuen Discount hinzufügen</h2>
    <input type="text" bind:value={name} placeholder="Name" />
    <textarea bind:value={description} placeholder="Beschreibung"></textarea>
    <button on:click={handleAddDiscount}>Hinzufügen</button>
</div>
