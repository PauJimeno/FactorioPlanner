class ConveyorCell extends Cell{
    constructor(direction, itemCarrying, inputFlow, outputFlow, routeValue, x, y) {
        super(x, y, 'conveyor');
        this.dir = direction;
        this.itemCarrying = itemCarrying;
        this.inputFlow = inputFlow;
        this.outputFlow = outputFlow;
        this.routeValue = routeValue;
        this.routeStatus = 'nothing';
    }

    updateCellInfo() {
        let infoDiv = document.getElementById('selected-cell-info');

        infoDiv.innerHTML = '';

        infoDiv.appendChild(this.createInfoElement('Description', `${this.formatItemName(this.dir)} facing conveyor`));
        infoDiv.appendChild(this.createInfoElement('Cell Item Flow', `The conveyor is transporting ${this.formatItemName(this.itemCarrying)} at a rate of:\nIn: ${this.inputFlow} per minute\nOut: ${this.outputFlow} per minute`));
        let statusText = '';
        if(this.routeStatus != 'nothing') statusText = `(blueprint ${this.routeStatus})`;
        infoDiv.appendChild(this.createInfoElement('Route Value', `${this.routeValue} ${statusText}`));
    }

    draw(sprite, itemSprite, canvas, rows, cols){
        let context = canvas.getContext('2d');
        let tolerance = 1;
        let width = canvas.width/cols + (canvas.width/cols)*tolerance;
        let height = canvas.height/rows + (canvas.height/rows)*tolerance;
        context.drawImage(sprite, this.x - width / 2, this.y - height / 2, width, height);

        this.drawItem(itemSprite, canvas, canvas.width/cols);

        if(this.routeStatus != 'nothing'){
            let sprite = new Image();
            sprite.src = `static/blueprint_sprites/utilities/${this.dir}-${this.routeStatus}.png`;
            sprite.onload = () => {
                super.draw(sprite, canvas, rows, cols);
            };
        }

    }
}