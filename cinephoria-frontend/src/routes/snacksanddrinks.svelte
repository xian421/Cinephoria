<script> 
    import { onMount } from "svelte";
  
    let loading = true;
    let activeCategory = "bundles";
  
    const categories = [
      { id: "bundles", name: "Bundles", emoji: "🎁" },
      { id: "snacks", name: "Snacks", emoji: "🍿" },
      { id: "drinks", name: "Getränke", emoji: "🥤" },
    ];
  
    const bundles = [
      {
        name: "Familien Bundle",
        price: "24.99",
        items: ["2x Große Popcorn", "4x Softdrink 0.5L", "2x Nachos mit Käsedip"],
        description: "Das perfekte Paket für den Familienfilmabend!",
        image: "/BilderfürSnacks/familybundle.webp",
      },
      {
        name: "Romantik Bundle",
        price: "19.99",
        items: ["1x Große Popcorn süß", "2x Prosecco 0.2L", "1x Snack-Mix"],
        description: "Ideal für einen gemütlichen Abend zu zweit",
        image: "/BilderfürSnacks/paarbundle.webp",
      },
    ];
  
    const snacks = [
      {
        name: "Popcorn süß",
        sizes: ["Klein 3.50€", "Mittel 4.50€", "Groß 5.50€"],
        image: "/BilderfürSnacks/SüßesPopcorn.webp",
      },
      {
        name: "Popcorn salzig",
        sizes: ["Klein 3.50€", "Mittel 4.50€", "Groß 5.50€"],
        image: "/BilderfürSnacks/SalzigesPopcorn.webp",
      },
      {
        name: "Nachos mit Käsedip",
        price: "4.99€",
        image: "/BilderfürSnacks/NatchosmitKäse.webp",
      },
    ];
  
    const drinks = [
      {
        name: "Getränke Übersicht",
        image: "/BilderfürSnacks/getränke.webp",
        description: "Alle verfügbaren Getränke in verschiedenen Größen.",
      },
      { name: "Coca-Cola", sizes: ["0.3L 3.50€", "0.5L 4.50€", "0.75L 5.50€"] },
      { name: "Sprite", sizes: ["0.3L 3.50€", "0.5L 4.50€", "0.75L 5.50€"] },
      { name: "Fanta", sizes: ["0.3L 3.50€", "0.5L 4.50€", "0.75L 5.50€"] },
      { name: "Mineralwasser", sizes: ["0.3L 2.50€", "0.5L 3.50€"] },
      { name: "Sekt", sizes: ["0.2L 4.00€", "0.5L 8.00€"] },
    ];
  
    onMount(() => {
      setTimeout(() => {
        loading = false;
      }, 1000);
    });
  </script>
  
  {#if loading}
    <div class="min-h-screen flex items-center justify-center bg-gradient-to-b from-[#0a192f] to-[#112240] text-white">
      <h2 class="text-2xl font-bold text-[#4ade80]">Lade Snacks & Drinks...</h2>
    </div>
  {:else}
    <div class="min-h-screen bg-gradient-to-b from-[#0a192f] to-[#112240] text-white">
      <div class="container mx-auto px-6 py-16 max-w-6xl">
        <div class="text-center mb-12">
          <h1 class="text-5xl font-extrabold text-[#4ade80] glow">Snacks & Drinks</h1>
          <p class="text-lg text-gray-300 mt-2">Genieße dein Kinoerlebnis mit leckeren Snacks und Getränken</p>
        </div>
  
        <div class="flex justify-center space-x-6 mb-20">
          {#each categories as category}
            <button
              on:click={() => (activeCategory = category.id)}
              class="category-button px-6 py-3 rounded-full text-lg font-semibold transition-all duration-300 
              {activeCategory === category.id ? 'bg-[#4ade80] text-black' : 'bg-white/10 text-white hover:bg-white/20'}">
              <span class="mr-2">{category.emoji}</span>{category.name}
            </button>
          {/each}
        </div>
  
        {#if activeCategory === "bundles"}
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-16 mt-8">
            {#each bundles as bundle}
              <div class="card">
                <div class="image-container">
                  <img src={bundle.image} alt={bundle.name} class="bundle-image" />
                </div>
                <h3 class="text-2xl font-bold text-[#4ade80] mb-2">{bundle.name}</h3>
                <p class="text-gray-400 mb-4">{bundle.description}</p>
                <ul class="text-gray-300 space-y-1 list-none">
                  {#each bundle.items as item}
                    <li class="text-base">{item}</li>
                  {/each}
                </ul>
                <p class="text-xl font-bold text-[#4ade80] mt-4">{bundle.price}€</p>
              </div>
            {/each}
          </div>
        {/if}
  
        {#if activeCategory === "snacks"}
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-16 mt-8">
            {#each snacks as snack}
              <div class="card">
                <div class="image-container">
                  <img src={snack.image} alt={snack.name} class="bundle-image" />
                </div>
                <h3 class="text-2xl font-bold text-[#4ade80] mb-2">{snack.name}</h3>
                {#if snack.sizes}
                  <ul class="text-gray-300 space-y-1 list-none">
                    {#each snack.sizes as size}
                      {#if size.trim() !== ""}
                        <li class="text-base">{size}</li>
                      {/if}
                    {/each}
                  </ul>
                {:else}
                  <p class="text-lg font-bold text-[#4ade80]">{snack.price}</p>
                {/if}
              </div>
            {/each}
          </div>
        {/if}
  
        {#if activeCategory === "drinks"}
          <div class="card mb-12 mt-8">
            <div class="image-container">
              <img src={drinks[0].image} alt={drinks[0].name} class="bundle-image" />
            </div>
            <p class="text-gray-400 mb-4">{drinks[0].description}</p>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mt-8">
            {#each drinks.slice(1) as drink}
              <div class="card p-4">
                <h3 class="text-2xl font-bold text-[#4ade80] mb-2">{drink.name}</h3>
                <ul class="text-gray-300 space-y-1 list-none">
                  {#each drink.sizes as size}
                    {#if size.trim() !== ""}
                      <li class="text-base">{size}</li>
                    {/if}
                  {/each}
                </ul>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    </div>
  {/if}
  
  <style>
    :global(body) {
      margin: 0;
      font-family: "Inter", sans-serif;
      background: linear-gradient(to bottom, #0a192f, #112240);
    }
  
    li:empty {
      display: none;
    }
  
    .glow {
      text-shadow: 0 0 15px rgba(74, 222, 128, 0.7);
    }
  
    .card {
      background: rgba(255, 255, 255, 0.1);
      border: 1px solid rgba(255, 255, 255, 0.2);
      border-radius: 12px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
      padding: 20px;
      margin-bottom: 32px;
      transition: transform 0.3s ease, box-shadow 0.3s ease;
      text-align: center;
    }
  
    .card:hover {
      transform: translateY(-5px);
      box-shadow: 0 6px 30px rgba(0, 0, 0, 0.7);
    }
  
    .image-container {
      width: 100%;
      height: 250px;
      overflow: hidden;
      border-radius: 12px;
      margin-bottom: 16px;
    }
  
    .bundle-image {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }
  
    .category-button {
      margin: 0 8px;
    }
  
    .category-button:hover {
      transform: scale(1.05);
    }

    /* Entfernen der Aufzählungspunkte */
    ul.list-none {
      list-style: none;
      padding-left: 0;
    }

    /* Hinzufügen von vertikalem Abstand */
    .mt-8 {
      margin-top: 2rem; /* 32px */
    }
  </style>
