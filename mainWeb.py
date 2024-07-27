from flask import Flask, render_template, request, jsonify
from ast import literal_eval
from model.FactorioSolver import FactorioSolver
import json
_app = Flask(__name__, template_folder='templates', static_folder='static')

@_app.route('/')
def endpointHome():
    """
    Endpoint that loads the home HTML

    :return: main web page
    :rtype: HTML
    """
    return render_template('index.html')

@_app.route('/generate.html')
def endpointGenerate():
    """
    Endpoint that loads the instance generator HTML

    :return: generator web page
    :rtype: HTML
    """
    return render_template('generate.html')

@_app.route('/visualize.html')
def endpointVisualize():
    """
    Endpoint that loads the instance visualizer HTML

    :return: visualizer web page
    :rtype: HTML
    """
    return render_template('visualize.html')

@_app.route('/solve-instance', methods=['POST'])
def solve_instance():
    """
    Loads the received instance data from the client and calls the solving function.

    :return: the solved instance
    :rtype: Json
    """
    data = request.get_json()
    instanceDataPath = "static/model_image/instance_to_solve.json"
    with open(instanceDataPath, 'w') as f:
        json.dump(data, f)
    recipes = data['recipes']
    blueprint_width = data['size'][0]
    blueprint_height = data['size'][1]
    in_out_pos = {k: {literal_eval(key): value for key, value in v.items()} for k, v in data['inOutPos'].items()}
    opt_criteria = data["optimize"]

    solver = FactorioSolver(blueprint_width, blueprint_height, in_out_pos, recipes, opt_criteria)

    # FIND A SOLUTION #
    solver.find_solution()
    instance_model = solver.model_to_json()

    return jsonify(instance_model)


if __name__ == '__main__':
    _app.run(debug=False)
