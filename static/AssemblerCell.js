class AssemblerCell extends Cell{
    constructor(itemProducing, x, y) {
        super(x, y, 'assembler');
        this.description = 'assembler';
        this.itemProducing = itemProducing;
        this.isDrawn = false;
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
        if(!this.isDrawn){
            let context = canvas.getContext('2d');
            var img = new Image();
            let tolerance = 0.15;
            let width = (canvas.width/cols)*3 + (canvas.width/cols)*tolerance*3;
            let height = (canvas.height/rows)*3 + (canvas.height/rows)*tolerance*3;
            img.onload = () => {
                context.drawImage(img, this.x - width / 2, this.y - height / 2, width, height);
            }
            img.src = image_src;
        }
    }
}