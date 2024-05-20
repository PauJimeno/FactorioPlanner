// MAIN SCRIPT
const iconPath = "static/RecipeIcons"
const instanceImagePath = "static/model_image/solved_instance.png";
recipes = new Recipes(iconPath);
modelView = new ModelView(5, 5);

function solveInstance() {
    // Your data to send to the server
    var dataLoad = {}
    var rows = parseInt(document.getElementById('rows').value);
    var cols = parseInt(document.getElementById('cols').value);

    dataLoad["recipes"] = recipes.recipesInvolved;
    dataLoad["size"] = [cols, rows]
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
            modelView.drawInstanceImage(instanceImagePath);
        }
        console.log('Success:', dataLoad);
        console.log('Result from server:', data.result);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}










