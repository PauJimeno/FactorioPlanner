class ModelView{
    constructor(rows, columns){
         this.canvas = document.getElementById('model-view');
         this.context = this.canvas.getContext('2d');
         this.rows = rows;
         this.columns = columns;
         this.sizeInputHandler();
         this.calculateGridSize(this.rows, this.columns);

         this.drawGrid(this.rows, this.columns, "#FFFFFF");
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

    sizeInputHandler(){
        var rowsInput = document.getElementById('rows');
        var colsInput = document.getElementById('cols');

        rowsInput.addEventListener('change', () => {
            this.rows = parseInt(rowsInput.value);
            this.calculateGridSize(this.rows, this.columns);
            this.drawGrid(this.rows, this.columns, "#FFFFFF");
        });

        colsInput.addEventListener('change', () => {
            this.columns = parseInt(colsInput.value);
            this.calculateGridSize(this.rows, this.columns);
            this.drawGrid(this.rows, this.columns, "#FFFFFF");
        });
    }

    drawGrid(rows, cols, color) {
        this.context.beginPath();
        var rowHeight = this.height / rows;
        var colWidth = this.width / cols;

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
}
