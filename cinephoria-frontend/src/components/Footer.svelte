<!-- src/components/Footer.svelte -->
<script>
    import Swal from 'sweetalert2';
    export let firstCinema;
</script>




<style>
  
    /* Button-Stile */
    button {
      font-size: 1.2rem;
      font-weight: bold;
      color: rgb(0, 0, 0);
      background: #ffffff;
      border: 2px solid transparent;
      border-radius: 12px;
      padding: 1rem 2rem;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
      cursor: pointer;
      transition: all 0.3s ease;
      min-width: 160px;
      text-align: center;
    }
  
    button:hover {
      border-color: #1abc9c;
      transform: scale(1.1);
    }

  
    /* Footer-Stile */
    footer {
      position: relative;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      background: #ffffff;
      padding: 2rem 1rem;
      border-radius: 0 0 12px 12px;
      box-shadow: 0 -4px 6px rgba(0, 0, 0, 0.3);
      margin-top: 2rem;
      overflow: hidden;
    }
  
    footer::before {
      content: '';
      position: absolute;
      top: -30px;
      left: 0;
      width: 100%;
      height: 60px;
      background: #ffffff;
      border-radius: 50%;
      box-shadow: 0 -4px 6px rgba(0, 0, 0, 0.1);
      z-index: -1;
    }
  
    .footer-buttons {
      display: flex;
      gap: 1.5rem;
      margin-bottom: 1.5rem;
    }
  
    .footer-buttons button {
      font-size: 1rem;
      font-weight: bold;
      color: rgb(0, 0, 0);
      background: #ffffff;
      border: 2px solid transparent;
      border-radius: 12px;
      padding: 0.8rem 1.5rem;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
      cursor: pointer;
      transition: all 0.3s ease;
    }
  
    .footer-buttons button:hover {
      border-color: #1abc9c;
      transform: scale(1.1);
    }
  
    .social-icons {
      display: flex;
      gap: 1.5rem;
      margin-bottom: 1.5rem;
    }
  
    .social-icons a {
      text-decoration: none;
      color: white;
      font-size: 1.5rem;
      display: flex;
      justify-content: center;
      align-items: center;
      background: #ffffff;
      width: 50px;
      height: 50px;
      border-radius: 50%;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
      transition: all 0.3s ease;
    }
  
    .social-icons a:hover {
      background: #1abc9c;
      transform: scale(1.1);
    }
  
    .social-icons img {
      width: 100%;
      height: 100%;
      object-fit: contain;
    }
  
    .scroll-to-top {
      font-size: 1rem;
      font-weight: bold;
      color: white;
      background: #3498db;
      border: 2px solid transparent;
      border-radius: 50px;
      padding: 0.8rem 1.5rem;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
      cursor: pointer;
      transition: all 0.3s ease;
      margin-top: 1.5rem;
    }
  
    .scroll-to-top:hover {
      border-color: #1abc9c;
      transform: scale(1.1);
      background: #24b497;
    }
  
    .footer-text {
      color: black;
      font-size: 0.9rem;
      text-align: center;
    }
  
  </style>




<footer>
    <!-- Interaktive Buttons -->
    <div class="footer-buttons">
        <button on:click={() => Swal.fire({
            title: "Kontakt",
            icon: "info",
            html: `
                <h2>${firstCinema.name}</h2>
                <p>Standort: ${firstCinema.location}<br />
                Telefax: ${firstCinema.contact_number}<br />
            `,
            confirmButtonText: "Schließen"
        })}>
            Kontakt
        </button>
        <button on:click={() => Swal.fire({
            title: "Impressum",
            icon: "info",
            html: `
                <p>Max Mustermann<br />
                Musterweg 111<br />
                Hausnummer 44<br />
                90210 Musterstadt</p>
                <h2>Kontakt</h2>
                <p>Telefon: +49 (0) 123 44 55 66<br />
                Telefax: +49 (0) 123 44 55 99<br />
                E-Mail: mustermann@musterfirma.de</p>
            `,
            confirmButtonText: "Schließen"
        })}>
            Impressum
        </button>
        <button on:click={() => alert("Datenschutz anzeigen!")}>
            Datenschutz
        </button>
    </div>

    <!-- Social-Media-Icons -->
    <div class="social-icons">
        <a href="https://facebook.com" target="_blank" aria-label="Facebook">
            <img src="/facebook.png" alt="Facebook" />
        </a>
        <a href="https://twitter.com" target="_blank" aria-label="Twitter">
            <img src="/twitter.png" alt="Twitter" />
        </a>
        <a href="https://instagram.com" target="_blank" aria-label="Instagram">
            <img src="/instagram.png" alt="Instagram" />
        </a>
        <a href="https://linkedin.com" target="_blank" aria-label="LinkedIn">
            <img src="/linked.png" alt="LinkedIn" />
        </a>
    </div>

    <!-- Scroll-to-Top Button -->
    <button class="scroll-to-top" on:click={() => window.scrollTo({ top: 0, behavior: "smooth" })}>
        Nach oben
    </button>

    <!-- Footer-Text -->
    <p class="footer-text">
        © 2024 Cinephoria. Alle Rechte vorbehalten.
    </p>
</footer>
