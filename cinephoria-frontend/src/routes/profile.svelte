<!-- src/routes/Profil.svelte -->
<script>
  import { onMount } from 'svelte';
  import { get } from 'svelte/store';
  import { authStore } from '../stores/authStore';
  import { fetchProfile } from '../services/api.js';
  import Swal from 'sweetalert2';
  import { navigate } from 'svelte-routing';

  let profile = {
      vorname: '',
      nachname: '',
      email: '',
      role: ''
  };
  let isLoading = true;
  let error = null;

  onMount(async () => {
      const token = get(authStore).token;
      if (!token) {
          error = 'Nicht authentifiziert';
          isLoading = false;
          Swal.fire({
              title: "Fehler",
              text: error,
              icon: "error",
              confirmButtonText: "OK",
          });
          return;
      }

      try {
          const data = await fetchProfile(token);
          profile = data;
      } catch (err) {
          console.error('Fehler beim Abrufen des Profils:', err);
          error = err.message || 'Fehler beim Abrufen des Profils';
          Swal.fire({
              title: "Fehler",
              text: error,
              icon: "error",
              confirmButtonText: "OK",
          });
      } finally {
          isLoading = false;
      }
  });

  // Funktion zur Berechnung der Initialen
  function getInitials(vorname, nachname) {
      const vorInitial = vorname ? vorname.charAt(0).toUpperCase() : '';
      const nachInitial = nachname ? nachname.charAt(0).toUpperCase() : '';
      return `${vorInitial}${nachInitial}`;
  }
</script>

<style>
  /* Gesamtcontainer */
  .profile-container {
      max-width: 800px;
      margin: 2rem auto;
      padding: 2rem;
      background: linear-gradient(145deg, #ffffff, #f8f9fa);
      border-radius: 12px;
      box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
      font-family: Arial, sans-serif;
  }

  /* Profilüberschrift */
  .profile-header {
      display: flex;
      align-items: center;
      gap: 1rem;
      margin-bottom: 2rem;
  }

  .initials {
      width: 100px;
      height: 100px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 50%;
      background-color: red;
      color: white;
      font-size: 2rem;
      font-weight: bold;
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }

  .profile-details {
      flex-grow: 1;
  }

  .profile-details h1 {
      font-size: 2rem;
      color: #333;
      margin: 0;
  }

  .profile-details p {
      font-size: 1rem;
      color: #555;
      margin: 0.5rem 0 0 0;
  }

  /* Profilinformationen */
  .profile-info {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1rem;
  }

  .profile-info div {
      background: #ffffff;
      padding: 1rem;
      border-radius: 8px;
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }

  .profile-info div h3 {
      font-size: 1.2rem;
      color: #333;
      margin-bottom: 0.5rem;
  }

  .profile-info div p {
      font-size: 1rem;
      color: #555;
      margin: 0;
  }

  /* Buttons */
  .profile-actions {
      display: flex;
      justify-content: space-between;
      gap: 1rem;
      margin-top: 2rem;
  }

  .profile-actions button {
      flex: 1;
      font-size: 1rem;
      font-weight: bold;
      color: #ffffff;
      background: #3498db;
      border: none;
      border-radius: 8px;
      padding: 0.8rem 1.5rem;
      cursor: pointer;
      transition: background 0.3s ease;
  }

  .profile-actions button:hover {
      background: #24b497;
  }

  /* Responsive Design */
  @media (max-width: 600px) {
      .profile-info {
          grid-template-columns: 1fr;
      }

      .profile-header {
          flex-direction: column;
          align-items: center;
          text-align: center;
      }

      .profile-details p {
          margin-top: 0.5rem;
      }
  }

  /* Fehleranzeige */
  .error-message {
      color: red;
      text-align: center;
      font-weight: bold;
      margin-top: 2rem;
  }
</style>

<main>
  {#if isLoading}
      <p>Lade Profil...</p>
  {:else if error}
      <p class="error-message">{error}</p>
  {:else}
      <div class="profile-container">
          <div class="profile-header">
              <div class="initials">
                  {getInitials(profile.vorname, profile.nachname)}
              </div>
              <div class="profile-details">
                  <h1>{profile.vorname} {profile.nachname}</h1>
                  <p>{profile.email}</p>
              </div>
          </div>

          <div class="profile-info">
              <div>
                  <h3>Vorname</h3>
                  <p>{profile.vorname}</p>
              </div>
              <div>
                  <h3>Nachname</h3>
                  <p>{profile.nachname}</p>
              </div>
              <div>
                  <h3>Email</h3>
                  <p>{profile.email}</p>
              </div>
              <div>
                  <h3>Rolle</h3>
                  <p>{profile.role}</p>
              </div>
          </div>

          <div class="profile-actions">
              <button on:click={() => navigate('/edit-profile')}>Profil bearbeiten</button>
              
          </div>
      </div>
      <button class="back-button" on:click={() => navigate('/')}>Zurück zur Startseite</button>
  {/if}
</main>
