class InputCell extends Cell{
    constructor(x, y) {
        super(x, y, 'input');
        this.itemCarrying = 'none';
        this.isOutput = false;
    }

    updateCellInfo(){
        // Load the cell information into the selection
        document.getElementById('item-selection').value = this.itemCarrying;

        // Load the cell information into the checkbox
        document.getElementById('is-output').checked = this.isOutput;
    }


}