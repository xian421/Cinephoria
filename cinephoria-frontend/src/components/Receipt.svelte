<!-- src/components/Receipt.svelte -->
<script>
    import { createEventDispatcher } from 'svelte';
    import { format } from 'date-fns'; // Optional, falls du Daten formatieren möchtest
  
    const dispatch = createEventDispatcher();
  
    export let scannedItems = [];
    export let subtotal = 0;
    export let tax = 0;
    export let discount = 0;
    export let total = 0;
  
    // Funktion zum Entfernen eines Artikels
    function removeItem(item_id) {
      dispatch('remove', { item_id });
    }
  </script>
  
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
          <div class="receipt-item indent">
            <span>Pfand für {item.name} x{item.quantity}</span>
            <span>{(item.pfandPrice * item.quantity).toFixed(2)} €</span>
          </div>
        {/if}
        <div class="receipt-item">
          <button class="remove-button" on:click={() => removeItem(item.item_id)}>
            Artikel entfernen
          </button>
        </div>
      {/each}
      {#if scannedItems.length === 0}
        <div class="empty">Keine Artikel gescannt.</div>
      {/if}
    </div>
    <div class="totals">
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
        <span>{discount.toFixed(2)} €</span>
      </div>
      <div class="total">
        <span>Gesamt:</span>
        <span>{total.toFixed(2)} €</span>
      </div>
    </div>
  </div>
  
  <style>
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
    .receipt-item.indent {
      margin-left: 20px;
    }
    .receipt-item:last-child {
      border-bottom: none;
    }
    .totals div {
      display: flex;
      justify-content: space-between;
      font-weight: bold;
      font-size: 1.2rem;
      margin-top: 10px;
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
    }
  </style>
  