<script>
    import Swal from "sweetalert2";
  
    let firstName = "";
    let lastName = "";
    let email = "";
    let password = "";
  
    const handleRegisterm = async () => {
      if (!firstName || !lastName || !email || !password) {
        Swal.fire({
          title: "Fehler",
          text: "Bitte fülle alle Felder aus.",
          icon: "error",
          confirmButtonText: "OK",
        });
        return;
      }
  
      try {
        const response = await fetch("https://cinephoria-backend-c53f94f0a255.herokuapp.com/register", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ vorname, nachname, email, password }),
        });
  
        const data = await response.json();
  
        if (response.ok) {
          Swal.fire({
            title: "Erfolgreich registriert!",
            text: "Du kannst dich jetzt einloggen.",
            icon: "success",
            confirmButtonText: "OK",
          });
          // Felder leeren
          firstName = "";
          lastName = "";
          email = "";
          password = "";
        } else {
          Swal.fire({
            title: "Fehler",
            text: data.error || "Ein Fehler ist aufgetreten.",
            icon: "error",
            confirmButtonText: "OK",
          });
        }
      } catch (error) {
        Swal.fire({
          title: "Fehler",
          text: "Es konnte keine Verbindung zum Server hergestellt werden.",
          icon: "error",
          confirmButtonText: "OK",
        });
      }
    };
  </script>
  
  <style>
    .register-container {
      max-width: 400px;
      margin: 0 auto;
      padding: 2rem;
      background: #ffffff;
      border-radius: 12px;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
  
    .register-container h1 {
      text-align: center;
      margin-bottom: 1.5rem;
    }
  
    .form-group {
      margin-bottom: 1rem;
    }
  
    .form-group label {
      display: block;
      margin-bottom: 0.5rem;
      font-weight: bold;
    }
  
    .form-group input {
      width: 100%;
      padding: 0.8rem;
      border: 1px solid #ccc;
      border-radius: 8px;
      font-size: 1rem;
    }
  
    .form-group input:focus {
      border-color: #1abc9c;
      box-shadow: 0 0 4px rgba(26, 188, 156, 0.5);
      outline: none;
    }
  
    .register-button {
      width: 100%;
      background: #3498db;
      color: #ffffff;
      font-size: 1rem;
      font-weight: bold;
      padding: 0.8rem;
      border: none;
      border-radius: 12px;
      cursor: pointer;
      transition: background-color 0.3s ease;
    }
  
    .register-button:hover {
      background: #24b497;
    }
  </style>
  
  <div class="register-container">
    <h1>Registrieren</h1>
    <div class="form-group">
      <label for="firstName">Vorname</label>
      <input type="text" id="firstName" bind:value={firstName} placeholder="Gib deinen Vornamen ein" />
    </div>
    <div class="form-group">
      <label for="lastName">Nachname</label>
      <input type="text" id="lastName" bind:value={lastName} placeholder="Gib deinen Nachnamen ein" />
    </div>
    <div class="form-group">
      <label for="email">E-Mail</label>
      <input type="email" id="email" bind:value={email} placeholder="Gib deine E-Mail ein" />
    </div>
    <div class="form-group">
      <label for="password">Passwort</label>
      <input type="password" id="password" bind:value={password} placeholder="Gib dein Passwort ein" />
    </div>
    <button class="register-button" on:click={handleRegisterm}>Registrieren</button>
  </div>
  