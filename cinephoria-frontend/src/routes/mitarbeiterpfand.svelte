<!--src/routes/mitarbeiterpfand.svelte-->
<script>
    import { onMount } from 'svelte';
    import { scanPfandItem, addOrUpdatePfandItem, calculateTotalPfand } from '../services/pfandService.js';
    import { getPfandSVG } from '../utils/pfandUtils.js';
    import { showSuccessToast, showErrorToast } from '../utils/notifications.js';
    
    let barcodeInput = '';
    let scannedPfandItems = [];
    let inputEl; // Referenz für das Barcode-Eingabefeld
    
    // Reaktive Berechnung der Gesamtsumme
    $: totalPfand = calculateTotalPfand(scannedPfandItems);
    
    // Beim Mount wird der Fokus auf das Eingabefeld gesetzt
    onMount(() => {
      inputEl.focus();
    });
    
    async function handleScan() {
      const barcode = barcodeInput.trim();
      if (!barcode) {
        showErrorToast('Bitte gib einen Barcode ein.');
        return;
      }
      try {
        const pfandItem = await scanPfandItem(barcode);
        scannedPfandItems = addOrUpdatePfandItem(scannedPfandItems, pfandItem);
        barcodeInput = '';
        inputEl.focus();
        showSuccessToast('Pfand erfolgreich gescannt!');
      } catch (err) {
        showErrorToast(err.message);
        barcodeInput = '';
        inputEl.focus();
      }
    }
    
    function handleEnter(e) {
      if (e.key === 'Enter') {
        handleScan();
      }
    }
    
    function resetAll() {
      scannedPfandItems = [];
      barcodeInput = '';
      inputEl.focus();
    }
    
    function handleWeiter() {
      window.print();
    }
  </script>
  
  <style>
    /* Normale Ansicht */
    .screen-container {
      width: 320px;
      margin: 20px auto;
      background: #f4f4f4;
      border: 2px solid #333;
      border-radius: 10px;
      box-shadow: 0 4px 8px rgba(0,0,0,0.3);
      font-family: 'Arial', sans-serif;
      overflow: hidden;
    }
    
    .header-bar {
      background-color: #333;
      color: #fff;
      padding: 12px;
      text-align: center;
      font-size: 1.1rem;
      font-weight: bold;
    }
    
    .content {
      padding: 15px;
    }
    
    .scan-area {
      display: flex;
      flex-direction: column;
      gap: 10px;
      margin-bottom: 20px;
    }
    
    .scan-area input {
      padding: 10px;
      font-size: 1.1rem;
      border: 2px solid #333;
      border-radius: 5px;
      text-align: center;
    }
    
    .scan-area input:focus {
      outline: none;
      border-color: #007bff;
      box-shadow: 0 0 5px rgba(0,123,255,0.5);
    }
    
    .scan-area button {
      padding: 12px;
      font-size: 1.1rem;
      background-color: #007bff;
      color: #fff;
      border: none;
      border-radius: 5px;
      cursor: pointer;
      text-transform: uppercase;
      font-weight: bold;
      transition: background-color 0.3s;
    }
    
    .scan-area button:hover {
      background-color: #0056b3;
    }
    
    .pfand-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 0;
      border-bottom: 1px solid #ddd;
    }
    
    .pfand-item:last-child {
      border-bottom: none;
    }
    
    .pfand-info {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    
    .pfand-icon {
      width: 28px;
      height: 28px;
    }
    
    .pfand-description {
      font-size: 1rem;
      font-weight: bold;
    }
    
    .price {
      font-size: 1.1rem;
      font-weight: bold;
      color: #333;
    }
    
    .divider {
      border-top: 2px solid #333;
      margin: 15px 0;
    }
    
    .total {
      text-align: right;
      font-size: 1.3rem;
      font-weight: bold;
      margin-bottom: 15px;
    }
    
    .total span {
      color: #007bff;
    }
    
    .big-button {
      display: block;
      width: 100%;
      padding: 15px;
      background-color: #28a745;
      color: #fff;
      border: none;
      font-size: 1.1rem;
      font-weight: bold;
      text-align: center;
      border-radius: 5px;
      cursor: pointer;
      text-transform: uppercase;
      transition: background-color 0.3s;
    }
    
    .big-button:hover {
      background-color: #218838;
    }
    
    /* Druckbereich: Normale Ansicht ausblenden */
    @media print {
      .screen-container {
        display: none !important;
      }
      /* Nur den Bon-Bereich anzeigen */
      #print-section,
      #print-section * {
        display: block !important;
      }
      #print-section {
        position: static;
        width: 58mm; /* Bonbreite */
        margin: 0 auto;
        padding: 10px;
        box-sizing: border-box;
        font-family: Arial, sans-serif;
        font-size: 12pt;
        background: #fff;
      }
      @page {
        margin: 0;
      }
    }
  </style>
  
  <!-- Normale Ansicht -->
  <div class="screen-container">
    <div class="header-bar">
      Bitte leere Behälter einführen ...
    </div>
    <div class="content">
      <!-- Scan-Bereich -->
      <div class="scan-area">
        <input
          type="text"
          placeholder="Barcode eingeben"
          bind:value={barcodeInput}
          bind:this={inputEl}
          on:keydown={handleEnter}
        />
        <button on:click={handleScan}>Scannen</button>
      </div>
    
      <!-- Liste der Pfand-Artikel -->
      {#each scannedPfandItems as item}
        <div class="pfand-item">
          <div class="pfand-info">
            <div class="pfand-icon">{@html getPfandSVG(item.pfand_name)}</div>
            <div class="pfand-description">
              {item.pfand_name} x{item.quantity}
            </div>
          </div>
          <div class="price">
            {(item.amount * item.quantity).toFixed(2)} EUR
          </div>
        </div>
      {/each}
    
      {#if scannedPfandItems.length > 0}
        <div class="divider"></div>
        <div class="total">
          Summe: <span>{totalPfand.toFixed(2)} EUR</span>
        </div>
        <button class="big-button" on:click={handleWeiter}>Bon drucken</button>
      {/if}
    </div>
  </div>
    
  <!-- Druckbereich: Nur der Pfandbon -->
  <div id="print-section">
    <h2 style="text-align: center; margin-bottom: 5px;">Pfandautomat Bon</h2>
    <hr style="margin: 5px 0;" />
    <p><strong>Datum:</strong> {new Date().toLocaleString()}</p>
    <h3 style="margin-bottom: 5px;">Artikel:</h3>
    <ul style="list-style: none; padding: 0; margin: 0;">
      {#each scannedPfandItems as item}
        <li style="margin-bottom: 3px; display: flex; justify-content: space-between;">
          <span>{item.pfand_name} x{item.quantity}</span>
          <span>{(item.amount * item.quantity).toFixed(2)} EUR</span>
        </li>
      {/each}
    </ul>
    <hr style="margin: 5px 0;" />
    <p><strong>Summe:</strong> {totalPfand.toFixed(2)} EUR</p>
    <p style="text-align: center; margin-top: 10px;">Hier im Supermarkt Pfand gutschreiben lassen!</p>
  </div>
  