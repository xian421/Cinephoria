<!-- src/routes/mitarbeiterscannen.svelte-->
<script>
  import { get } from 'svelte/store';
  import BarcodeScanner from '../components/BarcodeScanner.svelte';
  import Receipt from '../components/Receipt.svelte';
  import PaymentMethod from '../components/PaymentMethod.svelte';
  import { fetchProductByBarcode } from '../services/api';
  import { authStore } from '../stores/authStore.js';
  import { computeTotals } from '../utils/computeTotals.js';
  import { showErrorToast, showSuccessAlert, showSuccessToast } from '../utils/notifications.js';

  let barcodeInput = '';
  let scannedItems = [];
  let discount = 0;
  let paymentMethod = 'Bar';

  // Referenz auf die BarcodeScanner-Komponente
  let barcodeScanner;

  // Reaktive Berechnung der Totals (zusätzlich erhalten wir auch den Bruttobetrag)
  $: ({ subtotal, pfand, tax, total, gross } = computeTotals(scannedItems, discount));

  // Helper-Funktion, um den Fokus auf das Barcode-Eingabefeld zu setzen
  function focusBarcodeInput() {
    if (barcodeScanner && barcodeScanner.focusInput) {
      barcodeScanner.focusInput();
    }
  }

  // Artikel hinzufügen oder aktualisieren
  function addOrUpdateItem(item) {
    const index = scannedItems.findIndex(i => i.item_id === item.item_id);
    if (index !== -1) {
      scannedItems[index].quantity += 1;
      scannedItems[index].totalPrice += (item.price + item.pfandPrice);
      scannedItems = [...scannedItems];
    } else {
      scannedItems = [
        ...scannedItems,
        {
          ...item,
          quantity: 1,
          totalPrice: item.price + item.pfandPrice
        }
      ];
    }
    focusBarcodeInput();
  }

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
        const productData = {
          item_id,
          name: item_name,
          price: itemPrice,
          pfandName: pfand_name || null,
          pfandPrice
        };
        addOrUpdateItem(productData);
        showSuccessToast('Artikel erfolgreich gescannt!');
      } else {
        showErrorToast('Artikel nicht gefunden.');
      }
    } catch (error) {
      console.error('Fehler beim Scannen:', error);
      showErrorToast(error.message || 'Fehler beim Scannen des Artikels.');
    }
  }

  // Entfernt einen Artikel oder reduziert dessen Menge
  function handleRemove({ detail }) {
    const { item_id } = detail;
    const index = scannedItems.findIndex(item => item.item_id === item_id);
    if (index !== -1) {
      const item = scannedItems[index];
      if (item.quantity > 1) {
        item.quantity -= 1;
        item.totalPrice -= (item.price + item.pfandPrice);
        scannedItems = [...scannedItems];
        showSuccessToast(`Die Menge von "${item.name}" wurde verringert.`);
      } else {
        scannedItems = scannedItems.filter(i => i.item_id !== item_id);
        showSuccessToast(`Artikel "${item.name}" entfernt.`);
      }
    }
    focusBarcodeInput();
  }

  function handlePaymentChange({ detail }) {
    paymentMethod = detail.method;
  }

  function resetScan() {
    scannedItems = [];
    discount = 0;
    focusBarcodeInput();
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
  .discount-input {
    text-align: center;
    margin: 20px 0;
  }
  .discount-input input {
    width: 100px;
    padding: 5px;
    font-size: 1rem;
    text-align: right;
  }
  /* Druckstyles */
  @media print {
    body * {
      visibility: hidden;
    }
    .receipt, .receipt * {
      visibility: visible;
    }
    .receipt {
      position: absolute;
      left: 0;
      top: 0;
      width: 100%;
    }
    .actions, .scanner, .payment-method, .discount-input, h1 {
      display: none;
    }
  }
</style>

<div class="container">
  <h1>Mitarbeiter-Scannen</h1>

  <!-- Barcode Scanner -->
  <div class="scanner">
    <BarcodeScanner bind:value={barcodeInput} on:scan={handleScan} bind:this={barcodeScanner} />
  </div>

  <!-- Rabatt-Eingabe (nur sichtbar, wenn Artikel vorhanden sind) -->
  {#if scannedItems.length > 0}
    <div class="discount-input">
      <label for="discount">Rabatt (EUR): </label>
      <input
        type="number"
        id="discount"
        value={discount}
        min="0"
        step="0.01"
        on:input={(e) => {
          const inputVal = Math.max(0, parseFloat(e.target.value) || 0);
          // Rabatt darf nicht größer als der Bruttobetrag sein
          discount = Math.min(gross, inputVal);
        }}
        on:mouseleave={focusBarcodeInput}
      />
    </div>
  {/if}

  <!-- Quittungsanzeige -->
  <Receipt 
    {scannedItems} 
    {subtotal} 
    {pfand}
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
