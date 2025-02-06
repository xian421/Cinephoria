<!-- src/Checkout.svelte -->
<script lang="ts">
    import { onMount } from 'svelte';
    import { get } from 'svelte/store';
    import { navigate } from 'svelte-routing';

    import { authStore } from '../stores/authStore';
    import { cart, clearCart, loadCart } from '../stores/cartStore';

    import { createPayPalOrder, capturePayPalOrder } from '../services/api.js';

    // Statt Swal direkt, importiere deine zentralen Notifications-Funktionen:
    import {
        showErrorAlert,
        showSuccessAlert,
        showCustomAlert
    } from '../utils/notifications.js';

    let firstName = '';
    let lastName = '';
    let email = '';
    let emailRepeat = '';

    let totalPrice = 0;
    let paypalLoaded = false;
    let paypalContainer: HTMLElement | null = null; // Für das PayPal-Button-Container-DIV

    // Beim Laden: Warenkorb laden & PayPal-SDK rein
    onMount(async () => {
        loadCart();
        try {
            await loadPayPalScript();
            if (paypalContainer) {
                initializePayPalButton(paypalContainer);
            }
        } catch (error: any) {
            console.error(error);
            showErrorAlert(error.message || "PayPal SDK konnte nicht geladen werden.");
        }
    });

    // Reaktiver Gesamtpreis
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

    // Userdaten vorbelegen
    $: {
        const user = get(authStore);
        if (user.isLoggedIn) {
            firstName = user.userFirstName ?? 'Max';
            lastName  = user.userLastName  ?? 'Mustermann';
            email     = user.email         ?? 'max.mustermann@example.com';
            emailRepeat = email;
        }
    }

    // (A) Validierung
    function validateForm() {
        if (!firstName || !lastName || !email || !emailRepeat) {
            showErrorAlert("Bitte alle Felder ausfüllen.");
            return false;
        }
        if (email !== emailRepeat) {
            showErrorAlert("Die E-Mail-Adressen stimmen nicht überein.");
            return false;
        }
        return true;
    }

    // (B) PayPal-SDK laden
    function loadPayPalScript(): Promise<void> {
        return new Promise((resolve, reject) => {
            const existingScript = document.querySelector(`script[src*="paypal.com/sdk/js"]`);
            if (existingScript) {
                if (window.paypal) {
                    paypalLoaded = true;
                    resolve();
                } else {
                    const interval = setInterval(() => {
                        if (window.paypal) {
                            clearInterval(interval);
                            paypalLoaded = true;
                            resolve();
                        }
                    }, 100);
                    // Timeout
                    setTimeout(() => {
                        clearInterval(interval);
                        reject(new Error("PayPal SDK konnte nicht geladen werden."));
                    }, 10000);
                }
                return;
            }

            // Neues Script-Tag anlegen
            const script = document.createElement('script');
            script.src = "https://www.paypal.com/sdk/js?client-id=AXWfRwPPgPCoOBZzqI-r4gce1HuWZXDnFqUdES0bP8boKSv5KkkPvZrMFwcCDShXjC3aTdChUjOhwxhW&currency=EUR";
            script.onload = () => {
                paypalLoaded = true;
                resolve();
            };
            script.onerror = () => {
                reject(new Error("PayPal SDK konnte nicht geladen werden."));
            };
            document.body.appendChild(script);
        });
    }

    // (C) PayPal-Button
    function initializePayPalButton(container: HTMLElement) {
        if (!window.paypal) {
            console.error('PayPal SDK nicht geladen');
            return;
        }

        window.paypal.Buttons({
            createOrder: async (data, actions) => {
                if (!validateForm()) {
                    throw new Error("Formular ungültig");
                }
                try {
                    const response = await createPayPalOrder(totalPrice);
                    return response.orderID;
                } catch (e: any) {
                    console.error("Fehler bei createPayPalOrder:", e);
                    showErrorAlert("PayPal-Order konnte nicht erstellt werden.");
                    throw e;
                }
            },
            onApprove: async (data, actions) => {
                const { orderID } = data;
                try {
                    const token = get(authStore).token;

                    const cart_items = $cart.map(item => ({
                        seat_id: item.seat_id,
                        showtime_id: item.showtime_id,
                        seat_type_discount_id: item.seat_type_discount_id
                    }));

                    const captureResp = await capturePayPalOrder(
                        orderID,
                        firstName,
                        lastName,
                        email,
                        token,
                        totalPrice,
                        cart_items
                    );

                    if (captureResp.error) {
                        throw new Error(captureResp.error);
                    }

                    const qrToken = captureResp.qr_token;

                    // Erfolgsmeldung + .then
                    showSuccessAlert("Buchung erfolgreich angelegt!")
                        .then(() => {
                            clearCart();
                            navigate(`/ticketanzeige/${qrToken}`);
                        });

                } catch (err: any) {
                    console.error("Fehler onApprove:", err);
                    showErrorAlert(err.message || "Zahlung oder Buchung fehlgeschlagen.");
                }
            },
            onCancel: (data) => {
                showCustomAlert("Abgebrochen", "Die PayPal-Zahlung wurde abgebrochen.", "info");
            },
            onError: (err) => {
                console.error("PayPal Button Error:", err);
                showErrorAlert("Es ist ein Fehler bei PayPal aufgetreten.");
            }
        }).render(container);
    }
</script>

<div class="background">
    <header class="header-section">
        <h1 class="header-text">CINEPHORIA - Checkout</h1>
        <p class="tagline">Fast am Ziel! Bitte überprüfe deine Daten.</p>
    </header>

    <main class="checkout-container">
        <h2>Deine Daten</h2>
        <form class="checkout-form" on:submit|preventDefault>
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
        </form>

        <h2>Gesamtpreis: {totalPrice.toFixed(2)} €</h2>

        <div class="payment-section">
            <p>Wähle deine Zahlungsmethode:</p>
            <div class="paypal-placeholder">
                {#if paypalLoaded}
                    <!-- PayPal-Container -->
                    <div bind:this={paypalContainer} id="paypal-button-container"></div>
                {:else}
                    <p>PayPal-Button wird geladen ...</p>
                {/if}
            </div>
        </div>

        <div class="button-group">
            <button class="back-btn" on:click={() => navigate('/warenkorb')}>
                <i class="fas fa-arrow-left"></i> Zurück zum Warenkorb
            </button>
        </div>
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
  min-height: 80px;
  justify-content: center;
}

.button-group {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 2rem;
}

.back-btn {
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

.back-btn:hover {
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
