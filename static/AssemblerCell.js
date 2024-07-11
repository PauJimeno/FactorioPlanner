class AssemblerCell extends Cell{
    constructor(itemProducing, x, y) {
        super(x, y, 'assembler');
        this.description = 'assembler';
        this.itemProducing = itemProducing;
        this.isDrawn = false;
        this.inputItems = {};
        this.outputItem = {};
    }

    updateCellInfo() {
        let infoDiv = document.getElementById('selected-cell-info');

        infoDiv.innerHTML = '';

        infoDiv.appendChild(this.createInfoElement('Description', `Assembler producing ${this.formatItemName(this.itemProducing)}`));
        //infoDiv.appendChild(this.createInfoElement('Input/Output', `The conveyor is transporting ${this.formatItemName(this.itemCarrying)} at a rate of:\nIn: ${this.inputFlow} per minute\nOut: ${this.outputFlow} per minute`));
        // infoDiv.appendChild(this.createInfoElement('Route Value', this.routeValue != '1'? this.routeValue: `${this.routeValue} (blueprint input)`));
    }

    draw(sprite, itemSprite, canvas, rows, cols){
        if(!this.isDrawn){
            let context = canvas.getContext('2d');
            let tolerance = 0.15;
            let width = (canvas.width/cols)*3 + (canvas.width/cols)*tolerance*3;
            let height = (canvas.height/rows)*3 + (canvas.height/rows)*tolerance*3;
            context.drawImage(sprite, this.x - width / 2, this.y - height / 2, width, height);
            this.drawItem(itemSprite, canvas, canvas.width/cols);
        }
    }

    drawItem(itemSprite, canvas, cellSize){
        let context = canvas.getContext('2d');
        context.drawImage(itemSprite, this.x - cellSize/2, this.y - cellSize/2, cellSize, cellSize);
    }
}