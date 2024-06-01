const iconPath = "static/RecipeIcons"
const instanceImagePath = "static/model_image/solved_instance.png";
modelView = new Blueprint(5, 5);
recipes = new Recipes(iconPath, modelView);

function solveInstance() {
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
        if (data.result === "SAT"){
            console.log(JSON.stringify(data.model));
            modelView.drawInstanceImage(instanceImagePath);
        }
        console.log('Success:', dataLoad);
        console.log('Result from server:', data.result);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}










