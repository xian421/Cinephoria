<!-- mitarbeiterscannen.svelte -->
<script>
    import { onMount } from 'svelte';

    // Fake-Daten für die Demonstration
    const fakeProducts = {
        '1234567890123': { name: 'Apfel', price: 0.99 },
        '9876543210987': { name: 'Bananen', price: 1.29 },
        '5555555555555': { name: 'Milch', price: 0.89 },
        '4444444444444': { name: 'Brot', price: 1.49 },
        '3333333333333': { name: 'Käse', price: 2.99 }
    };

    let barcodeInput = '';
    let scannedItems = [];
    let total = 0;
    let errorMessage = '';

    function handleScan() {
        const barcode = barcodeInput.trim();
        if (!barcode) {
            errorMessage = 'Bitte geben Sie einen Barcode ein.';
            return;
        }

        const product = fakeProducts[barcode];
        if (product) {
            scannedItems = [...scannedItems, { ...product, barcode }];
            total += product.price;
            errorMessage = '';
            barcodeInput = '';
        } else {
            errorMessage = 'Artikel nicht gefunden.';
        }
    }

    function handleEnter(event) {
        if (event.key === 'Enter') {
            handleScan();
        }
    }

    function resetScan() {
        scannedItems = [];
        total = 0;
        errorMessage = '';
        barcodeInput = '';
    }
</script>

<style>
    .container {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
        font-family: 'Arial', sans-serif;
        color: #333;
    }

    .title {
        text-align: center;
        font-size: 2rem;
        margin-bottom: 20px;
    }

    .scanner {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-bottom: 30px;
    }

    .scanner input {
        width: 300px;
        padding: 10px;
        font-size: 1rem;
        border: 1px solid #ddd;
        border-radius: 5px;
        margin-bottom: 10px;
    }

    .scanner button {
        padding: 10px 20px;
        font-size: 1rem;
        background-color: #007bff;
        color: #fff;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        transition: background-color 0.3s;
    }

    .scanner button:hover {
        background-color: #0056b3;
    }

    .error {
        color: red;
        margin-top: 10px;
    }

    .receipt {
        border: 2px dashed #ccc;
        padding: 20px;
        border-radius: 10px;
        background-color: #f9f9f9;
    }

    .receipt-header {
        text-align: center;
        margin-bottom: 20px;
    }

    .receipt-header h2 {
        margin: 0;
        font-size: 1.5rem;
    }

    .receipt-items {
        margin-bottom: 20px;
    }

    .receipt-item {
        display: flex;
        justify-content: space-between;
        padding: 5px 0;
        border-bottom: 1px solid #ddd;
    }

    .receipt-item:last-child {
        border-bottom: none;
    }

    .total {
        display: flex;
        justify-content: space-between;
        font-weight: bold;
        font-size: 1.2rem;
    }

    .actions {
        text-align: center;
        margin-top: 20px;
    }

    .actions button {
        padding: 10px 20px;
        font-size: 1rem;
        background-color: #dc3545;
        color: #fff;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        transition: background-color 0.3s;
    }

    .actions button:hover {
        background-color: #c82333;
    }
</style>

<div class="container">
    <h1 class="title">Mitarbeiterscannen</h1>

    <div class="scanner">
        <input 
            type="text" 
            placeholder="Barcode eingeben" 
            bind:value={barcodeInput} 
            on:keydown={handleEnter}
        />
        <button on:click={handleScan}>Abschicken</button>
        {#if errorMessage}
            <div class="error">{errorMessage}</div>
        {/if}
    </div>

    <div class="receipt">
        <div class="receipt-header">
            <h2>Quittung</h2>
        </div>
        <div class="receipt-items">
            {#each scannedItems as item, index}
                <div class="receipt-item">
                    <span>{index + 1}. {item.name}</span>
                    <span>{item.price.toFixed(2)} €</span>
                </div>
            {/each}
            {#if scannedItems.length === 0}
                <div style="text-align: center; color: #777;">Keine Artikel gescannt.</div>
            {/if}
        </div>
        <div class="total">
            <span>Gesamt:</span>
            <span>{total.toFixed(2)} €</span>
        </div>
    </div>

    {#if scannedItems.length > 0}
        <div class="actions">
            <button on:click={resetScan}>Neuer Scan</button>
        </div>
    {/if}
</div>
