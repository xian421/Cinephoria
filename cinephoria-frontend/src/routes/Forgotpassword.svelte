<script>
    import Swal from "sweetalert2";
  
    let email = "";
  
    const handleForgotPassword = async () => {
      if (!email) {
        Swal.fire({
          title: "Fehler",
          text: "Bitte gib deine E-Mail-Adresse ein.",
          icon: "error",
          confirmButtonText: "OK",
        });
        return;
      }
  
      try {
        const response = await fetch("https://cinephoria-backend-c53f94f0a255.herokuapp.com/forgot-password", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ email }),
        });
  
        const data = await response.json();
  
        if (response.ok) {
          Swal.fire({
            title: "E-Mail gesendet!",
            text: "Falls die E-Mail existiert, erhältst du in Kürze Anweisungen zum Zurücksetzen des Passworts.",
            icon: "success",
            confirmButtonText: "OK",
          });
          email = ""; // Eingabefeld leeren
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
    .forgot-password-container {
      max-width: 400px;
      margin: 0 auto;
      padding: 2rem;
      background: #ffffff;
      border-radius: 12px;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      background: linear-gradient(145deg, #f8f9fa, #e9ecef);
    }
  
    .forgot-password-container h1 {
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
  
    .forgot-password-button {
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
  
    .forgot-password-button:hover {
      background: linear-gradient(145deg, #2980b9, #1abc9c);
    }
  </style>
  
  <div class="forgot-password-container">
    <h1>Passwort vergessen</h1>
    <div class="form-group">
      <input type="email" id="email" bind:value={email} placeholder="E-Mail-Adresse" />
    </div>
    <button class="forgot-password-button" on:click={handleForgotPassword}>
      Link zum Zurücksetzen senden
    </button>
  </div>
  