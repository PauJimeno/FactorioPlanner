class Recipes{
    constructor(iconPath, modelView) {
        this.modelView = modelView;
        this.iconPath = iconPath;
        this.recipeData = {};

        this.recipesInvolved = {}
        this.itemsInvolved = new Set();
        this.selectedRecipe = 'none';

        this.recipeFileHandler();
        this.recipeSelectionHandler();
    }
    createRecipeSelection(recipeName){
        var option = document.createElement('option');
        option.value = recipeName;
        option.text = this.formatRecipeName(recipeName);
        return option;
    }

    formatRecipeName(recipeName){
        return recipeName.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
    }

    recipeFileHandler(){
       var fileInput = document.getElementById('file-id');
       fileInput.addEventListener('change', (e) => {
          var file = e.target.files[0];
          var reader = new FileReader();
          reader.onload = (e) => {
             var contents = e.target.result;
             this.recipeData = JSON.parse(contents);
             var recipeSelection = document.getElementById('recipe-selection');
             for(var recipe in this.recipeData){
                recipeSelection.appendChild(this.createRecipeSelection(recipe));
             }
          };
          reader.readAsText(file);
       });
    }

    recipeSelectionHandler(){
        let recipeSelection = document.getElementById('recipe-selection');
        recipeSelection.addEventListener('change', () => {
            this.selectedRecipe = recipeSelection.value;
            this.recipeDisplay(recipeSelection.value);
            this.recipesInvolved = {}
            this.recipeBreakdown(recipeSelection.value);
            this.recipeBreakdownDisplay(this.recipesInvolved);
            this.modelView.setItemsInUse(this.itemsInvolved);
            this.modelView.resetGridInfo();
        });
    }

    createListItem(imagePath, text) {
        let listItem = document.createElement('li');
        let contentDiv = document.createElement('div');
        contentDiv.style.display = 'flex';
        contentDiv.style.alignItems = 'center';

        let icon = document.createElement('img');
        icon.src = imagePath;
        icon.style.marginRight = '10px'; // Add right margin

        contentDiv.appendChild(icon);
        contentDiv.appendChild(document.createTextNode(text));
        listItem.appendChild(contentDiv);

        return listItem;
    }

    recipeDisplay(recipeName){
        // Remove existing recipe info
        var recipeInformation = document.getElementById('recipe-information');

        // Create the recipe element
        var recipeElement = document.getElementById('info');
        recipeElement.textContent="";

        // Create a container for the recipe name and icon
        var nameContainer = this.createListItem(this.iconPath + '/' + recipeName + '.png', this.formatRecipeName(recipeName));

        // Add the name container to the recipe element
        recipeElement.appendChild(nameContainer);

        // Create a container for the inputs and outputs
        var ioContainer = document.createElement('div');
        ioContainer.style.display = 'flex';
        ioContainer.style.justifyContent = 'space-between';

        // Create containers for the inputs and outputs
        var inputsContainer = document.createElement('div');
        var outputsContainer = document.createElement('div');

        // Style the containers
        inputsContainer.style.margin = '5px';
        outputsContainer.style.margin = '5px';

        // Add the inputs
        let inputsTitle = document.createElement('h3');
        inputsTitle.textContent = 'Inputs';
        inputsContainer.appendChild(inputsTitle);
        for(var input of this.recipeData[recipeName]["IN"]){
            var inputElement = this.createListItem(this.iconPath + '/' + input[0] + '.png', this.formatRecipeName(input[0]) + ': ' + input[1] + '/min');
            inputsContainer.appendChild(inputElement);
        }

        // Add the outputs
        let outputsTitle = document.createElement('h3');
        outputsTitle.textContent = 'Outputs';
        outputsContainer.appendChild(outputsTitle);
        for(var output of this.recipeData[recipeName]["OUT"]){
            var outputElement = this.createListItem(this.iconPath + '/' + output[0] + '.png', this.formatRecipeName(output[0]) + ': ' + output[1] + '/min');
            outputsContainer.appendChild(outputElement);
        }

        // Add the inputs and outputs containers to the io container
        ioContainer.appendChild(inputsContainer);
        ioContainer.appendChild(outputsContainer);

        // Add the io container to the recipe element
        recipeElement.appendChild(ioContainer);

        // Add the recipe element to the body
        recipeInformation.appendChild(recipeElement)
    }

    recipeBreakdownDisplay(recipeInfo){
        let recipeNamesDiv = document.getElementById('recipe-names');
        let involvedItemsDiv = document.getElementById('involved-items');

        // Clear the previous contents
        recipeNamesDiv.innerHTML = '';
        involvedItemsDiv.innerHTML = '';

        // Add titles
        let recipeNamesTitle = document.createElement('h3');
        recipeNamesTitle.textContent = 'Recipes Used';
        recipeNamesDiv.appendChild(recipeNamesTitle);

        let involvedItemsTitle = document.createElement('h3');
        involvedItemsTitle.textContent = 'Raw Items Needed';
        involvedItemsDiv.appendChild(involvedItemsTitle);

        let recipeNamesList = document.createElement('ul');
        recipeNamesDiv.appendChild(recipeNamesList);

        this.itemsInvolved.clear();

        let producedItems = new Set();

        // First, collect all produced items
        for (let recipe in recipeInfo) {
            recipeInfo[recipe].OUT.forEach(item => {
                producedItems.add(item[0]);
            });
        }

        // Then, initialize the involved items, excluding those that are produced by any recipe
        for (let recipe in recipeInfo) {
            let recipeNameElement = this.createListItem(this.iconPath + '/' + recipe + '.png', this.formatRecipeName(recipe));
            recipeNamesList.appendChild(recipeNameElement);

            recipeInfo[recipe].IN.forEach(item => {
                if (!this.itemsInvolved.has(item[0]) && !producedItems.has(item[0])) { // If the item is not in the Set and not produced by any recipe
                    this.itemsInvolved.add(item[0]); // Add the item to the Set

                    let itemElement = this.createListItem(this.iconPath + '/' + item[0] + '.png', this.formatRecipeName(item[0]));
                    involvedItemsDiv.appendChild(itemElement);
                }
            });
        }

    }

    recipeBreakdown(itemName){
        // Quan estigui l'input de caselles cal comprovar que no sigui un item d'entrada (per no involucrar receptes
        // que no siguin necessàries)
        if(itemName in this.recipeData){
            this.recipesInvolved[itemName] = this.recipeData[itemName];
            for (var item of this.recipeData[itemName]["IN"]){
                this.recipeBreakdown(item[0]);
            }
        }
    }
}


