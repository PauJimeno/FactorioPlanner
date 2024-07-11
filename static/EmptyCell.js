class EmptyCell extends Cell{
    constructor() {
        super(0, 0, 'empty');
        this.description = 'An empty cell (nothing to see here)';
        this.isDrawable = false;
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