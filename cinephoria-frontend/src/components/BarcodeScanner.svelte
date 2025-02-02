<!-- src/components/BarcodeScanner.svelte -->
<script>
    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher();
  
    export let value = '';
    export let placeholder = 'Barcode eingeben';
  
    function handleKeydown(event) {
      if(event.key === 'Enter'){
        dispatch('scan', { barcode: value });
      }
    }
  
    function handleClick() {
      dispatch('scan', { barcode: value });
    }
  </script>
  
  <div class="scanner">
    <input 
      type="text" 
      bind:value 
      {placeholder}
      on:keydown={handleKeydown} 
    />
    <button on:click={handleClick}>Abschicken</button>
  </div>
  
  <style>
    .scanner {
      display: flex;
      flex-direction: column;
      align-items: center;
      margin-bottom: 30px;
    }
    .scanner input {
      width: 300px;
      padding: 10px;
      font-size: 1rem;
      border: 1px solid #ddd;
      border-radius: 5px;
      margin-bottom: 10px;
    }
    .scanner button {
      padding: 10px 20px;
      font-size: 1rem;
      background-color: #007bff;
      color: #fff;
      border: none;
      border-radius: 5px;
      cursor: pointer;
      transition: background-color 0.3s;
    }
    .scanner button:hover {
      background-color: #0056b3;
    }
  </style>
  