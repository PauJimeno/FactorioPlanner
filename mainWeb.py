from flask import Flask, render_template, request, jsonify

from model.FactorioSolver import FactorioSolver

_app = Flask(__name__, template_folder='templates', static_folder='static')

@_app.route('/')
def endpointHome():
    return render_template('index.html')

@_app.route('/solve-instance', methods=['POST'])
def your_flask_function():
    data = request.get_json()
    recipes = data['recipes']
    blueprint_width = data['size'][0]
    blueprint_height = data['size'][1]

    # Queda fer que les posicions també vinguin del client (s'ha de fer al canvas del client web)
    in_out_pos = {
        'IN': {(0, 0): {'ITEM': 'iron-plate', 'RATE': 100}, (0, 7): {'ITEM': 'copper-plate', 'RATE': 100}, (7, 0): {'ITEM': 'plastic-bar', 'RATE': 100}},
        'OUT': {(7, 7): {'ITEM': 'advanced-circuit'}},
    }

    solver = FactorioSolver(blueprint_width, blueprint_height, in_out_pos, recipes)
    instance_status = 'UNSAT'
    # FIND A SOLUTION #
    if solver.find_solution():
        # PRINT THE MODEL OF THE SOLUTION #
        instance_status = 'SAT'
        solver.model_to_string()
        solver.model_to_image()

    return jsonify({'result': instance_status})

if __name__ == '__main__':
    _app.run(debug=False)

