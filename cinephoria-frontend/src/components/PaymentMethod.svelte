<!-- src/components/PaymentMethod.svelte -->
<script>
    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher();
  
    export let method = 'Bar';
    const options = ['Bar', 'Kreditkarte', 'Debitkarte', 'PayPal', 'Andere'];
  
    function handleChange(event) {
      const selected = event.target.value;
      dispatch('change', { method: selected });
    }
  </script>
  
  <div class="payment-method">
    <label for="payment">Zahlungsmethode:</label>
    <select id="payment" bind:value={method} on:change={handleChange}>
      {#each options as option}
        <option value={option}>{option}</option>
      {/each}
    </select>
  </div>
  
  <style>
    .payment-method {
      margin-top: 20px;
      text-align: center;
    }
    .payment-method label {
      margin-right: 10px;
    }
  </style>
  