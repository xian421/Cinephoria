<!-- mitarbeiterscannen.svelte -->
<script>
    import { fetchProductByBarcode } from '../services/api';
    import { authStore } from '../stores/authStore.js';
    import { get } from 'svelte/store';

    let barcodeInput = '';
    let scannedItems = [];
    let total = 0;
    let subtotal = 0;
    let tax = 0;
    let errorMessage = '';
    let paymentMethod = 'Bar'; // Standard Zahlungsmethode
    let discount = 0; // Rabatt in Euro

    // Konstante für Mehrwertsteuer (z.B. 19%)
    const TAX_RATE = 0.19;

    // Funktion zur Berechnung von Subtotal, MwSt. und Total
    function computeTotals() {
        subtotal = scannedItems.reduce((acc, item) => acc + (item.price * item.quantity), 0);
        tax = subtotal * TAX_RATE;
        total = subtotal + pfandTotal() - discount;
    }

    // Funktion zur Berechnung der gesamten Pfandbeträge
    function pfandTotal() {
        return scannedItems.reduce((acc, item) => acc + (item.pfandPrice * item.quantity), 0);
    }

    async function handleScan() {
        const barcode = barcodeInput.trim();
        if (!barcode) {
            errorMessage = 'Bitte geben Sie einen Barcode ein.';
            return;
        }

        const token = get(authStore).token;
        try {
            const data = await fetchProductByBarcode(token, barcode);
            const product = data; // API gibt das gesamte Objekt zurück
            console.log(product);

            if (product) {
                const itemName = product.item_name;
                const itemPrice = parseFloat(product.price) || 0;
                const pfandName = product.pfand_name || null;
                const pfandPrice = parseFloat(product.amount) || 0;

                // Prüfen, ob der Artikel bereits gescannt wurde
                const existingItemIndex = scannedItems.findIndex(item => item.item_id === product.item_id);

                if (existingItemIndex !== -1) {
                    // Artikel existiert bereits, Menge und Gesamtpreis erhöhen
                    scannedItems[existingItemIndex].quantity += 1;
                    scannedItems[existingItemIndex].totalPrice += (itemPrice + pfandPrice);
                } else {
                    // Neuer Artikel hinzufügen
                    scannedItems = [
                        ...scannedItems,
                        { 
                            item_id: product.item_id,
                            name: itemName,
                            price: itemPrice,
                            pfandName: pfandName,
                            pfandPrice: pfandPrice,
                            quantity: 1,
                            totalPrice: itemPrice + pfandPrice
                        }
                    ];
                }

                // Reaktive Aktualisierung des Arrays
                scannedItems = [...scannedItems];

                // Berechnungen aktualisieren
                computeTotals();

                errorMessage = '';
                barcodeInput = '';
            } else {
                errorMessage = 'Artikel nicht gefunden.';
            }
        } catch (error) {
            console.error('Fehler beim Scannen des Artikels:', error);
            errorMessage = error.message || 'Fehler beim Scannen des Artikels.';
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
        subtotal = 0;
        tax = 0;
        discount = 0;
        errorMessage = '';
        barcodeInput = '';
    }

    function applyDiscount() {
        // Rabatt nicht negativ und nicht größer als subtotal + tax
        if (discount < 0) {
            discount = 0;
        } else if (discount > (subtotal + tax)) {
            discount = subtotal + tax;
        }
        computeTotals();
    }

    function removeItem(item_id) {
        const item = scannedItems.find(i => i.item_id === item_id);
        if (item) {
            scannedItems = scannedItems.filter(i => i.item_id !== item_id);
            computeTotals();
        }
    }

    function changePaymentMethod(method) {
        paymentMethod = method;
    }

    function printReceipt() {
        window.print();
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

    .subtotal, .tax, .discount, .total {
        display: flex;
        justify-content: space-between;
        font-weight: bold;
        font-size: 1.2rem;
        margin-top: 10px;
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
        margin: 0 5px;
    }

    .actions button:hover {
        background-color: #c82333;
    }

    .payment-method {
        margin-top: 20px;
        text-align: center;
    }

    .payment-method label {
        margin-right: 10px;
    }

    .remove-button {
        background-color: transparent;
        border: none;
        color: red;
        cursor: pointer;
        font-size: 0.9rem;
        margin-left: 10px;
    }

    .remove-button:hover {
        text-decoration: underline;
    }

    @media print {
        .scanner, .actions, .payment-method, .error {
            display: none;
        }

        .receipt {
            border: none;
            background-color: white;
        }
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
                    <span>{index + 1}. {item.name} x{item.quantity}</span>
                    <span>{(item.price * item.quantity).toFixed(2)} €</span>
                </div>
                {#if item.pfandPrice > 0}
                    <div class="receipt-item" style="margin-left: 20px;">
                        <span>Pfand für {item.name} x{item.quantity}</span>
                        <span>{(item.pfandPrice * item.quantity).toFixed(2)} €</span>
                    </div>
                {/if}
                <div class="receipt-item">
                    <button class="remove-button" on:click={() => removeItem(item.item_id)}>Artikel entfernen</button>
                </div>
            {/each}
            {#if scannedItems.length === 0}
                <div style="text-align: center; color: #777;">Keine Artikel gescannt.</div>
            {/if}
        </div>
        <div class="subtotal">
            <span>Zwischensumme:</span>
            <span>{subtotal.toFixed(2)} €</span>
        </div>
        <div class="tax">
            <span>MwSt. (19%):</span>
            <span>{tax.toFixed(2)} €</span>
        </div>
        <div class="discount">
            <span>Rabatt:</span>
            <span>
                <input 
                    type="number" 
                    step="0.01" 
                    bind:value={discount} 
                    on:change={applyDiscount} 
                    placeholder="Rabatt in €" 
                    style="width: 100px; padding: 5px; border: 1px solid #ddd; border-radius: 5px;"
                /> € 
            </span>
        </div>
        <div class="total">
            <span>Gesamt:</span>
            <span>{total.toFixed(2)} €</span>
        </div>
    </div>

    {#if scannedItems.length > 0}
        <div class="payment-method">
            <label for="payment">Zahlungsmethode:</label>
            <select id="payment" bind:value={paymentMethod}>
                <option value="Bar">Bar</option>
                <option value="Kreditkarte">Kreditkarte</option>
                <option value="Debitkarte">Debitkarte</option>
                <option value="PayPal">PayPal</option>
                <option value="Andere">Andere</option>
            </select>
        </div>

        <div class="actions">
            <button on:click={resetScan}>Neuer Scan</button>
            <button on:click={printReceipt}>Quittung Drucken</button>
        </div>
    {/if}
</div>
