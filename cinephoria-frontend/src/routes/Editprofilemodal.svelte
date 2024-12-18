<!-- src/components/EditProfileModal.svelte -->
<script>
    import { createEventDispatcher } from 'svelte';
    import { get } from 'svelte/store';
    import { authStore, updateAuth } from '../stores/authStore';
    import { updateProfile } from '../services/api.js';
    import Swal from 'sweetalert2';

    const dispatch = createEventDispatcher();

    export let initialProfile = {
        vorname: '',
        nachname: '',
        email: '',
        nickname: '',
        role: ''
    };

    let vorname = initialProfile.vorname;
    let nachname = initialProfile.nachname;
    let email = initialProfile.email;
    let nickname = initialProfile.nickname;
    let role = initialProfile.role;

    let isSubmitting = false;

    let emailError = '';

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Einfache E-Mail-Validierung
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            emailError = 'Bitte eine gültige E-Mail-Adresse eingeben.';
            return;
        } else {
            emailError = '';
        }

        isSubmitting = true;

        const token = get(authStore).token;
        const updates = { vorname, nachname, email, nickname, role };

        try {
            const data = await updateProfile(token, updates);
            Swal.fire({
                title: "Erfolgreich",
                text: data.message || "Profil erfolgreich aktualisiert.",
                icon: "success",
                timer: 1500,
                showConfirmButton: false,
            });
            
            // Aktualisiere den Auth-Store
            updateAuth(current => ({
                ...current,
                userFirstName: vorname,
                userLastName: nachname,
                initials: getInitials(vorname, nachname),
                email: email,
                nickname: nickname,
                role: role
            }));

            // Dispatch das 'update' Event mit den neuen Profil-Daten
            dispatch('update', { vorname, nachname, email, nickname, role });

            dispatch('close');
        } catch (err) {
            console.error('Fehler beim Aktualisieren des Profils:', err);
            Swal.fire({
                title: "Fehler",
                text: err.message || 'Fehler beim Aktualisieren des Profils',
                icon: "error",
                confirmButtonText: "OK",
            });
        } finally {
            isSubmitting = false;
        }
    };

    function getInitials(vorname, nachname) {
        const vorInitial = vorname ? vorname.charAt(0).toUpperCase() : '';
        const nachInitial = nachname ? nachname.charAt(0).toUpperCase() : '';
        return `${vorInitial}${nachInitial}`;
    }

    const handleClose = () => {
        dispatch('close');
    };
</script>

<div class="modal-overlay" on:click={handleClose}>
    <div class="modal-content" on:click|stopPropagation>
        <header class="modal-header">
            <h2>Profil bearbeiten</h2>
            <button class="close-button" on:click={handleClose}>&times;</button>
        </header>
        <form on:submit={handleSubmit}>
            <div class="form-group">
                <label for="vorname">Vorname</label>
                <input id="vorname" type="text" bind:value={vorname} required />
            </div>
            <div class="form-group">
                <label for="nachname">Nachname</label>
                <input id="nachname" type="text" bind:value={nachname} required />
            </div>
            <div class="form-group">
                <label for="email">Email</label>
                <input id="email" type="email" bind:value={email} required />
                {#if emailError}
                    <p class="error-text">{emailError}</p>
                {/if}
            </div>
            <div class="form-group">
                <label for="nickname">Nickname</label>
                <input id="nickname" type="text" bind:value={nickname} required />
            </div>
            <!-- Optional: Rolle nur anzeigen, wenn der Benutzer Admin ist -->
         <!--    {#if !$authStore.isAdmin} -->
                <div class="form-group">
                    <label for="role">Rolle</label>
                    <input id="role" type="text" bind:value={role} required />
                </div>
       <!--      {/if} -->
            <div class="form-actions">
                <button type="submit" disabled={isSubmitting}>
                    {#if isSubmitting}
                        <i class="fas fa-spinner fa-spin"></i> Speichern...
                    {:else}
                        <i class="fas fa-save"></i> Speichern
                    {/if}
                </button>
                <button type="button" class="cancel-button" on:click={handleClose}>
                    Abbrechen
                </button>
            </div>
        </form>
    </div>
</div>

<style>
    
    .error-text {
        color: #e74c3c;
        font-size: 0.9rem;
        margin-top: 0.3rem;
    }

    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.6);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
    }

    .modal-content {
        background: #1a1a1a;
        padding: 2rem;
        border-radius: 12px;
        width: 90%;
        max-width: 500px;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
        color: #fff;
    }

    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
    }

    .modal-header h2 {
        margin: 0;
        color: #2ecc71;
        text-shadow: 0 0 5px #2ecc71;
    }

    .close-button {
        background: none;
        border: none;
        color: #e74c3c;
        font-size: 1.5rem;
        cursor: pointer;
        transition: color 0.3s;
    }

    .close-button:hover {
        color: #c0392b;
    }

    .form-group {
        margin-bottom: 1rem;
    }

    .form-group label {
        display: block;
        margin-bottom: 0.5rem;
        color: #2ecc71;
    }

    .form-group input {
        width: 100%;
        padding: 0.8rem;
        border: none;
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.1);
        color: #fff;
        font-size: 1rem;
    }

    .form-group input:focus {
        outline: none;
        background: rgba(255, 255, 255, 0.2);
    }

    .form-actions {
        display: flex;
        justify-content: flex-end;
        gap: 1rem;
    }

    .form-actions button {
        padding: 0.8rem 1.5rem;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        font-size: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        transition: background-color 0.3s, transform 0.3s;
    }

    .form-actions button[type="submit"] {
        background: #2ecc71;
        color: #fff;
        box-shadow: 0 0 10px #2ecc71;
    }

    .form-actions button[type="submit"]:hover {
        background: #27ae60;
        transform: translateY(-2px);
        box-shadow: 0 0 15px #27ae60;
    }

    .cancel-button {
        background: #e74c3c;
        color: #fff;
        box-shadow: 0 0 10px #e74c3c;
    }

    .cancel-button:hover {
        background: #c0392b;
        transform: translateY(-2px);
        box-shadow: 0 0 15px #c0392b;
    }

    @media (max-width: 480px) {
        .modal-content {
            padding: 1.5rem;
        }

        .form-actions {
            flex-direction: column;
            align-items: stretch;
        }

        .form-actions button {
            width: 100%;
            justify-content: center;
        }
    }
</style>
