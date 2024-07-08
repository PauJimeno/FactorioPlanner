class ConveyorCell extends Cell{
    constructor(direction, itemCarrying, inputFlow, outputFlow, x, y) {
        super(x, y, 'conveyor');
        this.description = 'conveyor';
        this.dir = direction;
        this.itemCarrying = itemCarrying;
        this.inputFlow = inputFlow;
        this.outputFlow = outputFlow;
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