// src/strategy/SortStrategy.js
export class SortStrategy {
    sort(a, b, direction) {
      throw new Error('sort() muss in der konkreten Strategie überschrieben werden.');
    }
  }
  
  export class DateSortStrategy extends SortStrategy {
    sort(a, b, direction) {
      const aDate = new Date(a);
      const bDate = new Date(b);
      return direction === 'asc'
        ? aDate.getTime() - bDate.getTime()
        : bDate.getTime() - aDate.getTime();
    }
  }
  
  export class NumericSortStrategy extends SortStrategy {
    sort(a, b, direction) {
      return direction === 'asc'
        ? parseFloat(a) - parseFloat(b)
        : parseFloat(b) - parseFloat(a);
    }
  }
  
  export class TextSortStrategy extends SortStrategy {
    sort(a, b, direction) {
      const aText = a.toString().toLowerCase();
      const bText = b.toString().toLowerCase();
      if (aText < bText) return direction === 'asc' ? -1 : 1;
      if (aText > bText) return direction === 'asc' ? 1 : -1;
      return 0;
    }
  }
  
  export class PfandSortStrategy extends SortStrategy {
    constructor(pfandOptions) {
      super();
      this.pfandOptions = pfandOptions;
    }
    sort(a, b, direction) {
      // a und b sind hier Pfand-IDs
      const aPfand = this.pfandOptions.find(p => p.pfand_id === a) || { name: '' };
      const bPfand = this.pfandOptions.find(p => p.pfand_id === b) || { name: '' };
      const aName = aPfand.name.toLowerCase();
      const bName = bPfand.name.toLowerCase();
      if (aName < bName) return direction === 'asc' ? -1 : 1;
      if (aName > bName) return direction === 'asc' ? 1 : -1;
      return 0;
    }
  }
  