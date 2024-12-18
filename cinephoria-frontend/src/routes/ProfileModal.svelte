<script>
    export let images = [];
    export let selectedImage = '';
    export let onSelect;
    export let onClose;
  
    function handleSelect(image) {
        onSelect(image);
    }
</script>

<div class="modal-overlay" on:click={onClose}>
    <div class="modal-content" on:click|stopPropagation>
        <div class="modal-header">
            <h2>Profilbild auswählen</h2>
            <button class="close-button" on:click={onClose}>&times;</button>
        </div>
        <div class="image-grid">
            {#if images.length > 0}
                {#each images as image}
                    <div 
                        class="image-item {selectedImage === image ? 'selected' : ''}" 
                        on:click={() => handleSelect(image)}
                    >
                        <img src={`/Profilbilder/${image}`} alt={image} />
                    </div>
                {/each}
            {:else}
                <p class="no-images">Keine Profilbilder verfügbar.</p>
            {/if}
        </div>
    </div>
</div>

<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
@import url('https://use.fontawesome.com/releases/v5.15.4/css/all.css');

* {
  box-sizing: border-box;
}

/* Modal Overlay mit dunklem Hintergrund */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.6);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
    animation: fadeIn 0.3s ease;
    font-family: 'Roboto', sans-serif;
    color: #fff;
}

/* Modal Content mit dunklem Hintergrund und neon-Hervorhebungen */
.modal-content {
    background: #111;
    padding: 2rem;
    border-radius: 12px;
    max-width: 700px;
    width: 90%;
    max-height: 80%;
    overflow-y: auto;
    box-shadow: 0 5px 20px rgba(0,0,0,0.7);
    animation: slideIn 0.3s ease;
}

/* Header im Modal */
.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.modal-header h2 {
    margin: 0;
    font-size: 1.8rem;
    color: #2ecc71;
    text-shadow: 0 0 10px #2ecc71;
}

.close-button {
    background: none;
    border: none;
    font-size: 1.8rem;
    cursor: pointer;
    color: #7f8c8d;
    transition: color 0.3s ease;
}

.close-button:hover {
    color: #2ecc71;
}

/* Grid für die Bilder */
.image-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 1.2rem;
}

.no-images {
    text-align: center;
    color: #ccc;
    font-size: 1rem;
}

/* Einzelne Bild-Items */
.image-item {
    border: 3px solid transparent;
    border-radius: 8px;
    cursor: pointer;
    transition: border-color 0.3s ease, transform 0.3s ease, box-shadow 0.3s;
    position: relative;
    overflow: hidden;
    background: #000;
    box-shadow: 0 5px 20px rgba(0,0,0,0.5);
}

.image-item:hover {
    border-color: #3498db;
    transform: translateY(-5px) scale(1.02);
    box-shadow: 0 15px 40px rgba(0,0,0,0.7);
}

.image-item.selected {
    border-color: #2ecc71;
    transform: translateY(-5px) scale(1.02);
    box-shadow: 0 15px 40px rgba(0,0,0,0.7);
}

.image-item img {
    width: 100%;
    height: 100%;
    border-radius: 8px;
    object-fit: cover;
}

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes slideIn {
    from { transform: translateY(-20px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}
</style>
