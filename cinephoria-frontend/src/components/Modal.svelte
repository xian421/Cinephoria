<!-- src/components/Modal.svelte -->
<script>
    import { createEventDispatcher } from 'svelte';

    export let title = '';
    export let onClose = () => {};

    const dispatch = createEventDispatcher();

    function closeModal() {
        dispatch('close');
    }
</script>

<div class="modal-overlay" on:click|self={closeModal}>
    <div class="modal">
        <button class="close-button" on:click={closeModal}>×</button>
        <h2>{title}</h2>
        <slot></slot>
    </div>
</div>

<style>
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
    }

    .modal {
        background: #fff;
        padding: 30px;
        border-radius: 10px;
        width: 90%;
        max-width: 500px;
        position: relative;
    }

    .modal h2 {
        margin-top: 0;
    }

    .close-button {
        position: absolute;
        top: 15px;
        right: 20px;
        background: none;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
    }
</style>
