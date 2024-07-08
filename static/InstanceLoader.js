class InstanceLoader{
    constructor() {
        this.instanceData = {};
        this.instanceFileHandler();
        this.blueprint = this.initializeBlueprint(5, 5);
    }

    instanceFileHandler(){
        var fileInput = document.getElementById('instance-file-id');
        fileInput.addEventListener('change', (e) => {
            var file = e.target.files[0];
            var reader = new FileReader();
            reader.onload = (e) => {
                var contents = e.target.result;
                this.instanceData = JSON.parse(contents);
                this.blueprint.resetGridInfo();
                console.log(this.instanceData);
            };
            reader.readAsText(file);
        });
    }

    initializeBlueprint(rows, cols){
        let blueprint = new SolvedBlueprint(rows, cols);
        return blueprint;
    }

}