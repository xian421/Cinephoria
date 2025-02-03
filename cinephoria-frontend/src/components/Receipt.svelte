<!--src/components/Receipt.svelte-->
<script>
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();

  export let scannedItems = [];
  export let subtotal = 0;
  export let pfand = 0;
  export let tax = 0;
  export let discount = 0;
  export let total = 0;

  // Beim Klick auf "Artikel entfernen" wird das Item identifiziert
  function removeItem(item_id) {
    dispatch('remove', { item_id });
  }
</script>

<div class="receipt">
  <!-- Überschrift der Quittung -->
  <div class="receipt-header">
    <h2>Quittung</h2>
  </div>
  
  <!-- Liste der Artikel -->
  <div class="receipt-items">
    {#each scannedItems as item, index}
      <div class="receipt-item">
        <span>{index + 1}. {item.name} x{item.quantity}</span>
        <span>{(item.price * item.quantity).toFixed(2)} EUR</span>
      </div>
      {#if item.pfandPrice > 0}
        <div class="receipt-item indent">
          <span>Pfand: {item.name} x{item.quantity}</span>
          <span>{(item.pfandPrice * item.quantity).toFixed(2)} EUR</span>
        </div>
      {/if}
      <div class="receipt-item remove-item">
        <button class="remove-button" on:click={() => removeItem(item.item_id)}>
          Artikel entfernen
        </button>
      </div>
    {/each}
    {#if scannedItems.length === 0}
      <div class="empty">Keine Artikel gescannt.</div>
    {/if}
  </div>
  
  <!-- Berechnung der Totals -->
  <div class="totals">
    <div class="subtotal">
      <span>Zwischensumme: </span>
      <span>{subtotal.toFixed(2)} EUR</span>
    </div>
    <div class="pfand">
      <span>Pfand: </span>
      <span>{pfand.toFixed(2)} EUR</span>
    </div>
    <div class="tax">
      <span>MwSt. (19%):</span>
      <span>{tax.toFixed(2)} EUR</span>
    </div>
    <div class="discount">
      <span>Rabatt:</span>
      <span>{discount.toFixed(2)} EUR</span>
    </div>
    <div class="total">
      <span>Gesamt:</span>
      <span>{total.toFixed(2)} EUR</span>
    </div>
  </div>
</div>

<style>
  .receipt {
    border: 2px dashed #ccc;
    padding: 20px;
    border-radius: 10px;
    background-color: #f9f9f9;
    max-width: 400px;
    margin: 0 auto;
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
  .receipt-item.indent {
    margin-left: 20px;
    font-style: italic;
  }
  .remove-item {
    justify-content: flex-end;
  }
  .remove-button {
    background-color: transparent;
    border: none;
    color: red;
    cursor: pointer;
    font-size: 0.9rem;
  }
  .remove-button:hover {
    text-decoration: underline;
  }
  .empty {
    text-align: center;
    color: #777;
    padding: 10px 0;
  }
  .totals div {
    display: flex;
    justify-content: space-between;
    font-weight: bold;
    font-size: 1.2rem;
    margin-top: 10px;
  }
  
  /* Druckmodus */
  @media print {
    .receipt {
      font-family: monospace;
      white-space: pre-wrap;
      width: 100%;
    }
    .receipt-header,
    .totals {
      text-align: left;
    }
    .receipt-item {
      display: block;
      margin-bottom: 4px;
    }
    .receipt-item span {
      display: inline-block;
      vertical-align: top;
    }
    .receipt-item span:first-child {
      width: 70%;
    }
    .receipt-item span:last-child {
      width: 30%;
      text-align: right;
    }
    .remove-button {
      display: none;
    }
  }
</style>
