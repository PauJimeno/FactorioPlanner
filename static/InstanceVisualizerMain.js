instanceFileHandler();
let blueprint = new SolvedBlueprint(1, 1);
function handleFileContents(contents, context, canvas) {
    // Clear the canvas
    context.clearRect(0, 0, canvas.width, canvas.height);

    // Calculate the center of the canvas
    var centerX = canvas.width / 2;
    var centerY = canvas.height / 2;

    try {
        var instanceData = JSON.parse(contents);
        if (!instanceData.hasOwnProperty("status")) {
            // Draw the text in the center of the canvas
            context.fillText('The .json file does not have the field "status".', centerX, centerY);
            return;
        }
        switch (instanceData["status"]) {
            case "UNSAT":
                context.fillText('The instance is not solved: UN-SAT', centerX, centerY);
                break;
            case "TIMED_OUT":
                context.fillText('The instance is not solved: TIMED OUT', centerX, centerY);
                break;
            case "SAT":
                blueprint = new SolvedBlueprint(instanceData["CONVEYOR"].length, instanceData["CONVEYOR"][0].length);
                blueprint.solvedInstance = instanceData;
                blueprint.resetGridInfo();
                blueprint.draw();
                break;
            default:
                context.fillText('The "status" value is not recognized.', centerX, centerY);
                break;
        }
    } catch (error) {
        context.fillText('The file loaded is not a valid JSON.', centerX, centerY);
    }
}

function instanceFileHandler(){
    var fileInput = document.getElementById('instance-file-id');
    var canvas = document.getElementById('model-view');
    fileInput.addEventListener('change', (e) => {
        blueprint.removeAllEventListeners();
        var file = e.target.files[0];
        var reader = new FileReader();
        reader.onload = (e) => {
            var contents = e.target.result;
            var context = canvas.getContext('2d');
            context.font = '40px Arial'; // Set the font size and style
            context.fillStyle = '#fafafa'; // Set the text color
            context.textAlign = 'center'; // Align the text to the center
            var cursosCanvas = document.getElementById('cursor-canvas');
            cursosCanvas.getContext('2d').clearRect(0, 0, cursosCanvas.width, cursosCanvas.height);
            handleFileContents(contents, context, canvas);
        };
        reader.readAsText(file);
    });
}