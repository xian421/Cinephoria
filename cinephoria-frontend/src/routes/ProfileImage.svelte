<script>
    export let src = '';
    export let alt = 'Profilbild';
  </script>
  
  <div class="profile-image-wrapper" on:click>
    <img src={src} alt={alt} />
  </div>
  
  <style>
    .profile-image-wrapper {
        width: 120px;
        height: 120px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        overflow: hidden;
        cursor: pointer;
        transition: transform 0.3s ease;
    }
  
    .profile-image-wrapper:hover {
        transform: scale(1.05);
    }
  
    .profile-image-wrapper img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
  </style>
  