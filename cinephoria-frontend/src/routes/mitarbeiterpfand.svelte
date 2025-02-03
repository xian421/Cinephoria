<script>
    import { get } from 'svelte/store';
    import { authStore } from '../stores/authStore.js';
    import { fetchProductByBarcode } from '../services/api';
  
    let barcodeInput = '';
    let scannedPfandItems = [];
    let errorMessage = '';
  
    // Minimale SVG-Icons (Platzhalter – ersetze sie durch deinen SVG-Code)
    const normalBottleSVG = `...`; // Dein SVG-Code
    const crateSVG = `...`;
    const glassBottleSVG = `...`;
    const cinephoriaCupSVG = `...`;
  
    const pfandIcons = {
      "Flasche": normalBottleSVG,
      "Kiste": crateSVG,
      "Glasflasche": glassBottleSVG,
      "Cinephoria-Becher": cinephoriaCupSVG
      // Weitere Zuordnungen nach Bedarf ...
    };
  
    // Reaktive Berechnung der Gesamtsumme (als Zahl)
    $: totalPfand = scannedPfandItems.reduce(
      (sum, item) => sum + item.quantity * item.amount,
      0
    );
  
    async function handleScan() {
      const barcode = barcodeInput.trim();
      if (!barcode) {
        errorMessage = 'Bitte gib einen Barcode ein.';
        return;
      }
      errorMessage = '';
  
      const token = get(authStore).token;
      try {
        const product = await fetchProductByBarcode(token, barcode);
        if (!product) {
          errorMessage = 'Artikel nicht gefunden.';
          return;
        }
        if (product.pfand_id && product.amount) {
          const amount = parseFloat(product.amount);
          if (isNaN(amount)) {
            errorMessage = 'Ungültiger Pfandbetrag.';
            barcodeInput = '';
            return;
          }
          // Prüfen, ob das Produkt bereits in der Liste vorhanden ist
          const index = scannedPfandItems.findIndex(
            (item) => item.pfand_id === product.pfand_id
          );
          if (index !== -1) {
            // Bestehenden Eintrag aktualisieren
            scannedPfandItems = scannedPfandItems.map((item, i) =>
              i === index ? { ...item, quantity: item.quantity + 1 } : item
            );
          } else {
            // Neues Pfand-Item hinzufügen
            scannedPfandItems = [
              ...scannedPfandItems,
              {
                pfand_id: product.pfand_id,
                pfand_name: product.pfand_name,
                quantity: 1,
                amount: amount
              }
            ];
          }
        } else {
          errorMessage = 'Kein Pfand vorhanden oder Artikel ohne Pfand.';
        }
        barcodeInput = '';
      } catch (error) {
        console.error('Fehler beim Pfand-Scan:', error);
        errorMessage = 'Fehler beim Pfand-Scan oder bei der Verbindung zum Server.';
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
      errorMessage = '';
    }
  
    function getPfandSVG(pfandName) {
      return pfandIcons[pfandName] || `
        <svg viewBox="0 0 48 48" width="24" height="24">
          <circle cx="24" cy="24" r="20" fill="#ccc" />
          <text x="50%" y="55%" fill="#333" font-size="10" text-anchor="middle" font-family="sans-serif">
            Pfand
          </text>
        </svg>
      `;
    }
  
    function handleWeiter() {
      window.print();
    }
  
    /**
     * Formatiert den Bon als Text für den Drucker.
     * (Diese Funktion wird aktuell nicht verwendet, kann aber bei Bedarf eingebunden werden.)
     * @param {Object} bon 
     * @returns {string} Formatierten Bon-String
     */
    function formatBon(bon) {
      let bonText = "Pfandautomat Bon\n";
      bonText += "--------------------------\n";
      bonText += "Artikel:\n";
      bonText += bon.items.map(item => `${item.pfand_name} x${item.quantity}`).join('\n') + '\n';
      bonText += "--------------------------\n";
      bonText += `Summe: ${bon.summe} €\n`;
      bonText += "Danke für deinen Einkauf!\n";
      bonText += `${bon.datum}\n`;
      return bonText;
    }
  </script>
  
  <style>
    .screen-container {
      width: 300px;
      background-color: #fff;
      border: 1px solid #ccc;
      border-radius: 6px;
      overflow: hidden;
      box-shadow: 0 2px 6px rgba(0,0,0,0.2);
      font-family: sans-serif;
      margin: 0 auto;
      padding: 20px;
    }
  
    .header-bar {
      background-color: #333;
      color: #fff;
      padding: 8px;
      text-align: center;
      font-size: 0.9rem;
      border-radius: 4px 4px 0 0;
    }
  
    .content {
      padding: 10px 15px;
    }
  
    .scan-area {
      display: flex;
      flex-direction: column;
      gap: 10px;
      margin-bottom: 20px;
    }
  
    .scan-area input {
      padding: 8px;
      font-size: 1rem;
      border: 1px solid #ccc;
      border-radius: 5px;
      text-align: center;
    }
  
    .scan-area button {
      padding: 10px;
      font-size: 1rem;
      background-color: #007bff;
      color: #fff;
      border: none;
      border-radius: 5px;
      cursor: pointer;
      text-transform: uppercase;
      font-weight: bold;
    }
  
    .scan-area button:hover {
      background-color: #0056b3;
    }
  
    .error {
      margin-bottom: 10px;
      color: #f66;
      font-weight: bold;
      text-align: center;
    }
  
    .pfand-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 6px;
      padding: 5px 0;
      border-bottom: 1px solid #eee;
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
      width: 24px;
      height: 24px;
    }
  
    .pfand-description {
      font-size: 0.9rem;
    }
  
    .price {
      font-weight: bold;
      font-size: 0.95rem;
    }
  
    .divider {
      border-top: 1px solid #ccc;
      margin: 10px 0;
    }
  
    .total {
      text-align: right;
      font-size: 1.2rem;
      font-weight: bold;
      margin-bottom: 10px;
    }
  
    .total span {
      color: #333;
    }
  
    .big-button {
      display: block;
      width: 100%;
      padding: 12px;
      background-color: #28a745;
      color: #fff;
      border: none;
      font-size: 1rem;
      font-weight: bold;
      text-align: center;
      border-radius: 4px;
      cursor: pointer;
      text-transform: uppercase;
    }
  
    .big-button:hover {
      background-color: #218838;
    }
  
    @media print {
      body * {
        display: none !important;
      }
      #print-section, 
      #print-section * {
        display: block !important;
      }
      #print-section {
        position: static;
        width: 58mm;
        margin: 0 auto;
        padding: 0;
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
  
  <div class="screen-container">
    <div class="header-bar">
      Bitte leere Behälter einführen ...
    </div>
    <div class="content">
      {#if errorMessage}
        <div class="error">{errorMessage}</div>
      {/if}
  
      <!-- Scan-Bereich -->
      <div class="scan-area">
        <input
          type="text"
          placeholder="Barcode eingeben"
          bind:value={barcodeInput}
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
            {(item.amount * item.quantity).toFixed(2)} €
          </div>
        </div>
      {/each}
  
      <!-- Gesamtsumme und Bon-Druck -->
      {#if scannedPfandItems.length > 0}
        <div class="divider"></div>
        <div class="total">
          Summe: <span>{totalPfand.toFixed(2)} €</span>
        </div>
        <button class="big-button" on:click={handleWeiter}>
          Bon drucken
        </button>
      {/if}
    </div>
  </div>
  
  <!-- Druckbereich -->
  <div id="print-section">
    <h2 style="text-align: center; margin-bottom: 5px;">Pfandautomat Bon</h2>
    <hr style="margin: 5px 0;" />
    <p><strong>Datum:</strong> {new Date().toLocaleString()}</p>
    <h3 style="margin-bottom: 5px;">Artikel:</h3>
    <ul style="list-style: none; padding: 0; margin: 0;">
      {#each scannedPfandItems as item}
        <li style="margin-bottom: 3px; display: flex; justify-content: space-between;">
          <span>{item.pfand_name} x{item.quantity}</span>
          <span>{(item.amount * item.quantity).toFixed(2)} €</span>
        </li>
      {/each}
    </ul>
    <hr style="margin: 5px 0;" />
    <p><strong>Summe:</strong> {totalPfand.toFixed(2)} €</p>
    <p style="text-align: center; margin-top: 10px;">Danke für deinen Einkauf!</p>
  </div>
  