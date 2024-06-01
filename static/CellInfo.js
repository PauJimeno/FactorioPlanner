class CellInfo{
    constructor(itemList) {
        this.itemList = itemList; // Reference to the items that can be used in the blueprint
        this.itemCarrying = 'none'; // Cell carrying item
        this.solvedInstance = false; // Flag for cells that are part of a solved instance
        this.itemAmount = 0; // Amount of items the call carries
        this.isOutput = false;
    }
}