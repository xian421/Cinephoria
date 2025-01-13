<!-- src/components/ProtectedRoute.svelte -->
<script>
    import { navigate } from "svelte-routing";
    import { authStore } from '../stores/authStore.js';
    import { onMount } from 'svelte';
    import Swal from 'sweetalert2';
    import { get } from 'svelte/store';

    export let admin = false;

    let isLoggedIn;
    let isAdmin;

    onMount(async () => {
        const auth = get(authStore);
        isLoggedIn = auth.isLoggedIn;
        isAdmin = auth.isAdmin;

        if (!isLoggedIn) {
            await Swal.fire({
                title: "Nicht autorisiert",
                text: "Bitte loggen Sie sich ein.",
                icon: "error",
                confirmButtonText: "OK",
            });
            navigate('/');
            setTimeout(() => {
                location.reload();
            }, 500);
        } else if (admin && !isAdmin) {
            await Swal.fire({
                title: "Zugriff verweigert",
                text: "Sie haben keine Admin-Rechte.",
                icon: "error",
                confirmButtonText: "OK",
            });
            navigate('/unauthorized');
            setTimeout(() => {
                location.reload();
            }, 500);
        }
    });
</script>

{#if isLoggedIn && (!admin || isAdmin)}
    <slot />
{/if}
