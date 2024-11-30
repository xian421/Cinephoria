<!-- src/components/ProtectedRoute.svelte -->
<script>
    import { navigate } from "svelte-routing";
    import { authStore } from '../stores/authStore.js';
    import { onMount } from 'svelte';
    import Swal from 'sweetalert2';
    import { createEventDispatcher } from 'svelte';

    export let component; // Die zu rendernde Komponente
    export let admin = false; // Ob Admin-Rechte erforderlich sind

    // Reaktive Zuweisung der Store-Werte
    $: isLoggedIn = $authStore.isLoggedIn;
    $: isAdmin = $authStore.isAdmin;

    onMount(() => {
        if (!isLoggedIn) {
            Swal.fire({
                title: "Nicht autorisiert",
                text: "Bitte loggen Sie sich ein.",
                icon: "error",
                confirmButtonText: "OK",
            });
            navigate('/unauthorized');
        } else if (admin && !isAdmin) {
            Swal.fire({
                title: "Zugriff verweigert",
                text: "Sie haben keine Admin-Rechte.",
                icon: "error",
                confirmButtonText: "OK",
            });
            navigate('/unauthorized');
        }
    });
</script>

{#if isLoggedIn && (!admin || isAdmin)}
    <svelte:component this={component} />
{/if}
