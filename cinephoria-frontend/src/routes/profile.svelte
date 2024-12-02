<script>
    export let userProfile = {
      name: "Max Mustermann",
      email: "max.mustermann@example.com",
      phone: "+49 123 456789",
      address: "Musterstraße 1, 12345 Musterstadt",
      joinedDate: "01.01.2023",
      profileImage: "/profile-image.jpg",
    };
  </script>
  
  <style>
    /* Gesamtcontainer */
    .profile-container {
      max-width: 800px;
      margin: 2rem auto;
      padding: 2rem;
      background: linear-gradient(145deg, #ffffff, #f8f9fa);
      border-radius: 12px;
      box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
      font-family: Arial, sans-serif;
    }
  
    /* Profilüberschrift */
    .profile-header {
      display: flex;
      align-items: center;
      gap: 1rem;
      margin-bottom: 2rem;
    }
  
    .profile-header img {
      width: 100px;
      height: 100px;
      border-radius: 50%;
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
  
    .profile-header h1 {
      font-size: 2rem;
      color: #333;
      margin: 0;
    }
  
    .profile-header p {
      font-size: 1rem;
      color: #555;
      margin: 0;
    }
  
    /* Profilinformationen */
    .profile-info {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1rem;
    }
  
    .profile-info div {
      background: #ffffff;
      padding: 1rem;
      border-radius: 8px;
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
  
    .profile-info div h3 {
      font-size: 1.2rem;
      color: #333;
      margin-bottom: 0.5rem;
    }
  
    .profile-info div p {
      font-size: 1rem;
      color: #555;
      margin: 0;
    }
  
    /* Buttons */
    .profile-actions {
      display: flex;
      justify-content: space-between;
      gap: 1rem;
      margin-top: 2rem;
    }
  
    .profile-actions button {
      font-size: 1rem;
      font-weight: bold;
      color: #ffffff;
      background: #3498db;
      border: none;
      border-radius: 8px;
      padding: 0.8rem 1.5rem;
      cursor: pointer;
      transition: background 0.3s ease;
    }
  
    .profile-actions button:hover {
      background: #24b497;
    }
  </style>
  
  <div class="profile-container">
    <!-- Profilüberschrift -->
    <div class="profile-header">
      <img src={userProfile.profileImage} alt="Profilbild" />
      <div>
        <h1>{userProfile.name}</h1>
        <p>{userProfile.email}</p>
      </div>
    </div>
  
    <!-- Profilinformationen -->
    <div class="profile-info">
      <div>
        <h3>Telefonnummer</h3>
        <p>{userProfile.phone}</p>
      </div>
      <div>
        <h3>Adresse</h3>
        <p>{userProfile.address}</p>
      </div>
      <div>
        <h3>Mitglied seit</h3>
        <p>{userProfile.joinedDate}</p>
      </div>
      <div>
        <h3>Weitere Informationen</h3>
        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis vel nulla nec urna.</p>
      </div>
    </div>
  
    <!-- Aktionen -->
    <div class="profile-actions">
      <button on:click={() => navigate('/edit-profile')}>Profil bearbeiten</button>
      <button on:click={() => navigate('/logout')}>Abmelden</button>
    </div>
  </div>
  