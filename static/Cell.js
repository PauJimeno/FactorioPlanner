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

    draw(sprite, canvas, rows, cols){
        let context = canvas.getContext('2d');
        context.drawImage(sprite, this.x - sprite.width / 2, this.y - sprite.height / 2);
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

    formatItemName(itemName){
        return itemName.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
    }
}