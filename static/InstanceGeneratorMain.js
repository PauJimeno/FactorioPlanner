const iconPath = "static/RecipeIcons"
const instanceImagePath = "static/model_image/solved_instance.png";
modelView = new InputBlueprint(5, 5);
recipes = new Recipes(iconPath, modelView);
let solvedInstance = {};

function solveInstance() {
    document.getElementById("status-text").textContent = "Instance sent and being solved";
    let dataLoad = {}
    let rows = parseInt(document.getElementById('rows').value);
    let cols = parseInt(document.getElementById('cols').value);
    let inOutPos = modelView.inputItems(recipes.selectedRecipe);

    dataLoad["recipes"] = recipes.recipesInvolved;
    dataLoad["size"] = [cols, rows];
    dataLoad["inOutPos"] = inOutPos;

    fetch('/solve-instance', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(dataLoad),
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('download-solution').disabled = false;
        solvedInstance = data;
        if (data.result === "SAT"){
            document.getElementById("status-text").textContent = "Instance solved in " + data.model["solving_time"] + " seconds: SAT";
        }
        else if(data.result === "UNSAT"){
            document.getElementById("status-text").textContent = "Instance solved in " + data.model["solving_time"] + " seconds: UNSAT";
        }
        else if(data.result === "TIMEOUT"){
            document.getElementById("status-text").textContent = "Instance solved: TIMEOUT";
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function downloadSolution(){
    var jsonString = JSON.stringify(solvedInstance["model"], null, 2);
    var blob = new Blob([jsonString], {type: 'application/json'});
    var url = URL.createObjectURL(blob);
    var link = document.createElement('a');
    link.href = url;
    link.download = 'SolvedInstance.json';
    link.click();
}

function load_solved_instance(){

}










