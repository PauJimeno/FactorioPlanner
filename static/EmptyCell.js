class EmptyCell extends Cell{
    constructor(x, y) {
        super(x, y, 'empty');
        this.description = 'An empty cell (nothing to see here)';
    }

    updateCellInfo() {
        // Select the div
        let infoDiv = document.getElementById('selected-cell-info');

        // Clear the previous information
        infoDiv.innerHTML = '';

        // Load the cell information into the div
        infoDiv.innerHTML = this.description;
    }
}