class Blueprint {
    constructor(rows, columns){
        if (new.target === Blueprint) {
            throw new TypeError("Cannot construct Blueprint instances directly");
        }

        this.canvas = document.getElementById('model-view');
        this.context = this.canvas.getContext('2d');
        this.rows = rows;
        this.columns = columns;
        this.selectedCellX = columns-1;
        this.selectedCellY = rows-1;
        this.gridInformation = [];

        this.calculateGridSize(this.rows, this.columns);
        this.drawSelectedOutline();
        this.resetGridInfo();

    }

    resetGridInfo(){
        this.gridInformation = [];
        for(let i = 0; i < this.rows; i++){
            let row = [];
            for(let j = 0; j < this.columns; j++){
                row.push(new CellInfo());
            }
            this.gridInformation.push(row);
        }
    }

    calculateGridSize(rows, columns){
        var cellSize = Math.min(500 / Math.max(rows, columns));

        this.width = cellSize * columns;
        this.height = cellSize * rows;

        this.canvas.style.width = (cellSize * columns) + 'px';
        this.canvas.style.height = (cellSize * rows) + 'px';

        this.canvas.width = this.width;
        this.canvas.height = this.height;
    }

    handleCellClick(event) {
       throw new Error('You have to implement the method handleCellClick!');
    }

    updateSelectedCell(event){
        var rect = this.canvas.getBoundingClientRect();
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

        this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.drawGrid(this.rows, this.columns, "#FFFFFF");

        this.context.beginPath();
        this.context.rect(this.selectedCellX * cellWidth, this.selectedCellY * cellHeight, cellWidth, cellHeight);
        this.context.lineWidth = 4; // Change this to make the border thicker or thinner
        this.context.strokeStyle = "#FFFFFF"; // Change this to change the border color
        this.context.stroke();
    }

    updateCellInfo(){
        throw new Error('You have to implement the method updateCellInfo!');
    }

    drawGrid(rows, cols, color) {
        this.context.beginPath();
        var rowHeight = this.height / rows;
        var colWidth = this.width / cols;
        this.context.lineWidth = 1;
        // Draw horizontal grid lines
        for (var i = 0; i <= rows; i++) {
            this.context.moveTo(0, i * rowHeight);
            this.context.lineTo(this.width, i * rowHeight);
        }

        // Draw vertical grid lines
        for (var j = 0; j <= cols; j++) {
            this.context.moveTo(j * colWidth, 0);
            this.context.lineTo(j * colWidth, this.height);
        }

        this.context.strokeStyle = color;
        this.context.stroke();
    }

    drawInstanceImage(instance_image){
        var img = new Image();
        img.onload = () => {
            this.context.drawImage(img, 0, 0, this.width, this.height);
        }
        img.src = instance_image;
    }

    formatItemName(itemName){
        return itemName.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
    }
}
