const iconPath = "static/RecipeIcons"
modelView = new InputBlueprint(5, 5);
recipes = new Recipes(iconPath, modelView);
let solvedInstance = {};

function solveInstance() {
    document.getElementById("status-text").textContent = "Instance sent and being solved";
    let dataLoad = {}
    let rows = parseInt(document.getElementById('rows').value);
    let cols = parseInt(document.getElementById('cols').value);
    let optimize = document.getElementById('optimization').value;
    let inOutPos = modelView.inputItems(recipes.selectedRecipe);

    dataLoad["recipes"] = recipes.recipesInvolved;
    dataLoad["size"] = [cols, rows];
    dataLoad["inOutPos"] = inOutPos;
    dataLoad["optimize"] = optimize;

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
        if (solvedInstance['status'] === "SAT"){
            document.getElementById("status-text").textContent = "Instance solved in " + solvedInstance["solving_time"] + " seconds: SAT";
        }
        else if(solvedInstance['status'] === "UNSAT"){
            document.getElementById("status-text").textContent = "Instance solved in " + solvedInstance["solving_time"] + " seconds: UNSAT";
        }
        else if(solvedInstance['status'] === "TIMED_OUT"){
            document.getElementById("status-text").textContent = "Instance not solved: TIMED OUT after "+ solvedInstance["solving_time"] + " seconds";
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function downloadSolution(){
    var jsonString = JSON.stringify(solvedInstance, null, 2);
    var blob = new Blob([jsonString], {type: 'application/json'});
    var url = URL.createObjectURL(blob);
    var link = document.createElement('a');
    link.href = url;
    link.download = 'SolvedInstance.json';
    link.click();
}
