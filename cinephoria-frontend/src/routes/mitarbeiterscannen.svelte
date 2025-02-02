<!-- src/routes/mitarbeiterscannen.svelte -->
<script>
    import { get } from 'svelte/store';
    import BarcodeScanner from '../components/BarcodeScanner.svelte';
    import Receipt from '../components/Receipt.svelte';
    import PaymentMethod from '../components/PaymentMethod.svelte';
    import { fetchProductByBarcode } from '../services/api';
    import { authStore } from '../stores/authStore.js';
    import { computeTotals } from '../utils/computeTotals.js';
    import { showErrorToast, showSuccessAlert, showSuccessToast } from '../utils/notifications.js';
    import { testPrint } from '../utils/print.js';

  
    let barcodeInput = '';
    let scannedItems = [];
    let discount = 0;
    let paymentMethod = 'Bar';
  
    // Reaktive Totals: Werden immer neu berechnet, wenn scannedItems oder discount sich ändert.
    let subtotal = 0, tax = 0, total = 0;
    function updateTotals() {
      const totals = computeTotals(scannedItems, discount);
      subtotal = totals.subtotal;
      tax = totals.tax;
      total = totals.total;
    }

    $: updateTotals();
  
    async function handleScan({ detail }) {
      const barcode = detail.barcode.trim();
      if (!barcode) {
        showErrorToast('Bitte geben Sie einen Barcode ein.');
        return;
      }
      const token = get(authStore).token;
      try {
        const product = await fetchProductByBarcode(token, barcode);
        if (product) {
          const { item_id, item_name, price, pfand_name, amount } = product;
          const itemPrice = parseFloat(price) || 0;
          const pfandPrice = parseFloat(amount) || 0;
  
          const index = scannedItems.findIndex(item => item.item_id === item_id);
          if (index !== -1) {
            scannedItems[index].quantity += 1;
            scannedItems[index].totalPrice += (itemPrice + pfandPrice);
            scannedItems = [...scannedItems];
          } else {
            scannedItems = [
              ...scannedItems,
              {
                item_id,
                name: item_name,
                price: itemPrice,
                pfandName: pfand_name || null,
                pfandPrice,
                quantity: 1,
                totalPrice: itemPrice + pfandPrice
              }
            ];
          }
          showSuccessToast('Artikel erfolgreich gescannt!');
        } else {
          showErrorToast('Artikel nicht gefunden.');
        }
      } catch (error) {
        console.error('Fehler beim Scannen:', error);
        showErrorToast(error.message || 'Fehler beim Scannen des Artikels.');
      }
    }
  
    function handleRemove({ detail }) {
      const { item_id } = detail;
      const item = scannedItems.find(i => i.item_id === item_id);
      if (item) {
        scannedItems = scannedItems.filter(i => i.item_id !== item_id);
        showSuccessAlert(`Artikel "${item.name}" entfernt.`);
      }
    }
  
    function handlePaymentChange({ detail }) {
      paymentMethod = detail.method;
    }
  
    function resetScan() {
      scannedItems = [];
      discount = 0;
    }
  
    function printReceipt() {
      testPrint(scannedItems, total, paymentMethod);
    }    
  
    // Falls du den Rabatt dynamisch validieren möchtest, kannst du auch hier einen reaktiven Block einsetzen:
    $: if (discount < 0) discount = 0;
    $: if (discount > (subtotal + tax)) discount = subtotal + tax;
  </script>
  
  <style>
    .container {
      max-width: 800px;
      margin: 0 auto;
      padding: 20px;
      font-family: 'Arial', sans-serif;
      color: #333;
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
    @media print {
      .actions, .payment-method, .scanner {
        display: none;
      }
      .receipt {
        border: none;
        background-color: white;
      }
    }
  </style>
  
  <div class="container">
    <h1>Mitarbeiterscannen</h1>
  
    <!-- BarcodeScanner-Komponente -->
    <BarcodeScanner bind:value={barcodeInput} on:scan={handleScan} />
  
    <!-- Quittungsanzeige -->
    <Receipt 
      {scannedItems} 
      {subtotal} 
      {tax} 
      discount={discount} 
      {total} 
      on:remove={handleRemove}
    />
  
    <!-- Zahlungsmethode -->
    {#if scannedItems.length > 0}
      <PaymentMethod method={paymentMethod} on:change={handlePaymentChange} />
    {/if}
  
    <!-- Aktionen -->
    {#if scannedItems.length > 0}
      <div class="actions">
        <button on:click={resetScan}>Neuer Scan</button>
        <button on:click={printReceipt}>Quittung Drucken</button>
      </div>
    {/if}
  </div>
  