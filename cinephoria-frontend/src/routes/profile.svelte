<!-- src/routes/profile.svelte -->
<script>
  import { onMount } from 'svelte';
  import { get } from 'svelte/store';
  import { authStore, updateAuth } from '../stores/authStore';
  import { fetchProfile, updateProfileImage, fetchAvailableProfileImages } from '../services/api.js';
  import Swal from 'sweetalert2';
  import { navigate } from 'svelte-routing';

  let profile = {
      vorname: '',
      nachname: '',
      email: '',
      role: '',
      profile_image: 'default.png'
  };
  let isLoading = true;
  let error = null;
  let isModalOpen = false;
  let availableImages = [];

  onMount(async () => {
      const token = get(authStore).token;
      console.log('Token erhalten:', token); // Log Token
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
          // Profilinformationen abrufen
          const data = await fetchProfile(token);
          console.log('Profildaten erhalten:', data); // Log Profildaten
          profile = data;

          // Verfügbare Profilbilder abrufen
          const images = await fetchAvailableProfileImages(token);
          console.log('Verfügbare Profilbilder:', images); // Log verfügbare Bilder
          availableImages = images;
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

  // Funktionen zur Handhabung des Modals
  function openModal() {
      isModalOpen = true;
      console.log('Modal geöffnet'); // Log Modal öffnen
  }

  function closeModal() {
      isModalOpen = false;
      console.log('Modal geschlossen'); // Log Modal schließen
  }

  // Funktion zum Aktualisieren des Profilbildes
  async function selectProfileImage(imageName) {
      console.log('Ausgewähltes Bild:', imageName); // Log ausgewähltes Bild
      const token = get(authStore).token;
      try {
          const response = await updateProfileImage(token, imageName);
          console.log('Antwort nach Aktualisierung des Profilbildes:', response); // Log Antwort
          profile.profile_image = imageName;
          updateAuth(current => ({
              ...current,
              profile_image: imageName
          }));
          Swal.fire({
              title: "Erfolgreich",
              text: "Profilbild wurde aktualisiert.",
              icon: "success",
              timer: 1500,
              showConfirmButton: false,
          });
          closeModal();
      } catch (err) {
          console.error('Fehler beim Aktualisieren des Profilbildes:', err);
          Swal.fire({
              title: "Fehler",
              text: err.message || 'Fehler beim Aktualisieren des Profilbildes',
              icon: "error",
              confirmButtonText: "OK",
          });
      }
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
    background-color: #3498db;
    color: white;
    font-size: 2rem;
    font-weight: bold;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    cursor: pointer;
    position: relative;
}


.noinitials {
    width: 100px;
    height: 100px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background-color: white;
    color: white;
    font-size: 2rem;
    font-weight: bold;
    cursor: pointer;
    position: relative;
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

/* Modal */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.modal-content {
    background: #fff;
    padding: 2rem;
    border-radius: 12px;
    max-width: 600px;
    width: 90%;
    max-height: 80%;
    overflow-y: auto;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.modal-header h2 {
    margin: 0;
}

.close-button {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: #aaa;
}

.close-button:hover {
    color: #000;
}

.image-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    gap: 1rem;
}

.image-item {
    border: 2px solid transparent;
    border-radius: 8px;
    cursor: pointer;
    transition: border-color 0.3s ease;
  
}

.image-item:hover {
    border-color: #3498db;
}

.image-item.selected {
    border-color: #3498db;
    
}

.image-item img {
    width: 100%;
    height: auto;
    border-radius: 8px;
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

/* Back Button */
.back-button {
    display: block;
    margin: 2rem auto 0;
    padding: 10px 20px;
    font-size: 16px;
    cursor: pointer;
    border: none;
    background-color: #1976d2;
    color: white;
    border-radius: 5px;
    transition: background-color 0.3s;
}

.back-button:hover {
    background-color: #1565c0;
}

.profile-image {
    width: 100%;
    height: auto;
    border-radius: 30%;
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
                  {#if profile.profile_image && profile.profile_image !== 'default.png'}
                    <div class="noinitials" on:click={openModal}>

                      <img src={`/Profilbilder/${profile.profile_image}`} alt="Profilbild" class="profile-image" />
                    </div>
                  {:else}
                    <div class="initials" on:click={openModal}>
                      {getInitials(profile.vorname, profile.nachname)}
                    </div>
                  {/if}
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
      <button class="back-button" on:click={() => navigate('/')}>Zurück zur Startseite</button>

      {#if isModalOpen}
          <div class="modal-overlay" on:click={closeModal}>
              <div class="modal-content" on:click|stopPropagation>
                  <div class="modal-header">
                      <h2>Profilbild auswählen</h2>
                      <button class="close-button" on:click={closeModal}>&times;</button>
                  </div>
                  <div class="image-grid">
                      {#if availableImages.length > 0}
                          {#each availableImages as image}
                              <div 
                                  class="image-item {profile.profile_image === image ? 'selected' : ''}" 
                                  on:click={() => selectProfileImage(image)}
                              >
                                  <img src={`/Profilbilder/${image}`} alt={image} />
                              </div>
                          {/each}
                      {:else}
                          <p>Keine Profilbilder verfügbar.</p>
                      {/if}
                  </div>
              </div>
          </div>
      {/if}
  {/if}
</main>
