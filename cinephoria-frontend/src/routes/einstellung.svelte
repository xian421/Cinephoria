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

    
body {
    margin: 0;
    font-family: 'Roboto', sans-serif;
   
    color: #fff;
    overflow-x: hidden;
    max-width: 100%;
}

.settings-container {
    max-width: 1200px;
    margin: 4rem auto;
    padding: 2rem;
  
    border-radius: 12px;
    
    margin-top: 6rem;
}

.settings-header h1 {
    font-size: 3rem;
    margin: 0;
    color: #2ecc71;
    text-shadow: 0 0 20px #2ecc71, 0 0 40px #2ecc71;
    text-align: center;
    animation: glow 2s infinite alternate;
}

@keyframes glow {
  from {
    text-shadow: 0 0 10px #2ecc71, 0 0 20px #2ecc71;
  }
  to {
    text-shadow: 0 0 20px #2ecc71, 0 0 40px #2ecc71;
  }
}

.settings-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-top: 3rem;
}

.setting-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: rgba(0,0,0,0.4);
    padding: 1rem;
    border-radius: 8px;
    box-shadow: 0 0 20px rgba(0,0,0,0.5);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.setting-item:hover {
    transform: translateY(-5px);
    box-shadow: 0 0 25px #2ecc71;
}

.setting-item label {
    font-size: 1.2rem;
    color: #fff;
    cursor: pointer;
    text-shadow: 0 0 5px #fff;
}

.setting-item input[type="checkbox"] {
    width: 20px;
    height: 20px;
    cursor: pointer;
}

.save-button {
    width: 100%;
    padding: 0.8rem;
    font-size: 1.2rem;
    font-weight: bold;
    color: #000;
    background: #2ecc71;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    box-shadow: 0 0 10px #2ecc71;
    margin-top: 2rem;
    text-shadow: 0 0 10px #fff;
    transition: background-color 0.3s ease, transform 0.3s ease, box-shadow 0.3s;
}

.save-button:hover {
    background: #27ae60;
    transform: translateY(-3px) scale(1.05);
    box-shadow: 0 0 15px #27ae60;
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
  