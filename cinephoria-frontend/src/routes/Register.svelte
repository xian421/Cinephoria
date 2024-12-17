<script>
  import Swal from "sweetalert2";

  let firstName = "";
  let lastName = "";
  let email = "";
  let password = "";

  const handleRegister = async () => {
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
    max-width: 500px;
    margin: 2rem auto;
    padding: 2rem;
    background: #fdfdfd;
    border-radius: 20px;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    text-align: center;
    font-family: "Roboto", sans-serif;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
  }

  .register-container:hover {
    transform: translateY(-10px);
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.2);
  }

  .register-container h1 {
    font-size: 2rem;
    color: #3498db;
    margin-bottom: 1.5rem;
  }

  .form-group {
    margin-bottom: 1.2rem;
  }

  .form-group input {
    width: 100%;
    padding: 0.8rem;
    border: 2px solid #ddd;
    border-radius: 12px;
    font-size: 1rem;
    color: #333;
    background-color: #f9f9f9;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
  }

  .form-group input:focus {
    border-color: #3498db;
    box-shadow: 0 0 8px rgba(52, 152, 219, 0.5);
    outline: none;
  }

  .register-button {
    width: 100%;
    padding: 0.8rem;
    font-size: 1.2rem;
    font-weight: bold;
    color: #ffffff;
    background: linear-gradient(145deg, #3498db, #2980b9);
    border: none;
    border-radius: 12px;
    cursor: pointer;
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
    transition: background 0.3s ease, transform 0.3s ease;
  }

  .register-button:hover {
    background: linear-gradient(145deg, #2980b9, #1abc9c);
    transform: scale(1.05);
  }

  .register-button:active {
    transform: scale(0.98);
  }

  .register-footer {
    margin-top: 1rem;
    font-size: 0.9rem;
    color: #555;
  }

  .register-footer a {
    color: #3498db;
    text-decoration: none;
    transition: color 0.3s ease;
  }

  .register-footer a:hover {
    color: #1abc9c;
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
  <button class="register-button" on:click={handleRegister}>Registrieren</button>

  <div class="register-footer">
    <p>Hast du bereits ein Konto? <a href="/login">Hier einloggen</a></p>
  </div>
</div>
