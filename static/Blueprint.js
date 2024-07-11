class Blueprint {
    constructor(rows, columns){
        if (new.target === Blueprint) {
            throw new TypeError("Cannot construct Blueprint instances directly");
        }

        this.spriteCanvas = document.getElementById('model-view');
        this.spriteContext = this.spriteCanvas.getContext('2d');

        this.cursorCanvas = document.getElementById('cursor-canvas');
        this.cursorContext = this.cursorCanvas.getContext('2d');

        this.rows = rows;
        this.columns = columns;
        this.selectedCellX = columns-1;
        this.selectedCellY = rows-1;
        this.gridInformation = [];

        this.calculateGridSize(this.rows, this.columns);
        this.drawGrid(this.rows, this.columns, "#FFFFFF");
        this.drawSelectedOutline();

        this.cursorCanvas.addEventListener('click', (event) => this.handleCellClick(event));
    }

    resetGridInfo(){
        throw new Error('You have to implement the method resetGridInfo!');
    }

    calculateGridSize(rows, columns){
        var cellSize = Math.min(500 / Math.max(rows, columns));

        this.width = cellSize * columns;
        this.height = cellSize * rows;

        this.spriteCanvas.style.width = (cellSize * columns) + 'px';
        this.spriteCanvas.style.height = (cellSize * rows) + 'px';
        this.cursorCanvas.style.width = (cellSize * columns) + 'px';
        this.cursorCanvas.style.height = (cellSize * rows) + 'px';

        this.spriteCanvas.width = this.width;
        this.spriteCanvas.height = this.height;
        this.cursorCanvas.width = this.width;
        this.cursorCanvas.height = this.height;
    }

    getCellCenter(x, y) {
        var cellWidth = this.width / this.columns;
        var cellHeight = this.height / this.rows;

        var centerX = x * cellWidth + cellWidth / 2;
        var centerY = y * cellHeight + cellHeight / 2;

        return [centerY, centerX];
    }

    handleCellClick(event) {
        // Update the position of the current selected cell
        this.updateSelectedCell(event);

        // Outline the selected cell in the blueprint
        this.drawSelectedOutline();

        // Update the cell information
        this.gridInformation[this.selectedCellY][this.selectedCellX].updateCellInfo();
    }

    updateSelectedCell(event){
        var rect = this.cursorCanvas.getBoundingClientRect();
        var x = event.clientX - rect.left;
        var y = event.clientY - rect.top;

        var cellWidth = this.width / this.columns;
        var cellHeight = this.height / this.rows;

        this.selectedCellX = Math.floor(x / cellWidth);
        this.selectedCellY = Math.floor(y / cellHeight);
    }

    drawSelectedOutline(){
        var cellWidth = this.width / this.columns;
        var cellHeight = this.height / this.rows;

        this.cursorContext.clearRect(0, 0, this.cursorCanvas.width, this.cursorCanvas.height);

        this.cursorContext.beginPath();
        this.cursorContext.rect(this.selectedCellX * cellWidth, this.selectedCellY * cellHeight, cellWidth, cellHeight);
        this.cursorContext.lineWidth = 4; // Change this to make the border thicker or thinner
        this.cursorContext.strokeStyle = "#FFFFFF"; // Change this to change the border color
        this.cursorContext.stroke();
    }

    drawGrid(rows, cols, color) {
        this.spriteContext.beginPath();
        var rowHeight = this.height / rows;
        var colWidth = this.width / cols;
        this.spriteContext.lineWidth = 1;
        // Draw horizontal grid lines
        for (var i = 0; i <= rows; i++) {
            this.spriteContext.moveTo(0, i * rowHeight);
            this.spriteContext.lineTo(this.width, i * rowHeight);
        }

        // Draw vertical grid lines
        for (var j = 0; j <= cols; j++) {
            this.spriteContext.moveTo(j * colWidth, 0);
            this.spriteContext.lineTo(j * colWidth, this.height);
        }

        this.spriteContext.strokeStyle = color;
        this.spriteContext.stroke();
    }

    drawInstanceImage(instance_image){
        var img = new Image();
        img.onload = () => {
            this.spriteContext.drawImage(img, 0, 0, this.width, this.height);
        }
        img.src = instance_image;
    }

    formatItemName(itemName){
        return itemName.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
    }
}
