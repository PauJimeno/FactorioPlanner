from flask import Flask, render_template, request, jsonify
from ast import literal_eval
from model.FactorioSolver import FactorioSolver
import json
_app = Flask(__name__, template_folder='templates', static_folder='static')

@_app.route('/')
def endpointHome():
    return render_template('index.html')

@_app.route('/generate.html')
def endpointGenerate():
    return render_template('generate.html')

@_app.route('/visualize.html')
def endpointVisualize():
    return render_template('visualize.html')

@_app.route('/solve-instance', methods=['POST'])
def solve_instance():
    data = request.get_json()
    instanceDataPath = "static/model_image/instance_to_solve.json"
    with open(instanceDataPath, 'w') as f:
        json.dump(data, f)
    recipes = data['recipes']
    blueprint_width = data['size'][0]
    blueprint_height = data['size'][1]
    in_out_pos = {k: {literal_eval(key): value for key, value in v.items()} for k, v in data['inOutPos'].items()}

    solver = FactorioSolver(blueprint_width, blueprint_height, in_out_pos, recipes)
    instance_status = 'UNSAT'
    instance_model = {}
    # FIND A SOLUTION #
    if solver.find_solution():
        # PRINT THE MODEL OF THE SOLUTION #
        instance_status = 'SAT'
        solver.model_to_string()
        solver.model_to_image()
    instance_model = solver.model_to_json()

    return jsonify({'result': instance_status, 'model': instance_model})

if __name__ == '__main__':
    _app.run(debug=False)

