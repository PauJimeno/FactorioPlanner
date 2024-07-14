class Cell{
    constructor(x, y, type) {
        if (new.target === Blueprint) {
            throw new TypeError("Cannot construct Blueprint instances directly");
        }
        this.x = x;
        this.y = y;
        this.type = type;
    }

    updateCellInfo(){
        throw new Error('You have to implement the method updateCellInfo!');
    }

    draw(sprite, canvas, rows, cols){
        let context = canvas.getContext('2d');
        let width = canvas.width/cols;
        let height = canvas.height/rows;
        context.drawImage(sprite, this.x - width / 2, this.y - height / 2, width, height);
    }

    drawItem(itemSprite, canvas, cellSize){
        let context = canvas.getContext('2d');
        let size = cellSize/2;
        context.drawImage(itemSprite, this.x, this.y, size, size);
    }

    createInfoElement(titleText, valueText) {
        let infoDiv = document.createElement('div');
        let title = document.createElement('h3');
        title.textContent = titleText;
        let value = document.createElement('p');
        value.style.marginLeft = '20px'; // Add left margin to the value
        value.innerHTML = valueText.replace(/\n/g, '<br>'); // Replace \n with <br>
        infoDiv.appendChild(title);
        infoDiv.appendChild(value);

        return infoDiv;
    }

    drawSelectedOutline(canvas, rows, columns){
        var cellWidth = canvas.width / columns;
        var cellHeight = canvas.height / rows;
        var context = canvas.getContext('2d');
        context.clearRect(0, 0, canvas.width, canvas.height);

        var selectedCellX = Math.floor(this.x / cellWidth);
        var selectedCellY = Math.floor(this.y / cellHeight);
        context.beginPath();
        context.rect(selectedCellX * cellWidth, selectedCellY * cellHeight, cellWidth, cellHeight);
        context.lineWidth = 4; // Change this to make the border thicker or thinner
        context.strokeStyle = "#FFFFFF"; // Change this to change the border color
        context.stroke();
    }



    formatItemName(itemName){
        return itemName.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
    }
}