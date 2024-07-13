class SolvedBlueprint extends Blueprint{
    constructor(rows, columns) {
        // Super class constructor call
        super(rows, columns);
        this.spriteCanvas.addEventListener('click', (event) => this.handleCellClick(event));
        this.solvedInstance = {};
        this.adjacentPos = {
            'north': {'west': [0, -1], 'east': [0, 1], 'south': [1, 0]},
            'east': {'north': [-1, 0], 'south': [1, 0], 'west': [0, -1]},
            'south': {'west': [0, -1], 'east': [0, 1], 'north': [-1, 0]},
            'west': {'north': [-1, 0], 'south': [1, 0], 'east': [0, 1]}
        };
        this.dirCoord = {
            'north': [-1, 0],
            'east': [0, 1],
            'south': [1, 0],
            'west': [0, -1]
        };
        this.oppositeDir = {
            'north': 'south',
            'east': 'west',
            'south': 'north',
            'west': 'east'
        };
        this.spriteNames = ['blueprint_sprites/assembler/assembler', 'blueprint_sprites/conveyor_belt/east', 'blueprint_sprites/conveyor_belt/east_north',
            'blueprint_sprites/conveyor_belt/east_south', 'blueprint_sprites/conveyor_belt/north', 'blueprint_sprites/conveyor_belt/north_east',
            'blueprint_sprites/conveyor_belt/north_west', 'blueprint_sprites/conveyor_belt/south', 'blueprint_sprites/conveyor_belt/south_east',
            'blueprint_sprites/conveyor_belt/south_west', 'blueprint_sprites/conveyor_belt/west', 'blueprint_sprites/conveyor_belt/west_north',
            'blueprint_sprites/conveyor_belt/west_south', 'blueprint_sprites/inserter/north', 'blueprint_sprites/inserter/south', 'blueprint_sprites/inserter/east',
            'blueprint_sprites/inserter/west'];
        this.sprites = {};

        this.gridInformation = new Array(rows);
        for (let i = 0; i < rows; i++) {
            this.gridInformation[i] = new Array(columns);
            for (let j = 0; j < columns; j++) {
                let pos = this.getCellCenter(i, j);
                this.gridInformation[i][j] = new EmptyCell(pos[0], pos[1]);
            }
        }
    }

    resetGridInfo(){
        let route = this.solvedInstance["ROUTE"];
        let conveyorDir = this.solvedInstance["CONVEYOR"];
        let inserterDir = this.solvedInstance["INSERTER"];
        let assemblerCenter = this.solvedInstance["ASSEMBLER"];
        let itemType = this.solvedInstance["ITEM_FLOW"];
        let inputFlowRate = this.solvedInstance["INPUT_FLOW_RATE"];
        let outputFlowRate = this.solvedInstance["OUTPUT_FLOW_RATE"];

        // SET UP ASSEMBLER CELLS (SHARED REFERENCE BETWEEN THE SAME ASSEMBLER)
        let adjacentCell = [[0, 0], [1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]
        for(let i = 0; i < this.rows - 2; i++){
            for(let j = 0; j < this.columns - 2; j++){
                if(assemblerCenter[i][j] != 'none'){
                    let iCenter = i+1;
                    let jCenter = j+1;
                    let pos = this.getCellCenter(iCenter, jCenter);
                    let assemblerCell = new AssemblerCell(assemblerCenter[i][j], pos[0], pos[1]);
                    for(let pos of adjacentCell){
                        let x = pos[0];
                        let y = pos[1];
                        this.gridInformation[iCenter+x][jCenter+y] = assemblerCell;
                    }
                }
            }
        }

        // SET UP TRANSPORT CELLS (INSERTERS AND CONVEYORS)
        for(let i = 0; i < this.rows; i++){
            for(let j = 0; j < this.columns; j++){
                let blueprintPos = this.getCellCenter(i, j);
                let x = blueprintPos[0];
                let y = blueprintPos[1];
                if(conveyorDir[i][j] != 'empty'){
                    this.gridInformation[i][j] = new ConveyorCell(conveyorDir[i][j], itemType[i][j], this.toFloat(inputFlowRate[i][j]), this.toFloat(outputFlowRate[i][j]), route[i][j], x, y);
                }
                else if(inserterDir[i][j] != 'empty'){
                    this.gridInformation[i][j] = new InserterCell(inserterDir[i][j], itemType[i][j], this.toFloat(inputFlowRate[i][j]), this.toFloat(outputFlowRate[i][j]), route[i][j],  x, y);
                }
            }
        }

        for(let i = 0; i < this.rows; i++){
            for(let j = 0; j < this.columns; j++){
                if(this.gridInformation[i][j].type == 'conveyor'){
                    this.gridInformation[i][j].routeStatus = this.conveyorRouteStatus(i, j);
                }
            }
        }

        // GET ALL UNIQUE ITEMS USED
        let flattened = itemType.reduce((acc, val) => acc.concat(val), []);
        let uniqueItems = flattened.filter((value, index, self) => value !== 'none' && self.indexOf(value) === index);

        // APPEND UNIQUE ITEMS TO SPRITE NAMES
        this.spriteNames = [...this.spriteNames, ...uniqueItems.map(item => `RecipeIcons/${item}`)];
    }

    draw() {
        // FETCH THE SPRITES
        Promise.all(this.spriteNames.map(this.fetchSprite)).then(sprites => {
            this.sprites = Object.fromEntries(this.spriteNames.map((name, i) => [name, sprites[i]]));

            // CONVEYOR DRAWING LOOP
            for(let i = 0; i < this.rows; i++){
                for(let j = 0; j < this.columns; j++){
                    let currentCell = this.gridInformation[i][j];
                    if(currentCell.type == 'conveyor'){
                        currentCell.draw(this.conveyorSprite(i, j), this.sprites[`RecipeIcons/${currentCell.itemCarrying}`] ,this.spriteCanvas, this.rows, this.columns);
                    }
                }
            }

            // ASSEMBLER DRAWING LOOP
            for(let i = 0; i < this.rows; i++){
                for(let j = 0; j < this.columns; j++){
                    let currentCell = this.gridInformation[i][j];
                    if(currentCell.type == 'assembler'){
                        currentCell.draw(this.sprites['blueprint_sprites/assembler/assembler'], this.sprites[`RecipeIcons/${currentCell.itemProducing}`], this.spriteCanvas, this.rows, this.columns);
                    }
                }
            }

            // INSERTER DRAWING LOOP
            for(let i = 0; i < this.rows; i++){
                for(let j = 0; j < this.columns; j++){
                    let currentCell = this.gridInformation[i][j];
                    if(currentCell.type == 'inserter'){
                        this.gridInformation[i][j].draw(this.sprites[`blueprint_sprites/inserter/${currentCell.dir}`], this.sprites[`RecipeIcons/${currentCell.itemCarrying}`], this.spriteCanvas, this.rows, this.columns);
                        this.updateAssemblerInputOutput(i, j);
                    }
                }
            }
        }).catch(error => {
            console.error('Error loading sprites:', error);
        });
    }

    conveyorSprite(x, y){
        let currentCell = this.gridInformation[x][y];
        let sprite = this.sprites[`blueprint_sprites/conveyor_belt/${currentCell.dir}`];
        let nAdjacentCells = 0;

        for (let [dir, pos] of Object.entries(this.adjacentPos[currentCell.dir])){
            if(x+pos[0]>=0 && x+pos[0]<this.rows && y+pos[1]>=0 && y+pos[1]<this.columns){
                let adjacentCell = this.gridInformation[x+pos[0]][y+pos[1]];
                if(adjacentCell.type == 'conveyor'){
                    if(this.oppositeDir[adjacentCell.dir] == dir){
                        nAdjacentCells++;
                        if(adjacentCell.dir != currentCell.dir){
                            sprite = this.sprites[`blueprint_sprites/conveyor_belt/${adjacentCell.dir}_${currentCell.dir}`];
                        }
                    }
                }
            }
        }
        if(nAdjacentCells>1) sprite = this.sprites[`blueprint_sprites/conveyor_belt/${currentCell.dir}`];
        return sprite;
    }

    fetchSprite(spriteName){
        return new Promise((resolve, reject) => {
            let img = new Image();
            img.onload = () => resolve(img);
            img.onerror = reject;
            img.src = `/static/${spriteName}.png`;
        });
    }

    updateAssemblerInputOutput(x, y){
        let outPos = this.dirCoord[this.gridInformation[x][y].dir];
        let inPos = this.dirCoord[this.oppositeDir[this.gridInformation[x][y].dir]];
        let currentCell = this.gridInformation[x][y];
        let outputCell = this.gridInformation[outPos[0]+x][outPos[1]+y];
        let inputCell = this.gridInformation[inPos[0]+x][inPos[1]+y];
        if(outputCell.type == 'assembler'){
            if (outputCell.inputItems.hasOwnProperty(currentCell.itemCarrying)) {
            outputCell.inputItems[currentCell.itemCarrying] += currentCell.inputFlow;
            } else {
                outputCell.inputItems[currentCell.itemCarrying] = currentCell.inputFlow;
            }
        }
        if(inputCell.type == 'assembler'){
            if (inputCell.outputItem.hasOwnProperty(currentCell.itemCarrying)) {
            inputCell.outputItem[currentCell.itemCarrying] += currentCell.inputFlow;
            } else {
                inputCell.outputItem[currentCell.itemCarrying] = currentCell.inputFlow;
            }
        }
    }

    conveyorRouteStatus(x, y){
        let status = 'nothing';
        let outPos = this.dirCoord[this.gridInformation[x][y].dir];
        if(this.gridInformation[x][y].routeValue == 1) status = 'input';
        //OUT OF BOUNDS OUTPUT
        else if (x+outPos[0]>=this.rows || x+outPos[0]<0 || y+outPos[1]>=this.columns || y+outPos[1]<0) status = 'output';
        else if(this.gridInformation[x+outPos[0]][y+outPos[1]].type == 'conveyor'){
            let currentCell = this.gridInformation[x][y];
            let nextCell = this.gridInformation[x+outPos[0]][y+outPos[1]];
            // NOT CONNECTING CONVEYOR
            if (currentCell.dir == this.oppositeDir[nextCell.dir]) status = 'output';
        }
        else if(this.gridInformation[x+outPos[0]][y+outPos[1]].type == 'inserter'){
            let currentCell = this.gridInformation[x][y];
            let nextCell = this.gridInformation[x+outPos[0]][y+outPos[1]];
            // NOT CONNECTING INSERTER
            if (currentCell.dir != nextCell.dir) status = 'output';
        }
        // ASSEMBLER OUTPUT
        else if(this.gridInformation[x+outPos[0]][y+outPos[1]].type == 'empty') status = 'output';
        // EMPTY CELL
        else if(this.gridInformation[x+outPos[0]][y+outPos[1]].type == 'assembler') status = 'output';
        return status;
    }

    toFloat(number){
        let result;
        if (number.includes("/")) {
            let parts = number.split("/");
            result = parseFloat(parts[0]) / parseFloat(parts[1]);
        } else {
            result = parseFloat(number);
        }
        return result;
    }
}