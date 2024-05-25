class Recipes{
    constructor(iconPath) {
        this.iconPath = iconPath;
        this.recipeData = {};

        this.recipesInvolved = {}
        this.itemsInvolved = {}

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
           this.recipeDisplay(recipeSelection.value);
           this.recipesInvolved = {}
           this.recipeBreakdown(recipeSelection.value);
           this.recipeBreakdownDisplay(this.recipesInvolved);
           console.log(JSON.stringify(this.recipesInvolved));
        });
    }

    recipeDisplay(recipeName){
        // Remove existing recipe info
        var recipeInformation = document.getElementById('recipe-information');

        // Create the recipe element
        var recipeElement = document.getElementById('info');
        recipeElement.textContent="";

        // Create a container for the recipe name and icon
        var nameContainer = document.createElement('div');
        nameContainer.style.display = 'flex';
        nameContainer.style.alignItems = 'center';

        // Add the recipe name and icon
        var icon = document.createElement('img');
        icon.src = this.iconPath + '/' + recipeName + '.png'; // Replace with the actual path to your icons
        nameContainer.appendChild(icon);
        nameContainer.appendChild(document.createTextNode(this.formatRecipeName(recipeName)));

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
        inputsContainer.style.width = '200%';
        outputsContainer.style.width = '200%';
        inputsContainer.style.margin = '5px';
        outputsContainer.style.margin = '5px';

        // Add the inputs
        inputsContainer.appendChild(document.createTextNode('Inputs:'));
        for(var input of this.recipeData[recipeName]["IN"]){
            var inputElement = document.createElement('div');
            var icon = document.createElement('img');
            icon.src = this.iconPath + '/' + input[0] + '.png'; // Replace with the actual path to your icons
            inputElement.appendChild(icon);
            inputElement.appendChild(document.createTextNode(this.formatRecipeName(input[0]) + ': ' + input[1] + '/min'));
            inputsContainer.appendChild(inputElement);
        }

        // Add the outputs
        outputsContainer.appendChild(document.createTextNode('Outputs:'));
        for(var output of this.recipeData[recipeName]["OUT"]){
            var outputElement = document.createElement('div');
            var icon = document.createElement('img');
            icon.src = this.iconPath + '/' + output[0] + '.png'; // Replace with the actual path to your icons
            outputElement.appendChild(icon);
            outputElement.appendChild(document.createTextNode(this.formatRecipeName(output[0]) + ': ' + output[1] + '/min'));
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
        involvedItemsTitle.textContent = 'Items Needed';
        involvedItemsDiv.appendChild(involvedItemsTitle);

        let recipeNamesList = document.createElement('ul');
        recipeNamesDiv.appendChild(recipeNamesList);

        for (let recipe in recipeInfo) {
            let recipeNameElement = document.createElement('li');

            // Create an img element for the recipe
            let recipeIcon = document.createElement('img');
            recipeIcon.src = this.iconPath + '/' + recipe + '.png';
            recipeNameElement.appendChild(recipeIcon);

            recipeNameElement.appendChild(document.createTextNode(this.formatRecipeName(recipe)));
            recipeNamesList.appendChild(recipeNameElement);

            let involvedItemsList = document.createElement('ul');
            recipeInfo[recipe].IN.forEach(item => {
                let itemElement = document.createElement('li');

                // Create an img element for the item
                let itemIcon = document.createElement('img');
                itemIcon.src = this.iconPath + '/' + item[0] + '.png';
                itemElement.appendChild(itemIcon);

                itemElement.appendChild(document.createTextNode(this.formatRecipeName(item[0])));
                involvedItemsList.appendChild(itemElement);
            });
            involvedItemsDiv.appendChild(involvedItemsList);
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


