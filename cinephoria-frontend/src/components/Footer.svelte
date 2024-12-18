<!-- src/components/Footer.svelte -->
<script>
  import Swal from 'sweetalert2';
  export let firstCinema;
</script>

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
      <button on:click={() => Swal.fire({
        title: "Datenschutzerklärung",
        icon: "info",
        html: `
            <h3>Verantwortlicher</h3>
            <p>Max Mustermann<br />
            Musterweg 111<br />
            Hausnummer 44<br />
            90210 Musterstadt</p>
    
            <h3>Datenerhebung</h3>
            <p>Wir erheben, verarbeiten und nutzen personenbezogene Daten nur, soweit dies für die Bereitstellung unserer Dienste erforderlich ist. Dazu gehören:</p>
            <ul style="text-align: left; margin-left: 10px;">
                <li>Kontaktinformationen (Name, E-Mail, Telefonnummer)</li>
                <li>Nutzungsdaten (IP-Adresse, Zeitstempel der Nutzung)</li>
            </ul>
    
            <h3>Verwendung der Daten</h3>
            <p>Ihre Daten werden für folgende Zwecke verwendet:</p>
            <ul style="text-align: left; margin-left: 10px;">
                <li>Bereitstellung unserer Dienstleistungen</li>
                <li>Verbesserung der Nutzererfahrung</li>
                <li>Kommunikation und Support</li>
            </ul>
    
            <h3>Ihre Rechte</h3>
            <p>Sie haben das Recht, jederzeit Auskunft über die bei uns gespeicherten Daten zu erhalten. Darüber hinaus können Sie die Berichtigung, Sperrung oder Löschung Ihrer Daten verlangen, soweit keine gesetzlichen Aufbewahrungspflichten bestehen.</p>
    
            <h3>Kontakt</h3>
            <p>Für Anfragen zum Datenschutz kontaktieren Sie uns bitte:</p>
            <p>E-Mail: datenschutz@musterfirma.de<br />
            Telefon: +49 (0) 123 44 55 66</p>
        `,
        confirmButtonText: "Schließen"
    })}>
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

<style>
  /* Globale Stile */
  footer {
    
      color: #fff;
      padding: 2rem 1rem;
      border-radius: 0 0 12px 12px;
     
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      width: 100%;
      box-sizing: border-box;
      margin-top: 2rem;

  }

  /* Button-Stile */
  button {
    font-size: 1rem;
        font-weight: bold;
        background: transparent;
        color: #fff;
        border: 2px solid transparent;
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 0 0.5rem;
        text-shadow: 0 0 5px #fff;
        z-index: 1001;
  }

  button:hover {
    border-color: #2ecc71;
        transform: scale(1.05);
        box-shadow: 0 0 10px #2ecc71;
  }

  /* Anpassung der Footer-Buttons */
  .footer-buttons {
    font-size: 1rem;
        font-weight: bold;
        background: transparent;
        color: #fff;
        border: 2px solid transparent;
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 0 0.5rem;
        text-shadow: 0 0 5px #fff;
        z-index: 1001;
  }

  .footer-buttons button {
      background: rgba(255, 255, 255, 0.1);
      color: #fff;
      padding: 0.8rem 1.5rem;
      border: 2px solid transparent;
      border-radius: 12px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
      transition: all 0.3s ease;
  }

  .footer-buttons button:hover {
    border-color: #2ecc71;
        transform: scale(1.05);
        box-shadow: 0 0 10px #2ecc71;
  }

  /* Social-Media-Icons */
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
      background: rgba(255, 255, 255, 0.1);
      width: 50px;
      height: 50px;
      border-radius: 50%;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
      transition: all 0.3s ease;
  }

  .social-icons a:hover {
     border-color: #2ecc71;
        transform: scale(1.05);
        box-shadow: 0 0 10px #2ecc71;
  }

  .social-icons img {
      width: 60%;
      height: 60%;
      object-fit: contain;
  }

  /* Scroll-to-Top Button */
  .scroll-to-top {
      font-size: 1rem;
      font-weight: bold;
      color: #fff;
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

  /* Footer-Text */
  .footer-text {
      color: #fff;
      font-size: 0.9rem;
      text-align: center;
  }

  /* Responsives Design */
  @media (max-width: 768px) {
      .footer-buttons {
          flex-direction: column;
          gap: 1rem;
      }

      .social-icons {
          gap: 1rem;
      }

      .social-icons a {
          width: 40px;
          height: 40px;
      }

      .scroll-to-top {
          padding: 0.6rem 1.2rem;
          font-size: 0.9rem;
      }
  }
</style>
