class SolvedBlueprint extends Blueprint{
    constructor(rows, columns) {
        // Super class constructor call
        super(rows, columns);
        this.canvas.addEventListener('click', (event) => this.handleCellClick(event));
        this.solvedInstance = {};
        this.adjacentPos = {'north': {'west':[0, -1], 'east': [0, 1], 'south': [1, 0]},
                            'east': {'north': [-1, 0], 'south': [1, 0], 'west': [0, -1]},
                            'south': {'west':[0, -1], 'east': [0, 1], 'north': [-1, 0]},
                            'west': {'north': [-1, 0], 'south': [1, 0], 'east': [0, 1]}};
        this.oppositeDir = {'north': 'south',
                            'east': 'west',
                            'south': 'north',
                            'west': 'east'};
    }

    resetGridInfo(){
        this.gridInformation = [];
        let conveyorDir = this.solvedInstance["CONVEYOR"];
        let inserterDir = this.solvedInstance["INSERTER"];
        let assemblerCenter = this.solvedInstance["ASSEMBLER"];
        let itemType = this.solvedInstance["ITEM_FLOW"];
        let inputFlowRate = this.solvedInstance["INPUT_FLOW_RATE"];
        let outputFlowRate = this.solvedInstance["OUTPUT_FLOW_RATE"];

        // SET UP TRANSPORT CELLS (INSERTERS AND CONVEYORS)
        for(let i = 0; i < this.rows; i++){
            let row = [];
            for(let j = 0; j < this.columns; j++){
                let blueprintPos = this.getCellCenter(i, j);
                let x = blueprintPos[0];
                let y = blueprintPos[1];
                if(conveyorDir[i][j] != 'empty'){
                    row.push(new ConveyorCell(conveyorDir[i][j], itemType[i][j], inputFlowRate[i][j], outputFlowRate[i][j], x, y));
                }
                else if(inserterDir[i][j] != 'empty'){
                    row.push(new InserterCell(inserterDir[i][j], itemType[i][j], inputFlowRate[i][j], outputFlowRate[i][j], x, y));
                }
                else{
                    row.push(new EmptyCell());
                }
            }
            this.gridInformation.push(row);
        }

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
    }

    draw() {
        // CONVEYOR DRAWING LOOP
        for(let i = 0; i < this.rows; i++){
            for(let j = 0; j < this.columns; j++){
                if(this.gridInformation[i][j].type == 'conveyor'){
                    let spriteDir = this.conveyorSprite(i, j);
                    this.gridInformation[i][j].draw(spriteDir, this.canvas, this.rows, this.columns);
                }
            }
        }

        // ASSEMBLER DRAWING LOOP
        for(let i = 0; i < this.rows; i++){
            for(let j = 0; j < this.columns; j++){
                if(this.gridInformation[i][j].type == 'assembler'){
                    this.gridInformation[i][j].draw('static/blueprint_sprites/assembler/assembler.png', this.canvas, this.rows, this.columns);
                }
            }
        }

        // INSERTER DRAWING LOOP
        for(let i = 0; i < this.rows; i++){
            for(let j = 0; j < this.columns; j++){
                let currentCell = this.gridInformation[i][j];
                if(currentCell.type == 'inserter'){
                    this.gridInformation[i][j].draw(`static/blueprint_sprites/inserter/${currentCell.dir}_inserter.png`, this.canvas, this.rows, this.columns);
                }
            }
        }
    }

    conveyorSprite(x, y){
        let currentCell = this.gridInformation[x][y];
        let spriteDir = `static/blueprint_sprites/conveyor_belt/${currentCell.dir}_conveyor.png`;
        let nAdjacentCells = 0;

        for (let [dir, pos] of Object.entries(this.adjacentPos[currentCell.dir])){
            if(x+pos[0]>=0 && x+pos[0]<this.rows && y+pos[1]>=0 && y+pos[1]<this.columns){
                let adjacentCell = this.gridInformation[x+pos[0]][y+pos[1]];
                if(adjacentCell.type == 'conveyor'){
                    if(this.oppositeDir[adjacentCell.dir] == dir){
                        nAdjacentCells++;
                        if(adjacentCell.dir != currentCell.dir){
                            spriteDir = `static/blueprint_sprites/conveyor_belt/${adjacentCell.dir}_${currentCell.dir}_conveyor.png`;
                        }
                    }
                }
            }
        }
        if(nAdjacentCells>1) spriteDir = `static/blueprint_sprites/conveyor_belt/${currentCell.dir}_conveyor.png`;
        return spriteDir;
    }
}