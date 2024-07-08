let instanceData = {};
instanceFileHandler();
let blueprint;

function instanceFileHandler(){
    var fileInput = document.getElementById('instance-file-id');
    fileInput.addEventListener('change', (e) => {
        var file = e.target.files[0];
        var reader = new FileReader();
        reader.onload = (e) => {
            var contents = e.target.result;
            instanceData = JSON.parse(contents);
            blueprint = new SolvedBlueprint(instanceData["CONVEYOR"].length, instanceData["CONVEYOR"][0].length)
            blueprint.solvedInstance = instanceData;
            blueprint.resetGridInfo();
            blueprint.draw();
        };
        reader.readAsText(file);
    });
}