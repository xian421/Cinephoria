<script>
    let settings = {
      notifications: true,
      darkMode: false,
      emailUpdates: true,
    };
  
    const saveSettings = () => {
      console.log("Einstellungen gespeichert:", settings);
      alert("Einstellungen erfolgreich gespeichert!");
    };
  </script>
  
  <style>
    /* Gesamtcontainer */
    .settings-container {
      max-width: 800px;
      margin: 2rem auto;
      padding: 2rem;
      background: linear-gradient(145deg, #ffffff, #f8f9fa);
      border-radius: 12px;
      box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
      font-family: Arial, sans-serif;
    }
  
    /* Überschrift */
    .settings-header {
      text-align: center;
      margin-bottom: 2rem;
    }
  
    .settings-header h1 {
      font-size: 2rem;
      color: #333;
      margin: 0;
    }
  
    /* Einstellungen-Liste */
    .settings-list {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }
  
    .setting-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: #ffffff;
      padding: 1rem;
      border-radius: 8px;
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
  
    .setting-item label {
      font-size: 1.2rem;
      color: #555;
      cursor: pointer;
    }
  
    .setting-item input[type="checkbox"] {
      width: 20px;
      height: 20px;
      cursor: pointer;
    }
  
    /* Speicher-Button */
    .save-button {
      width: 100%;
      padding: 0.8rem;
      font-size: 1.2rem;
      font-weight: bold;
      color: #fff;
      background: #3498db;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      transition: background 0.3s ease, transform 0.2s ease;
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
      margin-top: 2rem;
    }
  
    .save-button:hover {
      background: #24b497;
    }
  
    .save-button:active {
      transform: scale(0.98);
    }
  </style>
  
  <div class="settings-container">
    <!-- Header -->
    <div class="settings-header">
      <h1>Einstellungen</h1>
    </div>
  
    <!-- Einstellungen-Liste -->
    <div class="settings-list">
      <div class="setting-item">
        <label for="notifications">Benachrichtigungen aktivieren</label>
        <input
          type="checkbox"
          id="notifications"
          bind:checked={settings.notifications}
        />
      </div>
      <div class="setting-item">
        <label for="darkMode">Dunkelmodus aktivieren</label>
        <input type="checkbox" id="darkMode" bind:checked={settings.darkMode} />
      </div>
      <div class="setting-item">
        <label for="emailUpdates">E-Mail-Updates erhalten</label>
        <input
          type="checkbox"
          id="emailUpdates"
          bind:checked={settings.emailUpdates}
        />
      </div>
    </div>
  
    <!-- Speicher-Button -->
    <button class="save-button" on:click={saveSettings}>Einstellungen speichern</button>
  </div>
  