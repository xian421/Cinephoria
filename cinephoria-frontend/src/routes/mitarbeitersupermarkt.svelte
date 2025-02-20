<!-- src/routes/mitarbeitersupermarkt.svelte -->
<script>
    import { onMount } from 'svelte';
    import { get } from 'svelte/store';
    import ProductList from '../components/ProductList.svelte';
    import ProductForm from '../components/ProductForm.svelte';
    import Modal from '../components/Modal.svelte';
    import { showSuccessAlert, showErrorAlert, showConfirmationDialog, showSuccessToast } from '../utils/notifications.js';
    import { productsStore, setProducts, addProductToStore, updateProductInStore } from '../stores/productStore.js';
    import { pfandStore, setPfandOptions } from '../stores/pfandStore.js';
    import { sortStore, updateSort } from '../stores/sortStore.js';
    import { loadAllProducts, loadPfandOptions, addProduct, updateProduct, deleteProduct } from '../services/productService.js';
    import { sortByDate, sortByNumeric, sortByString } from '../utils/sortStrategies.js';

    import { derived } from 'svelte/store';

    let newItem = { barcode: '', item_name: '', price: '', category: '', pfand_id: null };
    let isAdding = false;
    let showAddModal = false;
    let showEditModal = false;
    let editItem = null; 

    // Abgeleiteter Store für sortierte Produkte
    const sortedProductsStore = derived(
        [productsStore, pfandStore, sortStore],
        ([$productsStore, $pfandStore, $sortStore]) => {
            return sortProducts($productsStore, $sortStore.column, $sortStore.direction, $pfandStore);
        }
    );

    /**
     * Sortiert die Produkte basierend auf der Spalte und Richtung.
     * @param {Array} products - Die Liste der Produkte.
     * @param {String} column - Die Spalte, nach der sortiert werden soll.
     * @param {String} direction - 'asc' oder 'desc'.
     * @param {Array} pfandOptions - Liste der Pfand-Optionen.
     * @returns {Array} - Die sortierte Liste der Produkte.
     */
    function sortProducts(products, column, direction, pfandOptions) {
        if (!column) {
            return [...products];
        }

        // Sonderfall: Wenn nach pfand_id sortiert werden soll,
        // sortiere anhand des Pfandnamens.
        if (column === 'pfand_id') {
            return [...products].sort((a, b) => {
            const aPfand = pfandOptions.find(p => p.pfand_id === a[column]);
            const bPfand = pfandOptions.find(p => p.pfand_id === b[column]);
            const aName = aPfand ? aPfand.name : '';
            const bName = bPfand ? bPfand.name : '';
            return sortByString(aName, bName, direction);
            });
        }

        // Wähle die passende Strategie basierend auf der Spalte
        let strategy;

        // Für Datumsfelder
        if (column === 'created_at' || column === 'updated_at') {
            strategy = sortByDate;
        } else {
            // Prüfe anhand des ersten Elements, ob der Wert numerisch ist
            const firstValue = products[0][column];
            const isNumeric = !isNaN(parseFloat(firstValue)) && isFinite(firstValue);
            strategy = isNumeric ? sortByNumeric : sortByString;
        }

        // Wende die gewählte Strategie an
        return [...products].sort((a, b) => strategy(a[column], b[column], direction));
    }


    async function loadData() {
        try {
            const loadedProducts = await loadAllProducts();
            setProducts(loadedProducts);
            const loadedPfandOptions = await loadPfandOptions();
            setPfandOptions(loadedPfandOptions);
        } catch (error) {
            console.error('Fehler beim Laden der Daten:', error);
            showErrorAlert(error.message || 'Fehler beim Laden der Daten.');
        }
    }

    onMount(async () => {
        await loadData();
    });

    /**
     * Handhabt die Sortierung, wenn eine Spaltenüberschrift geklickt wird.
     * @param {String} column - Die Spalte, nach der sortiert werden soll.
     */
    function handleSort(column) {
        updateSort(column);
    }

    /**
     * Öffnet das Bearbeitungsmodal mit den Produktdaten.
     * @param {Object} product - Das zu bearbeitende Produkt.
     */
    function openEditModal(product) {
        editItem = { ...product };
        showEditModal = true;
    }

    /**
     * Schließt alle Modale.
     */
    function closeModal() {
        showAddModal = false;
        showEditModal = false;
        editItem = null;
    }

    /**
     * Handhabt das Hinzufügen eines neuen Produkts.
     * @param {CustomEvent} event - Das Submit-Event von ProductForm.
     */
    async function handleAddSubmit(event) {
        const product = event.detail.product;
        try {
            isAdding = true;
            const addedItem = await addProduct(product, get(pfandStore));
            addProductToStore(addedItem);
            // Sortierung wird automatisch durch den abgeleiteten Store angewendet

            // Setze das Formular zurück
            newItem = { barcode: '', item_name: '', price: '', category: '', pfand_id: null };
            showSuccessToast("Artikel erfolgreich hinzugefügt!");
            showAddModal = false; // Schließe das Modal
        } catch (error) {
            console.error('Fehler beim Hinzufügen des Artikels:', error);
            showErrorAlert(error.message || 'Fehler beim Hinzufügen des Artikels.');
        } finally {
            isAdding = false;
        }
    }

    /**
     * Handhabt das Aktualisieren eines bestehenden Produkts.
     * @param {CustomEvent} event - Das Submit-Event von ProductForm.
     */
    async function handleUpdateSubmit(event) {
        const product = event.detail.product;
        try {
            const updatedItem = await updateProduct(product, get(pfandStore));
            updateProductInStore(updatedItem);
            // Sortierung wird automatisch durch den abgeleiteten Store angewendet

            showSuccessToast("Artikel erfolgreich aktualisiert!");
            showEditModal = false; // Schließe das Modal
        } catch (error) {
            console.error('Fehler beim Aktualisieren des Artikels:', error);
            showErrorAlert(error.message || 'Fehler beim Aktualisieren des Artikels.');
        }
    }

    /**
     * Handhabt das Löschen eines Produkts.
     * @param {Number} item_id - Die ID des zu löschenden Produkts.
     */
   
     async function handleDelete(item_id) {
    try {
      await deleteProduct(item_id);
      setProducts(get(productsStore).filter(p => p.item_id !== item_id));
      showSuccessToast("Artikel erfolgreich gelöscht!");
    } catch (error) {
      console.error('Fehler beim Löschen des Artikels:', error);
      showErrorAlert(error.message || 'Fehler beim Löschen des Artikels.');
    }
  }

  // Zeigt einen Bestätigungsdialog und löscht das Produkt, falls bestätigt wird.
  async function handleDeleteWithConfirmation(item_id) {
    const result = await showConfirmationDialog("Produkt löschen", "Bist du sicher, dass du dieses Produkt löschen möchtest?");
    if (result.isConfirmed) {
      handleDelete(item_id);
    }
  }
