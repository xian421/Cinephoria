<!-- src/components/ProtectedRoute.svelte -->
<script>
    import { navigate } from "svelte-routing";
    import { authStore } from '../stores/authStore.js';
    import { onMount } from 'svelte';
    import Swal from 'sweetalert2';
    export let admin = false;

    $: ({ isLoggedIn, isAdmin } = $authStore);

    onMount(() => {
        if (!isLoggedIn) {
            Swal.fire({
                title: "Nicht autorisiert",
                text: "Bitte loggen Sie sich ein.",
                icon: "error",
                confirmButtonText: "OK",
            });
            navigate('/');
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
    <slot />
{/if}
