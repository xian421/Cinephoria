<script>
    let email = "";
    let password = "";
  
    const handleLogin = () => {
      if (email && password) {
        alert(`Erfolgreich eingeloggt als: ${email}`);
      } else {
        alert("Bitte E-Mail und Passwort eingeben!");
      }
    };
  </script>
  
  <main>
    <h1>Willkommen bei Cinephoria - Login</h1>
  
    <!-- Login-Box -->
    <section class="login-container">
      <form on:submit|preventDefault={handleLogin}>
        <input
          type="email"
          class="login-input"
          placeholder="E-Mail"
          bind:value={email}
        />
        <input
          type="password"
          class="login-input"
          placeholder="Passwort"
          bind:value={password}
        />
        <button type="submit" class="login-button">Einloggen</button>
      </form>
      <p class="login-footer">
        Noch kein Konto? <a href="/register">Registrieren</a>
      </p>
    </section>
  </main>
  
  <style>
    /* Allgemeine Styles */
    :global(body) {
      margin: 0;
      font-family: Arial, sans-serif;
      background-color: #eeeded;
      box-shadow: #333;
    }
  
    main {
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      min-height: 100vh; /* Höhe: gesamte Bildschirmhöhe */
      width: 100%;
      background-color: #eeeded;
      padding: 20px;
    }
  
    h1 {
      text-align: center;
      margin-bottom: 20px;
      font-size: 2rem;
      color: #333;
    }
  
    /* Login-Container */
    .login-container {
      background-color: #ffffff;
      padding: 30px;
      border-radius: 12px;
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
      width: 100%;
      max-width: 600px; /* Maximale Breite */
    }
  
    .login-input {
      width: 100%;
      padding: 1rem;
      margin: 10px 0;
      border: 1px solid #ccc;
      border-radius: 8px;
      box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
      font-size: 1rem;
    }
  
    .login-input:focus {
      outline: none;
      border-color: #1abc9c;
      box-shadow: 0 0 4px rgba(26, 188, 156, 0.5);
    }
  
    .login-button {
      font-size: 1.2rem;
      font-weight: bold;
      color: #fff;
      background: #3498db;
      border: none;
      border-radius: 12px;
      padding: 1rem 1.5rem;
      margin-top: 1rem;
      cursor: pointer;
      transition: all 0.3s ease;
      width: 100%;
    }
  
    .login-button:hover {
      background: #1abc9c;
      transform: scale(1.05);
    }
  
    .login-footer {
      margin-top: 1rem;
      font-size: 0.9rem;
      text-align: center;
    }
  
    .login-footer a {
      text-decoration: none;
      color: #3498db;
      font-weight: bold;
      cursor: pointer;
    }
  
    .login-footer a:hover {
      color: #1abc9c;
    }
  </style>
  