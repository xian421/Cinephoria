<!-- src/routes/checkout.svelte -->
<script lang="ts">
  import { onMount } from 'svelte';
  import { get } from 'svelte/store';
  import Swal from 'sweetalert2';
  import { navigate } from 'svelte-routing';

  import { authStore } from '../stores/authStore';
  import { cart, validUntil, clearCart, loadCart } from '../stores/cartStore';
  import { createBookingNew } from '../services/api.js'; // Importiere die Funktion

  // Platzhalter für Backend-Logik:
  // Wenn der Nutzer eingeloggt ist, können diese Daten aus dem Profil vorausgefüllt werden.
  let firstName = '';
  let lastName = '';
  let email = '';
  let emailRepeat = '';

  // Reaktive Berechnung des Gesamtpreises unter Berücksichtigung der Rabatte
  let totalPrice = 0;

  // Verwende eine reaktive Anweisung, um totalPrice automatisch zu aktualisieren
  $: totalPrice = $cart.reduce((sum, seat) => {
    let discount = 0;

    if (seat.selectedDiscount) {
      const { discount_amount, discount_percentage } = seat.selectedDiscount;

      if (discount_amount != null) {
        discount = discount_amount;
      } else if (discount_percentage != null) {
        discount = seat.price * (discount_percentage / 100);
      }
    }

    return sum + (seat.price - discount);
  }, 0);

  // Überprüfung, ob der Nutzer eingeloggt ist (Platzhalter)
  $: {
      const user = get(authStore);
      if (user.isLoggedIn) {
          // Diese Werte sollten dann aus dem Profil geholt werden.
          firstName = user.userFirstName || 'Max';
          lastName = user.userLastName || 'Mustermann';
          email = user.email || 'max.mustermann@example.com';
          emailRepeat = email;
      }
  }

  // Lade den Warenkorb beim Mounten der Komponente
  onMount(() => {
      loadCart();
      console.log($cart);
  });

  function validateForm() {
      if (!firstName || !lastName || !email || !emailRepeat) {
          Swal.fire({
              title: "Fehler",
              text: "Bitte alle Felder ausfüllen.",
              icon: "error",
              confirmButtonText: "OK"
          });
          return false;
      }

      if (email !== emailRepeat) {
          Swal.fire({
              title: "Fehler",
              text: "Die E-Mail-Adressen stimmen nicht überein.",
              icon: "error",
              confirmButtonText: "OK"
          });
          return false;
      }

      // Weitere Validierungen (z. B. E-Mail-Format) können hier erfolgen.
      return true;
  }

  async function proceedPayment() {
      if (!validateForm()) return;

      // Zeige eine Bestätigungs-Popup für die Zahlung
      Swal.fire({
          title: "Zahlung bestätigen",
          text: "Bist du sicher, dass du den Kauf abschließen möchtest?",
          icon: "question",
          showCancelButton: true,
          confirmButtonText: "Ja",
          cancelButtonText: "Abbrechen"
      }).then(async (result) => {
          if (result.isConfirmed) {
              try {
                  // Simuliere die Generierung einer PayPal-Order-ID
                  // In einer echten Anwendung würdest du hier die PayPal-API aufrufen
                  const paypal_order_id = 'ORDER_' + Date.now();

                  // Sammle die notwendigen Daten
                  const user = get(authStore);
                  const user_id = user.isLoggedIn ? user.userId : null;

                  const cart_items = $cart.map(item => ({
                      seat_id: item.seat_id,
                      showtime_id: item.showtime_id,
                      seat_type_discount_id: item.seat_type_discount_id
                  }));

                  // Rufe die Backend-API auf, um die Buchung zu erstellen
                  const bookingResponse = await createBookingNew(
                      firstName,
                      lastName,
                      email,
                      user_id,
                      totalPrice,
                      paypal_order_id,
                      cart_items
                  );

                  // Zeige eine Erfolgsmeldung an
                  Swal.fire({
                      title: "Erfolg",
                      text: `Buchung erfolgreich angelegt! Deine Buchungs-ID: ${bookingResponse.booking_id}`,
                      icon: "success",
                      confirmButtonText: "OK"
                  }).then(() => {
                      // Leere den Warenkorb oder führe weitere Aktionen durch
                      clearCart();
                      navigate('/bestellung-erfolgreich');
                  });
              } catch (error) {
                  // Fehlerbehandlung
                  Swal.fire({
                      title: "Fehler",
                      text: error.message || "Es ist ein Fehler aufgetreten.",
                      icon: "error",
                      confirmButtonText: "OK"
                  });
              }
          }
      });
  }
</script>