</script>

<style>
    .title {
        font-size: 2.5rem;
        margin-bottom: 30px;
        font-weight: bold;
        margin-top: 0;
        text-align: center;
    }

    .container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        margin: 0 auto;
        width: 100%;
        max-width: 1200px;
        height: auto; 
        font-family: 'Arial', sans-serif;
        color: #333;
        position: relative; 
        padding-top: 60px; 
    }

    .header {
        width: 100%;
        display: flex;
        justify-content: center; 
        align-items: center;
        margin-bottom: 20px;
        position: relative; 
    }

    .add-button {
        position: absolute;
        right: 0;
        top: 0;
        padding: 10px 20px;
        font-size: 1rem;
        background-color: #28a745;
        color: #fff;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-weight: bold;
        transition: background-color 0.3s;
    }

    .add-button:hover {
        background-color: #218838;
    }

    .table-wrapper {
        width: 100%;
        overflow-x: hidden; 
    }
</style>

<div class="container">
    <div class="header">
        <h1 class="title">Alle Artikel</h1>
        <button class="add-button" on:click={() => showAddModal = true}>Produkt hinzufügen</button>
    </div>

    <div class="table-wrapper">
        <ProductList 
            products={$sortedProductsStore} 
            sortColumn={$sortStore.column} 
            sortDirection={$sortStore.direction}
            onSort={handleSort}
            onEdit={openEditModal}
            onDelete={handleDeleteWithConfirmation}
        />
    </div>

    {#if showAddModal}
        <Modal title="Neues Produkt hinzufügen" on:close={closeModal}>
            <ProductForm 
                product={newItem} 
                pfandOptions={$pfandStore} 
                on:submit={handleAddSubmit} 
                isSubmitting={isAdding}
            />
        </Modal>
    {/if}

    {#if showEditModal && editItem}
        <Modal title="Produkt bearbeiten" on:close={closeModal}>
            <ProductForm 
                product={editItem} 
                pfandOptions={$pfandStore} 
                on:submit={handleUpdateSubmit} 
                isSubmitting={false}
                isEditing={true}
            />
        </Modal>
    {/if}
</div>
