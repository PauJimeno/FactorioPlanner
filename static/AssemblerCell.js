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
        infoDiv.append(this.createInfoElementWithDictionary('Inputs', this.inputItems));
        infoDiv.append(this.createInfoElementWithDictionary('Output', this.outputItem));
        infoDiv.append(this.createInfoElementWithDictionary('Input to output ratios', this.calculateRatios(this.inputItems, this.outputItem)));
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

    createInfoElementWithDictionary(titleText, dict) {
        let infoDiv = document.createElement('div');
        let title = document.createElement('h3');
        title.textContent = titleText;
        let list = document.createElement('ul');
        list.style.marginLeft = '20px';

        for(let key in dict) {
            let listItem = document.createElement('li');
            listItem.innerHTML = `${this.formatItemName(key)}: ${dict[key]}`;
            list.appendChild(listItem);
        }

        infoDiv.appendChild(title);
        infoDiv.appendChild(list);

        return infoDiv;
    }

    calculateRatios(inputItems, outputItem) {
        let itemRatios = {};
        let outputQuantity = Object.values(outputItem)[0];

        for(let key in inputItems) {
            let ratio = inputItems[key] / outputQuantity;
            itemRatios[key] = `${ratio}:1`;
        }

        return itemRatios;
    }

    drawSelectedOutline(canvas, rows, columns){
        var cellWidth = canvas.width / columns;
        var cellHeight = canvas.height / rows;
        var context = canvas.getContext('2d');
        context.clearRect(0, 0, canvas.width, canvas.height);

        var selectedCellX = Math.floor(this.x / cellWidth);
        var selectedCellY = Math.floor(this.y / cellHeight);

        // Calculate the start point for the 3x3 cell
        var startX = (selectedCellX - 1) * cellWidth;
        var startY = (selectedCellY - 1) * cellHeight;

        // Draw the outline for the 3x3 cell
        context.beginPath();
        context.rect(startX, startY, cellWidth * 3, cellHeight * 3);
        context.lineWidth = 4; // Change this to make the border thicker or thinner
        context.strokeStyle = "#FFFFFF"; // Change this to change the border color
        context.stroke();
    }
}