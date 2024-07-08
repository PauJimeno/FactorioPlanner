class InputBlueprint extends Blueprint{
    constructor(rows, columns) {
        // Super class constructor call
        super(rows, columns);

        // Set of items that can be selected in the blueprint
        this.itemsList = new Set();

        // Initialize handlers
        this.sizeInputHandler();
        this.isOutputHandler();
        this.itemSelectionHandler();
    }

    resetGridInfo(){
        this.gridInformation = [];
        for(let i = 0; i < this.rows; i++){
            let row = [];
            for(let j = 0; j < this.columns; j++){
                let pos = this.getCellCenter(i, j);
                row.push(new InputCell(pos[0], pos[1]));
            }
            this.gridInformation.push(row);
        }
    }

    itemSelectionHandler(){
        let itemSelect = document.getElementById('item-selection');
        itemSelect.addEventListener('change', (event) => {
            this.gridInformation[this.selectedCellY][this.selectedCellX].itemCarrying = event.target.value;
        });
    }

    isOutputHandler(){
        let outputCheckbox = document.getElementById('is-output');
        outputCheckbox.addEventListener('change', (event) => {
            this.gridInformation[this.selectedCellY][this.selectedCellX].isOutput = event.target.checked;
        });
    }

    sizeInputHandler(){
        var rowsInput = document.getElementById('rows');
        var colsInput = document.getElementById('cols');

        rowsInput.addEventListener('change', () => {
            this.rows = parseInt(rowsInput.value);
            this.calculateGridSize(this.rows, this.columns);
            this.drawGrid(this.rows, this.columns, "#FFFFFF");
            this.resetGridInfo();

        });

        colsInput.addEventListener('change', () => {
            this.columns = parseInt(colsInput.value);
            this.calculateGridSize(this.rows, this.columns);
            this.drawGrid(this.rows, this.columns, "#FFFFFF");
            this.resetGridInfo();
        });
    }

    setItemsInUse(items){
        this.itemsList = items;
        let itemSelect = document.getElementById('item-selection');
        itemSelect.innerHTML = "";
        let defaultOption = document.createElement('option');
        defaultOption.value = "none";
        defaultOption.text = "No item";
        defaultOption.selected = true;
        itemSelect.appendChild(defaultOption);

        for (let item of this.itemsList) {
            let option = document.createElement('option');
            option.value = item;
            option.text = this.formatItemName(item);
            itemSelect.appendChild(option);
        }
    }

    inputItems(outputItem){
        let inOutPos = {'IN':{}, 'OUT':{}};
        for(let i = 0; i < this.rows; i++) {
            for (let j = 0; j < this.columns; j++) {
                let cell = this.gridInformation[i][j];
                let key = `(${i},${j})`;
                if (cell.isOutput) {
                    inOutPos['OUT'][key] = {'ITEM': outputItem};
                }
                else if(cell.itemCarrying !== 'none'){
                    inOutPos['IN'][key] = {'ITEM': cell.itemCarrying, "RATE": cell.itemAmount};
                }
            }
        }
        console.log(JSON.stringify(inOutPos));
        return inOutPos;
    }

}