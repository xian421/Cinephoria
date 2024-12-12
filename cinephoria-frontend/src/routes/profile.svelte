<!-- src/routes/profile.svelte -->
<script>
    import { onMount } from 'svelte';
    import { get } from 'svelte/store';
    import { authStore, updateAuth } from '../stores/authStore';
    import { fetchProfile, updateProfileImage, fetchAvailableProfileImages } from '../services/api.js';
    import Swal from 'sweetalert2';
    import { navigate } from 'svelte-routing';
    import ProfileImage from './ProfileImage.svelte';
    import ProfileModal from './ProfileModal.svelte';
  
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
            profile = data;
  
            // Aktualisieren Sie den authStore mit den neuen Profilinformationen
            updateAuth(current => ({
                ...current,
                isLoggedIn: true,
                userFirstName: data.vorname,
                userLastName: data.nachname,
                initials: getInitials(data.vorname, data.nachname),
                isAdmin: data.role === 'admin', // Passen Sie dies an Ihre Rollenlogik an
                profile_image: data.profile_image || 'default.png',
                email: data.email, // Fügen Sie weitere benötigte Felder hinzu
                role: data.role
            }));
  
            // Verfügbare Profilbilder abrufen
            const images = await fetchAvailableProfileImages(token);
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
  
  <!-- Ihr CSS bleibt unverändert -->
  
  <main>
    {#if isLoading}
        <p class="loading">Profil wird geladen...</p>
    {:else if error}
        <p class="error-message">{error}</p>
    {:else}
        <div class="profile-container">
            <div class="profile-header">
                {#if profile.profile_image && profile.profile_image !== 'default.png'}
                    <ProfileImage src={`/Profilbilder/${profile.profile_image}`} on:click={openModal} />
                {:else}
                    <div class="initials" on:click={openModal}>
                        {getInitials(profile.vorname, profile.nachname)}
                    </div>
                {/if}
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
                <ProfileModal 
                    images={availableImages} 
                    selectedImage={profile.profile_image} 
                    onSelect={selectProfileImage} 
                    onClose={closeModal} 
                />
            {/if}
        </div>
    {/if}
  </main>
  
  <style>
    /* Gesamtcontainer */
.profile-container {
    max-width: 900px;
    margin: 2rem auto;
    padding: 2rem;
    background: #fdfdfd;
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    font-family: 'Roboto', sans-serif;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.profile-container:hover {
    transform: translateY(-10px);
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
}

/* Profilüberschrift */
.profile-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 2rem;
}

.initials, .profile-image-wrapper {
    width: 100px;
    height: 100px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background-color: #1abc9c;
    color: #fff;
    font-size: 2rem;
    font-weight: bold;
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
    cursor: pointer;
    transition: background-color 0.3s ease, transform 0.3s ease;
}

.initials:hover, .profile-image-wrapper:hover {
    background-color: #16a085;
    transform: scale(1.1);
}

.profile-image-wrapper img {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    object-fit: cover;
}

.profile-details {
    flex-grow: 1;
}

.profile-details h1 {
    font-size: 2rem;
    color: #34495e;
    margin: 0;
}

.profile-details p {
    font-size: 1rem;
    color: #7f8c8d;
    margin-top: 0.5rem;
}

/* Profilinformationen */
.profile-info {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.profile-info div {
    background: #ffffff;
    padding: 1.5rem;
    border-radius: 16px;
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.05);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.profile-info div:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.profile-info div h3 {
    font-size: 1.2rem;
    color: #2c3e50;
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
    font-weight: 600;
    color: #ffffff;
    background: #3498db;
    border: none;
    border-radius: 12px;
    padding: 0.8rem 1.5rem;
    cursor: pointer;
    transition: background-color 0.3s ease, transform 0.3s ease;
}

.profile-actions button:hover {
    background: #2980b9;
    transform: translateY(-3px);
}

/* Back Button */
.back-button {
    display: block;
    margin: 2rem auto 0;
    padding: 0.8rem 1.5rem;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    border: none;
    background-color: #e74c3c;
    color: white;
    border-radius: 10px;
    transition: background-color 0.3s, transform 0.3s;
}

.back-button:hover {
    background-color: #c0392b;
    transform: translateY(-3px);
}

/* Fehleranzeige */
.error-message {
    color: #e74c3c;
    text-align: center;
    font-weight: bold;
    margin-top: 3rem;
    font-size: 1.1rem;
}

/* Ladeanzeige */
.loading {
    text-align: center;
    font-size: 1.2rem;
    color: #3498db;
    margin-top: 3rem;
}

/* Responsive Design */
@media (max-width: 768px) {
    .profile-header {
        flex-direction: column;
        align-items: center;
        text-align: center;
    }

    .profile-info {
        grid-template-columns: 1fr;
    }

    .profile-actions {
        flex-direction: column;
    }
}

  </style>
  