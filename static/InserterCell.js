class InserterCell extends Cell{
    constructor(direction, itemCarrying, inputFlow, outputFlow, x, y) {
        super(x, y, 'inserter');
        this.description = 'inserter';
        this.dir = direction;
        this.itemCarrying = itemCarrying;
        this.inputFlow = inputFlow;
        this.outputFlow = outputFlow;
    }

    updateCellInfo() {
        // Select the div
        let infoDiv = document.getElementById('selected-cell-info');

        // Clear the previous information
        infoDiv.innerHTML = '';

        // Load the cell information into the div
        infoDiv.innerHTML = this.description;
    }

    draw(image_src, canvas, rows, cols){
        let context = canvas.getContext('2d');
        var img = new Image();
        img.onload = () => {
            // Draw the image at the center of the cell, adjusting for the image's size
            context.drawImage(img, this.x - img.width / 2, this.y - img.height / 2,);
        }
        img.src = image_src;
    }
}