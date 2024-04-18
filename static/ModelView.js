class ModelView{
    constructor(rows, columns){
         this.canvas = document.getElementById('model-view');
         this.context = this.canvas.getContext('2d');

    }
    drawGrid(rows, cols, color) {
        this.context.beginPath();
        var rowHeight = this.canvas.height / rows;
        var colWidth = this.canvas.width / cols;

        // Draw horizontal grid lines
        for (var i = 0; i <= rows; i++) {
            this.context.moveTo(0, i * rowHeight);
            this.context.lineTo(this.canvas.width, i * rowHeight);
        }

        // Draw vertical grid lines
        for (var j = 0; j <= cols; j++) {
            this.context.moveTo(j * colWidth, 0);
            this.context.lineTo(j * colWidth, this.canvas.height);
        }

        this.context.strokeStyle = color;
        this.context.stroke();
    }
}