<div class="background">
  <header class="header-section">
      <h1 class="header-text">CINEPHORIA - Checkout</h1>
      <p class="tagline">Fast am Ziel! Bitte überprüfe deine Daten.</p>
  </header>

  <main class="checkout-container">
      <h2>Deine Daten</h2>
      <form class="checkout-form" on:submit|preventDefault={proceedPayment}>
          <div class="form-group">
              <label for="firstname">Vorname</label>
              <input type="text" id="firstname" bind:value={firstName} placeholder="Vorname" />
          </div>

          <div class="form-group">
              <label for="lastname">Nachname</label>
              <input type="text" id="lastname" bind:value={lastName} placeholder="Nachname" />
          </div>

          <div class="form-group">
              <label for="email">E-Mail</label>
              <input type="email" id="email" bind:value={email} placeholder="Deine E-Mail" />
          </div>

          <div class="form-group">
              <label for="emailRepeat">E-Mail Wiederholung</label>
              <input type="email" id="emailRepeat" bind:value={emailRepeat} placeholder="E-Mail wiederholen" />
          </div>

          <h2>Gesamtpreis: {totalPrice.toFixed(2)} €</h2>

          <!-- Platzhalter für den PayPal-Button oder andere Zahlungsmethoden -->
          <div class="payment-section">
              <p>Wähle deine Zahlungsmethode:</p>
              <div class="paypal-placeholder">
                  <!-- Hier später PayPal-Buttons einbinden -->
                  <i class="fab fa-paypal fa-3x"></i>
                  <p>(PayPal-Button kommt hier hin)</p>
              </div>
          </div>

          <div class="button-group">
              <button class="back-btn" type="button" on:click={() => navigate('/warenkorb')}>
                  <i class="fas fa-arrow-left"></i> Zurück zum Warenkorb
              </button>
              <button class="proceed-btn" type="submit">
                  <i class="fas fa-check"></i> Zahlung abschließen
              </button>
          </div>
      </form>
  </main>
</div>

<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

.background {
position: relative;
min-height: 100vh;
padding: 2rem;
overflow: hidden;
}

.header-section {
text-align: center;
margin-top: 4rem;
}

.header-text {
font-size: 3rem;
margin: 0;
color: #2ecc71;
text-shadow: 0 0 20px #2ecc71, 0 0 40px #2ecc71;
animation: glow 2s infinite alternate;
}

.tagline {
font-size: 1.5rem;
color: #fff;
margin-top: 1rem;
text-shadow: 0 0 10px #fff;
}

@keyframes glow {
from {
  text-shadow: 0 0 10px #2ecc71, 0 0 20px #2ecc71;
}
to {
  text-shadow: 0 0 20px #2ecc71, 0 0 40px #2ecc71;
}
}

.checkout-container {
margin: 2rem auto;
padding: 2rem;
max-width: 800px;
background: rgba(0,0,0,0.4);
border: 1px solid #2ecc71;
border-radius: 20px;
box-shadow: 0 0 15px rgba(0,0,0,0.5);
color: #fff;
text-align: center;
}

.checkout-container h2 {
color: #2ecc71;
text-shadow: 0 0 10px #2ecc71;
margin-bottom: 2rem;
}

.checkout-form {
display: flex;
flex-direction: column;
gap: 1.5rem;
width: 100%;
}

.form-group {
display: flex;
flex-direction: column;
align-items: flex-start;
margin: 0 auto;
max-width: 400px;
width: 100%;
color: #fff;
}

.form-group label {
margin-bottom: 0.5rem;
font-weight: bold;
}

.form-group input {
width: 100%;
padding: 0.7rem;
border-radius: 10px;
border: none;
background: rgba(0,0,0,0.5);
color: #fff;
box-shadow: 0 0 5px #2ecc71 inset;
}

.form-group input::placeholder {
color: #ccc;
}

.payment-section {
margin-top: 2rem;
}

.payment-section p {
margin-bottom: 1rem;
font-weight: bold;
color: #2ecc71;
text-shadow: 0 0 5px #2ecc71;
}

.paypal-placeholder {
background: rgba(0,0,0,0.5);
border: 1px solid #2ecc71;
border-radius: 16px;
padding: 1.5rem;
box-shadow: 0 0 15px rgba(0,0,0,0.5);
display: flex;
flex-direction: column;
align-items: center;
gap: 0.5rem;
color: #fff;
}

.paypal-placeholder i {
color: #2ecc71;
text-shadow: 0 0 5px #2ecc71;
}

.button-group {
display: flex;
justify-content: center;
gap: 1rem;
margin-top: 2rem;
}

.back-btn, .proceed-btn {
font-size: 1rem;
font-weight: bold;
border: none;
border-radius: 10px;
padding: 0.7rem 1.2rem;
cursor: pointer;
transition: transform 0.3s ease;
background-color: #2ecc71;
color: #000;
box-shadow: 0 0 10px #2ecc71;
}

.back-btn:hover, .proceed-btn:hover {
transform: translateY(-3px) scale(1.05);
opacity: 0.9;
}

@media (max-width: 600px) {
.form-group {
  max-width: 100%;
}

.checkout-container {
  padding: 1rem;
}

.payment-section p {
  font-size: 1rem;
}
}
</style>
