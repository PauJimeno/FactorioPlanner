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

    instances_to_solve = [
        {"recipes": {"copper-cable": {"IN": [["copper-plate", 120]], "OUT": [["copper-cable", 240]]}}, "size": [5, 5],
         "inOutPos": {"IN": {"(0,0)": {"ITEM": "copper-plate", "RATE": 0}}, "OUT": {"(4,4)": {"ITEM": "copper-cable"}}}},
        {"recipes": {"copper-cable": {"IN": [["copper-plate", 120]], "OUT": [["copper-cable", 240]]}}, "size": [5, 5],
         "inOutPos": {"IN": {"(0,0)": {"ITEM": "copper-plate", "RATE": 0}},
                      "OUT": {"(4,0)": {"ITEM": "copper-cable"}, "(4,4)": {"ITEM": "copper-cable"}}}},
        {"recipes": {"iron-chest": {"IN": [["iron-plate", 960]], "OUT": [["iron-chest", 120]]}}, "size": [5, 5],
         "inOutPos": {"IN": {"(0,0)": {"ITEM": "iron-plate", "RATE": 0}}, "OUT": {"(4,4)": {"ITEM": "iron-chest"}}}},
        {"recipes": {"iron-chest": {"IN": [["iron-plate", 960]], "OUT": [["iron-chest", 120]]}}, "size": [5, 5],
         "inOutPos": {"IN": {"(0,4)": {"ITEM": "iron-plate", "RATE": 0}}, "OUT": {"(4,4)": {"ITEM": "iron-chest"}}}},
        {"recipes": {"wooden-chest": {"IN": [["wood", 240]], "OUT": [["wooden-chest", 120]]}}, "size": [5, 5],
         "inOutPos": {"IN": {"(0,0)": {"ITEM": "wood", "RATE": 0}}, "OUT": {"(4,4)": {"ITEM": "wooden-chest"}}}},
        {"recipes": {"pistol": {"IN": [["iron-plate", 60], ["copper-plate", 60]], "OUT": [["pistol", 12]]}},
         "size": [5, 5],
         "inOutPos": {"IN": {"(0,0)": {"ITEM": "iron-plate", "RATE": 0}, "(0,1)": {"ITEM": "copper-plate", "RATE": 0}},
                      "OUT": {"(4,4)": {"ITEM": "pistol"}}}},
        {"recipes": {"pistol": {"IN": [["iron-plate", 60], ["copper-plate", 60]], "OUT": [["pistol", 12]]}},
         "size": [5, 5],
         "inOutPos": {"IN": {"(0,0)": {"ITEM": "iron-plate", "RATE": 0}, "(0,4)": {"ITEM": "copper-plate", "RATE": 0}},
                      "OUT": {"(4,4)": {"ITEM": "pistol"}}}},
        {"recipes": {"pistol": {"IN": [["iron-plate", 60], ["copper-plate", 60]], "OUT": [["pistol", 12]]}},
         "size": [5, 5],
         "inOutPos": {"IN": {"(0,0)": {"ITEM": "iron-plate", "RATE": 0}, "(4,0)": {"ITEM": "copper-plate", "RATE": 0}},
                      "OUT": {"(4,4)": {"ITEM": "pistol"}}}},
        {"recipes": {"pistol": {"IN": [["iron-plate", 60], ["copper-plate", 60]], "OUT": [["pistol", 12]]}},
         "size": [5, 5], "inOutPos": {
            "IN": {"(0,0)": {"ITEM": "iron-plate", "RATE": 0}, "(0,1)": {"ITEM": "iron-plate", "RATE": 0},
                   "(4,0)": {"ITEM": "copper-plate", "RATE": 0}, "(4,1)": {"ITEM": "copper-plate", "RATE": 0}},
            "OUT": {"(4,4)": {"ITEM": "pistol"}}}},
        {"recipes": {"pistol": {"IN": [["iron-plate", 60], ["copper-plate", 60]], "OUT": [["pistol", 12]]}},
         "size": [5, 5], "inOutPos": {
            "IN": {"(0,0)": {"ITEM": "iron-plate", "RATE": 0}, "(0,1)": {"ITEM": "iron-plate", "RATE": 0},
                   "(0,2)": {"ITEM": "iron-plate", "RATE": 0}, "(4,0)": {"ITEM": "copper-plate", "RATE": 0},
                   "(4,1)": {"ITEM": "copper-plate", "RATE": 0}, "(4,2)": {"ITEM": "copper-plate", "RATE": 0}},
            "OUT": {"(4,4)": {"ITEM": "pistol"}}}},
        {"recipes": {"cannon-shell": {"IN": [["steel-plate", 15], ["plastic-bar", 15], ["explosives", 7.5]],
                                      "OUT": [["cannon-shell", 7.5]]}}, "size": [5, 5], "inOutPos": {
            "IN": {"(0,0)": {"ITEM": "steel-plate", "RATE": 0}, "(0,1)": {"ITEM": "plastic-bar", "RATE": 0},
                   "(0,2)": {"ITEM": "explosives", "RATE": 0}}, "OUT": {"(4,4)": {"ITEM": "cannon-shell"}}}},
        {"recipes": {"cannon-shell": {"IN": [["steel-plate", 15], ["plastic-bar", 15], ["explosives", 7.5]],
                                      "OUT": [["cannon-shell", 7.5]]}}, "size": [5, 5], "inOutPos": {
            "IN": {"(0,0)": {"ITEM": "steel-plate", "RATE": 0}, "(0,4)": {"ITEM": "plastic-bar", "RATE": 0},
                   "(4,0)": {"ITEM": "explosives", "RATE": 0}}, "OUT": {"(4,4)": {"ITEM": "cannon-shell"}}}},
        {"recipes": {"cannon-shell": {"IN": [["steel-plate", 15], ["plastic-bar", 15], ["explosives", 7.5]],
                                      "OUT": [["cannon-shell", 7.5]]}}, "size": [5, 5], "inOutPos": {
            "IN": {"(0,0)": {"ITEM": "steel-plate", "RATE": 0}, "(0,1)": {"ITEM": "plastic-bar", "RATE": 0},
                   "(0,2)": {"ITEM": "explosives", "RATE": 0}, "(0,3)": {"ITEM": "explosives", "RATE": 0}},
            "OUT": {"(4,4)": {"ITEM": "cannon-shell"}}}},
        {"recipes": {"copper-cable": {"IN": [["copper-plate", 120]], "OUT": [["copper-cable", 240]]}}, "size": [6, 6],
         "inOutPos": {"IN": {"(0,0)": {"ITEM": "copper-plate", "RATE": 0}}, "OUT": {"(5,5)": {"ITEM": "copper-cable"}}}},
        {"recipes": {"copper-cable": {"IN": [["copper-plate", 120]], "OUT": [["copper-cable", 240]]}}, "size": [6, 6],
         "inOutPos": {
             "IN": {"(0,5)": {"ITEM": "copper-plate", "RATE": 0}, "(1,5)": {"ITEM": "copper-plate", "RATE": 0}},
             "OUT": {"(5,5)": {"ITEM": "copper-cable"}}}},
        {"recipes": {"burner-inserter": {"IN": [["iron-plate", 120], ["iron-gear-wheel", 120]],
                                         "OUT": [["burner-inserter", 120]]},
                     "iron-gear-wheel": {"IN": [["iron-plate", 240]], "OUT": [["iron-gear-wheel", 120]]}},
         "size": [6, 6], "inOutPos": {"IN": {"(0,0)": {"ITEM": "iron-plate", "RATE": 0}},
                                      "OUT": {"(5,5)": {"ITEM": "burner-inserter"}}}},
        {"recipes": {"burner-inserter": {"IN": [["iron-plate", 120], ["iron-gear-wheel", 120]],
                                         "OUT": [["burner-inserter", 120]]},
                     "iron-gear-wheel": {"IN": [["iron-plate", 240]], "OUT": [["iron-gear-wheel", 120]]}},
         "size": [6, 6], "inOutPos": {"IN": {"(0,0)": {"ITEM": "iron-plate", "RATE": 0}},
                                      "OUT": {"(0,5)": {"ITEM": "burner-inserter"}}}},
        {"recipes": {"automation-science-pack": {"IN": [["copper-plate", 12], ["iron-gear-wheel", 12]],
                                                 "OUT": [["automation-science-pack", 12]]},
                     "iron-gear-wheel": {"IN": [["iron-plate", 240]], "OUT": [["iron-gear-wheel", 120]]}},
         "size": [6, 6],
         "inOutPos": {"IN": {"(0,0)": {"ITEM": "copper-plate", "RATE": 0}, "(0,1)": {"ITEM": "iron-plate", "RATE": 0}},
                      "OUT": {"(5,5)": {"ITEM": "automation-science-pack"}}}},
        {"recipes": {"automation-science-pack": {"IN": [["copper-plate", 12], ["iron-gear-wheel", 12]],
                                                 "OUT": [["automation-science-pack", 12]]},
                     "iron-gear-wheel": {"IN": [["iron-plate", 240]], "OUT": [["iron-gear-wheel", 120]]}},
         "size": [6, 6],
         "inOutPos": {"IN": {"(0,0)": {"ITEM": "copper-plate", "RATE": 0}, "(0,1)": {"ITEM": "iron-plate", "RATE": 0}},
                      "OUT": {"(5,0)": {"ITEM": "automation-science-pack"}}}},
        {"recipes": {"electronic-circuit": {"IN": [["iron-plate", 120], ["copper-cable", 360]],
                                            "OUT": [["electronic-circuit", 120]]},
                     "copper-cable": {"IN": [["copper-plate", 120]], "OUT": [["copper-cable", 240]]}}, "size": [6, 6],
         "inOutPos": {"IN": {"(0,0)": {"ITEM": "iron-plate", "RATE": 0}, "(0,5)": {"ITEM": "copper-plate", "RATE": 0}},
                      "OUT": {"(5,5)": {"ITEM": "electronic-circuit"}}}},
        {"recipes": {"electronic-circuit": {"IN": [["iron-plate", 120], ["copper-cable", 360]],
                                            "OUT": [["electronic-circuit", 120]]},
                     "copper-cable": {"IN": [["copper-plate", 120]], "OUT": [["copper-cable", 240]]}}, "size": [6, 6],
         "inOutPos": {"IN": {"(0,0)": {"ITEM": "iron-plate", "RATE": 0}, "(0,1)": {"ITEM": "copper-plate", "RATE": 0}},
                      "OUT": {"(5,0)": {"ITEM": "electronic-circuit"}}}},
        {"recipes": {"electronic-circuit": {"IN": [["iron-plate", 120], ["copper-cable", 360]],
                                            "OUT": [["electronic-circuit", 120]]},
                     "copper-cable": {"IN": [["copper-plate", 120]], "OUT": [["copper-cable", 240]]}}, "size": [6, 6],
         "inOutPos": {"IN": {"(0,0)": {"ITEM": "iron-plate", "RATE": 0}, "(0,5)": {"ITEM": "copper-plate", "RATE": 0}},
                      "OUT": {"(5,0)": {"ITEM": "electronic-circuit"}, "(5,5)": {"ITEM": "electronic-circuit"}}}},
        {"recipes": {"electronic-circuit": {"IN": [["iron-plate", 120], ["copper-cable", 360]],
                                            "OUT": [["electronic-circuit", 120]]},
                     "copper-cable": {"IN": [["copper-plate", 120]], "OUT": [["copper-cable", 240]]}}, "size": [6, 6],
         "inOutPos": {"IN": {"(0,0)": {"ITEM": "copper-plate", "RATE": 0}, "(0,1)": {"ITEM": "iron-plate", "RATE": 0}},
                      "OUT": {"(5,5)": {"ITEM": "electronic-circuit"}}}},
        {"recipes": {
            "piercing-rounds-magazine": {"IN": [["copper-plate", 100], ["steel-plate", 20], ["firearm-magazine", 20]],
                                         "OUT": [["piercing-rounds-magazine", 20]]},
            "firearm-magazine": {"IN": [["iron-plate", 240]], "OUT": [["firearm-magazine", 60]]}}, "size": [6, 6],
         "inOutPos": {"IN": {"(0,0)": {"ITEM": "copper-plate", "RATE": 0}, "(0,1)": {"ITEM": "steel-plate", "RATE": 0},
                             "(0,2)": {"ITEM": "iron-plate", "RATE": 0}},
                      "OUT": {"(5,5)": {"ITEM": "piercing-rounds-magazine"}}}},
        {"recipes": {
            "piercing-rounds-magazine": {"IN": [["copper-plate", 100], ["steel-plate", 20], ["firearm-magazine", 20]],
                                         "OUT": [["piercing-rounds-magazine", 20]]},
            "firearm-magazine": {"IN": [["iron-plate", 240]], "OUT": [["firearm-magazine", 60]]}}, "size": [6, 6],
         "inOutPos": {"IN": {"(0,0)": {"ITEM": "copper-plate", "RATE": 0}, "(0,1)": {"ITEM": "steel-plate", "RATE": 0},
                             "(0,5)": {"ITEM": "iron-plate", "RATE": 0}},
                      "OUT": {"(5,5)": {"ITEM": "piercing-rounds-magazine"}}}},
        {"recipes": {
            "piercing-rounds-magazine": {"IN": [["copper-plate", 100], ["steel-plate", 20], ["firearm-magazine", 20]],
                                         "OUT": [["piercing-rounds-magazine", 20]]},
            "firearm-magazine": {"IN": [["iron-plate", 240]], "OUT": [["firearm-magazine", 60]]}}, "size": [6, 6],
         "inOutPos": {"IN": {"(0,0)": {"ITEM": "copper-plate", "RATE": 0}, "(0,1)": {"ITEM": "steel-plate", "RATE": 0},
                             "(5,0)": {"ITEM": "iron-plate", "RATE": 0}},
                      "OUT": {"(5,5)": {"ITEM": "piercing-rounds-magazine"}}}},
        {"recipes": {"fusion-reactor-equipment": {"IN": [["processing-unit", 1200], ["low-density-structure", 300]],
                                                  "OUT": [["fusion-reactor-equipment", 6]]},
                     "low-density-structure": {"IN": [["copper-plate", 60], ["steel-plate", 6], ["plastic-bar", 15]],
                                               "OUT": [["low-density-structure", 3]]}}, "size": [6, 6], "inOutPos": {
            "IN": {"(0,0)": {"ITEM": "processing-unit", "RATE": 0}, "(0,1)": {"ITEM": "copper-plate", "RATE": 0},
                   "(0,2)": {"ITEM": "steel-plate", "RATE": 0}, "(0,3)": {"ITEM": "plastic-bar", "RATE": 0}},
            "OUT": {"(0,5)": {"ITEM": "fusion-reactor-equipment"}}}},
        {"recipes": {"automation-science-pack": {"IN": [["copper-plate", 12], ["iron-gear-wheel", 12]],
                                                 "OUT": [["automation-science-pack", 12]]},
                     "iron-gear-wheel": {"IN": [["iron-plate", 240]], "OUT": [["iron-gear-wheel", 120]]}},
         "size": [7, 7],
         "inOutPos": {"IN": {"(0,0)": {"ITEM": "copper-plate", "RATE": 0}, "(0,6)": {"ITEM": "iron-plate", "RATE": 0}},
                      "OUT": {"(6,6)": {"ITEM": "automation-science-pack"}}}},
        {"recipes": {"automation-science-pack": {"IN": [["copper-plate", 12], ["iron-gear-wheel", 12]],
                                                 "OUT": [["automation-science-pack", 12]]},
                     "iron-gear-wheel": {"IN": [["iron-plate", 240]], "OUT": [["iron-gear-wheel", 120]]}},
         "size": [7, 7], "inOutPos": {
            "IN": {"(0,0)": {"ITEM": "copper-plate", "RATE": 0}, "(0,1)": {"ITEM": "copper-plate", "RATE": 0},
                   "(0,2)": {"ITEM": "copper-plate", "RATE": 0}, "(0,5)": {"ITEM": "iron-plate", "RATE": 0},
                   "(0,6)": {"ITEM": "iron-plate", "RATE": 0}},
            "OUT": {"(5,6)": {"ITEM": "automation-science-pack"}, "(6,6)": {"ITEM": "automation-science-pack"}}}},
        {"recipes": {
            "piercing-rounds-magazine": {"IN": [["copper-plate", 100], ["steel-plate", 20], ["firearm-magazine", 20]],
                                         "OUT": [["piercing-rounds-magazine", 20]]},
            "firearm-magazine": {"IN": [["iron-plate", 240]], "OUT": [["firearm-magazine", 60]]}}, "size": [7, 7],
         "inOutPos": {"IN": {"(0,0)": {"ITEM": "copper-plate", "RATE": 0}, "(0,1)": {"ITEM": "steel-plate", "RATE": 0},
                             "(0,2)": {"ITEM": "iron-plate", "RATE": 0}},
                      "OUT": {"(5,0)": {"ITEM": "piercing-rounds-magazine"},
                              "(6,0)": {"ITEM": "piercing-rounds-magazine"}}}},
        {"recipes": {"fusion-reactor-equipment": {"IN": [["processing-unit", 1200], ["low-density-structure", 300]],
                                                  "OUT": [["fusion-reactor-equipment", 6]]},
                     "low-density-structure": {"IN": [["copper-plate", 60], ["steel-plate", 6], ["plastic-bar", 15]],
                                               "OUT": [["low-density-structure", 3]]}}, "size": [7, 7], "inOutPos": {
            "IN": {"(0,0)": {"ITEM": "copper-plate", "RATE": 0}, "(0,1)": {"ITEM": "steel-plate", "RATE": 0},
                   "(0,2)": {"ITEM": "plastic-bar", "RATE": 0}, "(0,3)": {"ITEM": "processing-unit", "RATE": 0}},
            "OUT": {"(6,0)": {"ITEM": "fusion-reactor-equipment"}}}},
        {"recipes": {"fusion-reactor-equipment": {"IN": [["processing-unit", 1200], ["low-density-structure", 300]],
                                                  "OUT": [["fusion-reactor-equipment", 6]]},
                     "low-density-structure": {"IN": [["copper-plate", 60], ["steel-plate", 6], ["plastic-bar", 15]],
                                               "OUT": [["low-density-structure", 3]]}}, "size": [7, 7], "inOutPos": {
            "IN": {"(0,0)": {"ITEM": "copper-plate", "RATE": 0}, "(0,1)": {"ITEM": "steel-plate", "RATE": 0},
                   "(0,2)": {"ITEM": "plastic-bar", "RATE": 0}, "(0,3)": {"ITEM": "processing-unit", "RATE": 0}},
            "OUT": {"(6,6)": {"ITEM": "fusion-reactor-equipment"}}}},
        {"recipes": {"fast-transport-belt": {"IN": [["iron-gear-wheel", 600], ["transport-belt", 120]],
                                             "OUT": [["fast-transport-belt", 120]]},
                     "iron-gear-wheel": {"IN": [["iron-plate", 240]], "OUT": [["iron-gear-wheel", 120]]},
                     "transport-belt": {"IN": [["iron-plate", 120], ["iron-gear-wheel", 120]],
                                        "OUT": [["transport-belt", 240]]}}, "size": [7, 7],
         "inOutPos": {"IN": {"(0,0)": {"ITEM": "iron-gear-wheel", "RATE": 0}},
                      "OUT": {"(0,1)": {"ITEM": "fast-transport-belt"}}}},
        {"recipes": {"burner-mining-drill": {"IN": [["iron-plate", 90], ["iron-gear-wheel", 90], ["stone-furnace", 30]],
                                             "OUT": [["burner-mining-drill", 30]]},
                     "iron-gear-wheel": {"IN": [["iron-plate", 240]], "OUT": [["iron-gear-wheel", 120]]},
                     "stone-furnace": {"IN": [["stone", 600]], "OUT": [["stone-furnace", 120]]}}, "size": [7, 7],
         "inOutPos": {"IN": {"(0,0)": {"ITEM": "iron-plate", "RATE": 0}, "(0,1)": {"ITEM": "stone", "RATE": 0}},
                      "OUT": {"(0,6)": {"ITEM": "burner-mining-drill"}}}},
        {"recipes": {"fast-transport-belt": {"IN": [["iron-gear-wheel", 600], ["transport-belt", 120]],
                                             "OUT": [["fast-transport-belt", 120]]},
                     "iron-gear-wheel": {"IN": [["iron-plate", 240]], "OUT": [["iron-gear-wheel", 120]]},
                     "transport-belt": {"IN": [["iron-plate", 120], ["iron-gear-wheel", 120]],
                                        "OUT": [["transport-belt", 240]]}}, "size": [8, 8],
         "inOutPos": {"IN": {"(0,0)": {"ITEM": "iron-plate", "RATE": 0}},
                      "OUT": {"(7,7)": {"ITEM": "fast-transport-belt"}}}},
        {"recipes": {"burner-mining-drill": {"IN": [["iron-plate", 90], ["iron-gear-wheel", 90], ["stone-furnace", 30]],
                                             "OUT": [["burner-mining-drill", 30]]},
                     "iron-gear-wheel": {"IN": [["iron-plate", 240]], "OUT": [["iron-gear-wheel", 120]]},
                     "stone-furnace": {"IN": [["stone", 600]], "OUT": [["stone-furnace", 120]]}}, "size": [8, 8],
         "inOutPos": {"IN": {"(0,7)": {"ITEM": "iron-plate", "RATE": 0}, "(1,7)": {"ITEM": "iron-plate", "RATE": 0},
                             "(2,7)": {"ITEM": "stone", "RATE": 0}}, "OUT": {"(7,7)": {"ITEM": "burner-mining-drill"}}}},
        {"recipes": {
            "red-wire": {"IN": [["copper-cable", 120], ["electronic-circuit", 120]], "OUT": [["red-wire", 120]]},
            "copper-cable": {"IN": [["copper-plate", 120]], "OUT": [["copper-cable", 240]]},
            "electronic-circuit": {"IN": [["iron-plate", 120], ["copper-cable", 360]],
                                   "OUT": [["electronic-circuit", 120]]}}, "size": [8, 8], "inOutPos": {
            "IN": {"(0,0)": {"ITEM": "copper-plate", "RATE": 0}, "(0,1)": {"ITEM": "copper-plate", "RATE": 0},
                   "(0,2)": {"ITEM": "iron-plate", "RATE": 0}}, "OUT": {"(7,7)": {"ITEM": "red-wire"}}}},
        {"recipes": {"advanced-circuit": {"IN": [["plastic-bar", 20], ["copper-cable", 40], ["electronic-circuit", 20]],
                                          "OUT": [["advanced-circuit", 10]]},
                     "copper-cable": {"IN": [["copper-plate", 120]], "OUT": [["copper-cable", 240]]},
                     "electronic-circuit": {"IN": [["iron-plate", 120], ["copper-cable", 360]],
                                            "OUT": [["electronic-circuit", 120]]}}, "size": [8, 8], "inOutPos": {
            "IN": {"(0,0)": {"ITEM": "iron-plate", "RATE": 0}, "(0,7)": {"ITEM": "copper-plate", "RATE": 0},
                   "(7,0)": {"ITEM": "plastic-bar", "RATE": 0}}, "OUT": {"(7,7)": {"ITEM": "advanced-circuit"}}}},
        {"recipes": {"advanced-circuit": {"IN": [["plastic-bar", 20], ["copper-cable", 40], ["electronic-circuit", 20]],
                                          "OUT": [["advanced-circuit", 10]]},
                     "copper-cable": {"IN": [["copper-plate", 120]], "OUT": [["copper-cable", 240]]},
                     "electronic-circuit": {"IN": [["iron-plate", 120], ["copper-cable", 360]],
                                            "OUT": [["electronic-circuit", 120]]}}, "size": [8, 8], "inOutPos": {
            "IN": {"(0,0)": {"ITEM": "iron-plate", "RATE": 0}, "(0,1)": {"ITEM": "plastic-bar", "RATE": 0},
                   "(0,2)": {"ITEM": "copper-plate", "RATE": 0}}, "OUT": {"(0,7)": {"ITEM": "advanced-circuit"}}}},
        {"recipes": {"poison-capsule": {"IN": [["coal", 75], ["steel-plate", 22.5], ["electronic-circuit", 22.5]],
                                        "OUT": [["poison-capsule", 7.5]]},
                     "electronic-circuit": {"IN": [["iron-plate", 120], ["copper-cable", 360]],
                                            "OUT": [["electronic-circuit", 120]]},
                     "copper-cable": {"IN": [["copper-plate", 120]], "OUT": [["copper-cable", 240]]}}, "size": [8, 8],
         "inOutPos": {"IN": {"(0,0)": {"ITEM": "coal", "RATE": 0}, "(0,1)": {"ITEM": "steel-plate", "RATE": 0},
                             "(0,2)": {"ITEM": "iron-plate", "RATE": 0}, "(0,3)": {"ITEM": "copper-plate", "RATE": 0}},
                      "OUT": {"(7,7)": {"ITEM": "poison-capsule"}}}},
        {"recipes": {"poison-capsule": {"IN": [["coal", 75], ["steel-plate", 22.5], ["electronic-circuit", 22.5]],
                                        "OUT": [["poison-capsule", 7.5]]},
                     "electronic-circuit": {"IN": [["iron-plate", 120], ["copper-cable", 360]],
                                            "OUT": [["electronic-circuit", 120]]},
                     "copper-cable": {"IN": [["copper-plate", 120]], "OUT": [["copper-cable", 240]]}}, "size": [8, 8],
         "inOutPos": {"IN": {"(0,0)": {"ITEM": "coal", "RATE": 0}, "(0,1)": {"ITEM": "steel-plate", "RATE": 0},
                             "(0,2)": {"ITEM": "iron-plate", "RATE": 0}, "(0,3)": {"ITEM": "copper-plate", "RATE": 0}},
                      "OUT": {"(7,0)": {"ITEM": "poison-capsule"}}}}

    ]
    n_instance = 0
    for data in instances_to_solve:
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
            solver.model_to_image(n_instance)
        instance_model = solver.model_to_json(n_instance)
        n_instance += 1


if __name__ == '__main__':
    _app.run(debug=False)

