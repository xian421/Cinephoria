<!-- src/routes/Register.svelte -->
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
        body: JSON.stringify({ first_name: firstName, last_name: lastName, email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        Swal.fire({
          title: "Erfolgreich registriert!",
          text: "Du kannst dich jetzt einloggen.",
          icon: "success",
          confirmButtonText: "OK",
        });
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
    margin: 2rem auto;
    padding: 2rem;
    background: linear-gradient(145deg, #f8f9fa, #e9ecef);
    border-radius: 12px;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
    text-align: center;
    font-family: Arial, sans-serif;
    text-align: center;
  }

  .register-container h1 {
    font-size: 1.8rem;
    color: #333;
    margin-bottom: 1.5rem;
    font-weight: bold;
  }

  .form-group {
    margin-bottom: 1.2rem;
  }

  .form-group input {
    width: 100%;
    padding: 0.9rem;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 1rem;
    color: #555;
    background: #f8f9fa;
    transition: all 0.3s ease;
  }

  .form-group input:focus {
    border-color: #1abc9c;
    box-shadow: 0 0 8px rgba(26, 188, 156, 0.5);
    outline: none;
    background: #ffffff;
  }

  .register-button {
    width: 100%;
    padding: 0.9rem;
    font-size: 1.2rem;
    font-weight: bold;
    color: #fff;
    background: linear-gradient(145deg, #3498db, #2980b9);
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.3s ease, transform 0.2s ease;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }

  .register-button:hover {
    background: linear-gradient(145deg, #2980b9, #1abc9c);
  }

  .register-button:active {
    transform: scale(0.98);
  }

  .register-button:disabled {
    background: #ccc;
    cursor: not-allowed;
    box-shadow: none;
  }

  @media (max-width: 480px) {
    .register-container {
      padding: 1.5rem;
    }

    .register-container h1 {
      font-size: 1.5rem;
    }

    .form-group input {
      font-size: 0.9rem;
    }

    .register-button {
      font-size: 1rem;
      padding: 0.8rem;
    }
  }
</style>

<div class="register-container">
  <h1>Registrieren</h1>
  <div class="form-group">
    <input type="text" id="firstName" bind:value={firstName} placeholder="Vorname" />
  </div>
  <div class="form-group">
    <input type="text" id="lastName" bind:value={lastName} placeholder="Nachname" />
  </div>
  <div class="form-group">
    <input type="email" id="email" bind:value={email} placeholder="E-Mail" />
  </div>
  <div class="form-group">
    <input type="password" id="password" bind:value={password} placeholder="Passwort" />
  </div>
  <button class="register-button" on:click={handleRegisterm}>Registrieren</button>
</div>
