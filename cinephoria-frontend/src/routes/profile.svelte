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
    import EditProfileModal from './Editprofilemodal.svelte';
    
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
    let isEditModalOpen = false; // Zustand für das Edit-Modal
    let availableImages = [];
    
    onMount(async () => {
        await loadProfile();
    });
    
    async function loadProfile() {
        isLoading = true;
        error = null;
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

            updateAuth(current => ({
                ...current,
                isLoggedIn: true,
                userFirstName: data.vorname,
                userLastName: data.nachname,
                initials: getInitials(data.vorname, data.nachname),
                isAdmin: data.role === 'admin',
                profile_image: data.profile_image || 'default.png',
                email: data.email,
                role: data.role
            }));

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
    }
    
    function getInitials(vorname, nachname) {
        const vorInitial = vorname ? vorname.charAt(0).toUpperCase() : '';
        const nachInitial = nachname ? nachname.charAt(0).toUpperCase() : '';
        return `${vorInitial}${nachInitial}`;
    }
    
    function openModal() {
        isModalOpen = true;
    }
    
    function closeModal() {
        isModalOpen = false;
    }
    
    function openEditModal() { // Funktion zum Öffnen des Edit-Modals
        isEditModalOpen = true;
    }
    
    function closeEditModal() { // Funktion zum Schließen des Edit-Modals
        isEditModalOpen = false;
    }
    
    async function selectProfileImage(imageName) {
        const token = get(authStore).token;
        try {
            await updateProfileImage(token, imageName);
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

    // Funktion zum Aktualisieren des lokalen Profils nach einer erfolgreichen Bearbeitung
    function handleProfileUpdate(event) {
        const { vorname, nachname, email } = event.detail;
        profile = { ...profile, vorname, nachname, email };
    }
</script>

<div class="background">
    <header class="header-section">
        <h1 class="header-text">CINEPHORIA - Dein Profil</h1>
        <p class="tagline">Verwalte deine Daten in futuristischem Stil!</p>
    </header>

    <main>
        {#if isLoading}
            <p class="loading">Profil wird geladen...</p>
        {:else if error}
            <p class="error-message">{error}</p>
        {:else}
            <div class="profile-container">
                <!-- Eine Art Überschrift / Titel für die Profilsektion -->
                <h2 class="section-title">Übersicht deiner persönlichen Daten</h2>

                <div class="profile-header">
                    {#if profile.profile_image && profile.profile_image !== 'default.png'}
                        <div class="image-container" on:click={openModal} title="Klicke, um dein Profilbild zu ändern">
                            <ProfileImage src={`/Profilbilder/${profile.profile_image}`} class="profile-image-wrapper" />
                            <div class="change-hint">Profilbild ändern</div>
                        </div>
                    {:else}
                        <div class="initials" on:click={openModal} title="Klicke, um dein Profilbild zu ändern">
                            {getInitials(profile.vorname, profile.nachname)}
                            <div class="change-hint">Profilbild ändern</div>
                        </div>
                    {/if}

                    <div class="profile-details">
                        <h1>{profile.vorname} {profile.nachname}</h1>
                        <p class="email">{profile.email}</p>
                        <!-- Rolle mit einem kleinen Badge dargestellt -->
                        <div class="role-badge" title="Deine Rolle im System">
                            {#if profile.role === 'admin'}
                                <i class="fas fa-user-shield"></i> Administrator
                            {:else}
                                <i class="fas fa-user"></i> {profile.role.charAt(0).toUpperCase() + profile.role.slice(1)}
                            {/if}
                        </div>
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
                    <button on:click={openEditModal}>
                        <i class="fas fa-user-edit"></i> Profil bearbeiten
                    </button>
                </div>

                <button class="back-button" on:click={() => navigate('/')}>
                    <i class="fas fa-home"></i> Zurück zur Startseite
                </button>

                {#if isModalOpen}
                    <ProfileModal 
                        images={availableImages} 
                        selectedImage={profile.profile_image} 
                        onSelect={selectProfileImage} 
                        onClose={closeModal} 
                    />
                {/if}

                {#if isEditModalOpen}
                    <EditProfileModal 
                        initialProfile={{ vorname: profile.vorname, nachname: profile.nachname, email: profile.email }} 
                        on:close={closeEditModal} 
                        on:update={handleProfileUpdate} 
                    />
                {/if}
            </div>
        {/if}
    </main>
</div>




<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
@import url('https://use.fontawesome.com/releases/v5.15.4/css/all.css');

* {
    box-sizing: border-box;
}



body {
    margin: 0;
    font-family: 'Roboto', sans-serif;
    background: linear-gradient(135deg, #000428, #004e92);
    color: #fff;
    overflow-x: hidden;
    max-width: 100%;
}

.background {
    position: relative;
    min-height: 100vh;
    padding: 2rem;
    overflow: hidden;
}

.header-section {
    text-align: center;
    margin-bottom: 3rem;
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
    text-align: center;
}

@keyframes glow {
  from {
    text-shadow: 0 0 10px #2ecc71, 0 0 20px #2ecc71;
  }
  to {
    text-shadow: 0 0 20px #2ecc71, 0 0 40px #2ecc71;
  }
}

/* Profilcontainer im gleichen Stil wie vorherige Layouts (max-width:1200px) */


.section-title {
    text-align: center;
    color: #2ecc71;
    text-shadow: 0 0 10px #2ecc71;
    margin-bottom: 3rem;
    font-size: 1.8rem;
}

.profile-header {
    display: flex;
    align-items: center;
    gap: 2rem;
    margin-bottom: 2rem;
    flex-wrap: wrap;
    justify-content: center;
}

.image-container {
    position: relative;
    display: inline-block;
}

.change-hint {
    position: absolute;
    bottom: -1.5rem;
    width: 100%;
    text-align: center;
    font-size: 0.8rem;
    color: #2ecc71;
    text-shadow: 0 0 5px #2ecc71;
    opacity: 0;
    transform: translateY(10px);
    transition: opacity 0.3s, transform 0.3s;
}

.image-container:hover .change-hint {
    opacity: 1;
    transform: translateY(0);
}

.initials, .profile-image-wrapper {
    width: 120px;
    height: 120px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background-color: #1abc9c;
    color: #fff;
    font-size: 2.5rem;
    font-weight: bold;
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
    cursor: pointer;
    transition: background-color 0.3s ease, transform 0.3s ease, box-shadow 0.3s;
}

.initials:hover, .profile-image-wrapper:hover {
    background-color: #16a085;
    transform: scale(1.1);
    box-shadow: 0 0 10px #2ecc71;
}

.profile-image-wrapper img {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    object-fit: cover;
}

.profile-details {
    flex-grow: 1;
    text-align: center;
}

.profile-details h1 {
    font-size: 2rem;
    color: #2ecc71;
    text-shadow: 0 0 10px #2ecc71;
    margin: 0;
}

.profile-details .email {
    font-size: 1rem;
    color: #7f8c8d;
    margin-top: 0.5rem;
}

.role-badge {
    margin-top: 1rem;
    display: inline-block;
    background: rgba(0,0,0,0.4);
    padding: 0.5rem 1rem;
    border-radius: 20px;
    color: #fff;
    font-weight: bold;
    box-shadow: 0 0 10px #2ecc71;
    font-size: 0.9rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    justify-content: center;
}

.role-badge i {
    color: #f1c40f;
}

/* Profilinformationen */
.profile-info {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.profile-info div {
    background: rgba(0,0,0,0.4);
    padding: 1.5rem;
    border-radius: 16px;
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    text-align: center;
}

.profile-info div:hover {
    transform: translateY(-5px);
    box-shadow: 0 0 25px #2ecc71;
}

.profile-info div h3 {
    font-size: 1.2rem;
    color: #2ecc71;
    margin-bottom: 0.5rem;
    text-shadow: 0 0 5px #2ecc71;
}

.profile-info div p {
    font-size: 1rem;
    color: #ddd;
    margin: 0;
}

/* Buttons */
.profile-actions {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-top: 2rem;
}

.profile-actions button {
    font-size: 1rem;
    font-weight: 600;
    color: #000;
    background: #2ecc71;
    border: none;
    border-radius: 12px;
    padding: 0.8rem 1.5rem;
    cursor: pointer;
    transition: background-color 0.3s ease, transform 0.3s ease, box-shadow 0.3s;
    box-shadow: 0 0 10px #2ecc71;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.profile-actions button:hover {
    background: #27ae60;
    transform: translateY(-3px) scale(1.05);
    box-shadow: 0 0 15px #27ae60;
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
    transition: background-color 0.3s, transform 0.3s, box-shadow 0.3s;
    box-shadow: 0 0 10px #e74c3c;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.back-button:hover {
    background-color: #c0392b;
    transform: translateY(-3px) scale(1.05);
    box-shadow: 0 0 15px #c0392b;
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

    .profile-details {
        text-align: center;
    }
}
</style>
