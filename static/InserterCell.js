class InserterCell extends Cell{
    constructor(direction, itemCarrying, inputFlow, outputFlow, routeValue, x, y) {
        super(x, y, 'inserter');
        this.description = 'inserter';
        this.dir = direction;
        this.itemCarrying = itemCarrying;
        this.inputFlow = inputFlow;
        this.outputFlow = outputFlow;
        this.itemSprite = new Image();
        this.itemSprite.src = `static/RecipeIcons/${itemCarrying}.png`;
        this.routeValue = routeValue;
    }

    updateCellInfo() {
        let infoDiv = document.getElementById('selected-cell-info');

        infoDiv.innerHTML = '';

        infoDiv.appendChild(this.createInfoElement('Description', `${this.formatItemName(this.dir)} facing inserter`));
        infoDiv.appendChild(this.createInfoElement('Cell Item Flow', `The conveyor is transporting ${this.formatItemName(this.itemCarrying)} at a rate of:\nIn: ${this.inputFlow} per minute\nOut: ${this.outputFlow} per minute`));
        infoDiv.appendChild(this.createInfoElement('Route Value', this.routeValue));
    }

    draw(sprite, itemSprite, canvas, rows, cols){
        let context = canvas.getContext('2d');
        let tolerance = 1.5;
        let cellWidth = canvas.width/cols;
        let spriteAspectRatio = sprite.width / sprite.height;

        let width, height;
        width = cellWidth * tolerance;
        height = width / spriteAspectRatio;


        // Calculate the position to center the sprite in the cell
        let x = this.x - width / 2;
        let y = this.y - height / 2;

        context.drawImage(sprite, x, y, width, height);
        this.drawItem(itemSprite, canvas, canvas.width/cols);
    }
}