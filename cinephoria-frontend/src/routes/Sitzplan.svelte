<div class="seat-map">
    <div class="row" data-row="A">
      <div class="seat" data-seat="1"></div>
      <div class="seat reserved" data-seat="2"></div>
      <div class="seat" data-seat="3"></div>
      <div class="seat" data-seat="4"></div>
    </div>
    <div class="row" data-row="B">
      <div class="seat" data-seat="1"></div>
      <div class="seat reserved" data-seat="2"></div>
      <div class="seat" data-seat="3"></div>
      <div class="seat" data-seat="4"></div>
    </div>
  </div>

<style>
  .seat-map {
    display: grid;
    gap: 10px;
  }
  
  .row {
    display: flex;
    justify-content: center;
  }
  
  .seat {
    width: 30px;
    height: 30px;
    background-color: #2b6802;
    border-radius: 5px;
    cursor: pointer;
  }
  
  .seat.reserved {
    background-color: #f44336;
    cursor: not-allowed;
  }
  
  .seat:hover:not(.reserved) {
    background-color: #ffeb3b;
  }
</style>