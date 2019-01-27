import json
import os

import numpy as np
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

UPLOAD_FOLDER = '/static/assets'
app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET'])
def process():
    if request.method == 'GET':
        input_data = dict(request.args)

        # If there is no input data, send the index.html
        if input_data == {}:
            return app.send_static_file('index.html')
        # else:
        #     print('------------------------')
        #     print('Input Data: ', input_data)
        #     print('------------------------')
        #     move = input_data['move_sent_to_py'][0]
        #     position = input_data['position'][0]
        #     computer_color = input_data['ComputerColor'][0]

        #     engine = Engine(move, position, computer_color)
        #     jsonified = jsonify(engine.build_output_data())
        #     return jsonified
    
@app.route('/uploaded', methods=['GET','POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file'];      
        file.save(file.filename);     
        print("This is the file: ",file);

        # 


        return 'OK'

if __name__ == '__main__':
    app.run(debug=True)