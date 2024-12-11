<!-- src/components/SeatModal.svelte -->
<script lang="ts">
    import { createEventDispatcher, onMount, onDestroy } from 'svelte';
    import { fly } from 'svelte/transition';

    type ModalEvents = {
        close: void;
    };

    const dispatch = createEventDispatcher<ModalEvents>();

    export let seat: {
        row: string;
        number: number;
        type?: string;
        price: number;
    } | null = null;

    function closeModal() {
        dispatch('close');
    }

    function handleKeydown(event: KeyboardEvent) {
        if (event.key === 'Escape') {
            closeModal();
        }
    }

    onMount(() => {
        window.addEventListener('keydown', handleKeydown);
    });

    onDestroy(() => {
        window.removeEventListener('keydown', handleKeydown);
    });
</script>

{#if seat}
    <div class="modal" in:fly={{ x: 300 }} out:fly={{ x: 300 }}>
        <button class="close-button" on:click={closeModal}>&times;</button>
        <h2>Details zum Sitzplatz</h2>
        <p><strong>Reihe:</strong> {seat.row}</p>
        <p><strong>Sitznummer:</strong> {seat.number}</p>
        <p><strong>Typ:</strong> {seat.type || 'Standard'}</p>
        <p><strong>Preis:</strong> {seat.price.toFixed(2)}€</p>
        <p>Hier kann dein Bullshit stehen.</p>
    </div>
{/if}

<style>
    .modal {
        position: fixed;
        top: 0;
        right: 0;
        width: 33.333%;
        height: 100%;
        background: #fff;
        box-shadow: -2px 0 5px rgba(0,0,0,0.3);
        padding: 2rem;
        z-index: 1001;
        overflow-y: auto;
        transition: transform 0.3s ease-in-out;
    }

    .close-button {
        position: absolute;
        top: 1rem;
        right: 1rem;
        background: transparent;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
    }

    @media (max-width: 768px) {
        .modal {
            width: 100%;
        }
    }
</style>
