class Cell{
    constructor(x, y, type) {
        if (new.target === Blueprint) {
            throw new TypeError("Cannot construct Blueprint instances directly");
        }
        this.x = x;
        this.y = y;
        this.isDrawable = true;
        this.type = type;
    }

    updateCellInfo(){
        throw new Error('You have to implement the method updateCellInfo!');
    }

    draw(image_src, canvas, rows, cols){
        let context = canvas.getContext('2d');
        var img = new Image();
        let tolerance = 1;
        let width = canvas.width/cols + (canvas.width/cols)*tolerance;
        let height = canvas.height/rows + (canvas.height/rows)*tolerance;
        img.onload = () => {
            // Draw the image at the center of the cell, adjusting for the image's size
            context.drawImage(img, this.x - width / 2, this.y - height / 2, width, height);
        }
        img.src = image_src;
    }
}