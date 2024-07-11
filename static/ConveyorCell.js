class ConveyorCell extends Cell{
    constructor(direction, itemCarrying, inputFlow, outputFlow, routeValue, x, y) {
        super(x, y, 'conveyor');
        this.dir = direction;
        this.itemCarrying = itemCarrying;
        this.inputFlow = inputFlow;
        this.outputFlow = outputFlow;
        this.routeValue = routeValue;
    }

    updateCellInfo() {
        let infoDiv = document.getElementById('selected-cell-info');

        infoDiv.innerHTML = '';

        infoDiv.appendChild(this.createInfoElement('Description', `${this.formatItemName(this.dir)} facing conveyor`));
        infoDiv.appendChild(this.createInfoElement('Cell Item Flow', `The conveyor is transporting ${this.formatItemName(this.itemCarrying)} at a rate of:\nIn: ${this.inputFlow} per minute\nOut: ${this.outputFlow} per minute`));
        infoDiv.appendChild(this.createInfoElement('Route Value', this.routeValue != '1'? this.routeValue: `${this.routeValue} (blueprint input)`));
    }

    draw(sprite, itemSprite, canvas, rows, cols){
        let context = canvas.getContext('2d');
        let tolerance = 1;
        let width = canvas.width/cols + (canvas.width/cols)*tolerance;
        let height = canvas.height/rows + (canvas.height/rows)*tolerance;
        context.drawImage(sprite, this.x - width / 2, this.y - height / 2, width, height);

        this.drawItem(itemSprite, canvas, canvas.width/cols);
    }
}