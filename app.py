# .venv\Scripts\activate
# pip install Flask-SQLAlchemy
# pip install -U flask-cors
# pip install Flask-SocketIO
from flask import Flask, request, jsonify
from datetime import datetime
# import openpyxl
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from flask import render_template


app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

# Global dictionary to store relay states
relay_states = {
    "relay1": "off",
    "relay2": "off",
    "relay3": "off",
    "relay4":"off",
    "relay5":"off",
}

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sensor_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the SensorData model
class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    waterTemperature = db.Column(db.Float, nullable=False)
    waterLevel = db.Column(db.Float, nullable=False)
    phValue = db.Column(db.Float, nullable=False)

# Create the database and the table
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return 'Hello, World!'

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@app.route('/sensor-data', methods=['POST'])
def receive_sensor_data():
    data = request.json
    humidity = data.get('humidity')
    temperature = data.get('temperature')
    waterTemperature = data.get('waterTemperature')
    waterLevel = data.get('waterLevel')
    phValue = data.get('phValue')
    # date = data.get('date')
    # time = data.get('time')

    if relay_states['relay5'] == 'on':
        # Check for irregular values and emit WebSocket events
        if waterTemperature < 15 or waterTemperature > 30:
            socketio.emit('notification', {'title': 'Warning', 'body': 'Irregular water temperature detected!'})
            relay_states['relay2'] = 'on'
        else:
            relay_states['relay2'] = 'off'
        if phValue < 6.5 or phValue > 7.5:
            socketio.emit('notification', {'title': 'Warning', 'body': 'Irregular pH value detected!'})
        if waterLevel < 10 or waterLevel > 50:
            socketio.emit('notification', {'title': 'Warning', 'body': 'Irregular water level detected!'})
            # Control relay1 state
            relay_states['relay1'] = 'on'
        else:
            relay_states['relay1'] = 'off'
    else:
                # Check for irregular values and emit WebSocket events
        if waterTemperature < 15 or waterTemperature > 30:
            socketio.emit('notification', {'title': 'Warning', 'body': 'Irregular water temperature detected!'})
        if phValue < 6.5 or phValue > 7.5:
            socketio.emit('notification', {'title': 'Warning', 'body': 'Irregular pH value detected!'})
        if waterLevel < 10 or waterLevel > 50:
            socketio.emit('notification', {'title': 'Warning', 'body': 'Irregular water level detected!'})
     
     # Check if all values are provided
    if None in [humidity, temperature, waterTemperature, waterLevel, phValue]:
        return 'Missing sensor data', 400
    
    date = datetime.now().strftime('%Y-%m-%d')
    time = datetime.now().strftime('%H:%M:%S')
    
    # Create a new SensorData record
    new_record = SensorData(
    date=date,
    time=time, 
    humidity=humidity,
    temperature=temperature,
    waterTemperature=waterTemperature,
    waterLevel=waterLevel,
    phValue=phValue
)
    db.session.add(new_record)
    db.session.commit()
    
    return jsonify({"status": "success"}), 200



@app.route('/sensor-data-records', methods=['GET'])
def get_sensor_data_records():
    
    records = SensorData.query.all()
    data = [
        {"date": record.date,"time":record.time,
            "humidity": record.humidity,
            "temperature": record.temperature,
            "waterTemperature": record.waterTemperature,
            "waterLevel": record.waterLevel,
            "phValue": record.phValue}
        for record in records
    ]
    # return jsonify(data), 200
    return render_template('sensor_data.html', data=data)



@app.route('/latest-sensor-data', methods=['GET'])
def get_latest_sensor_data():
    """
    Retrieve the latest sensor data record.
    """
    latest_record = SensorData.query.order_by(SensorData.id.desc()).first()
    if latest_record:
        data = {
            "date": latest_record.date,
            "time": latest_record.time,
            "humidity": latest_record.humidity,
            "temperature": latest_record.temperature,
            "waterTemperature": latest_record.waterTemperature,
            "waterLevel": latest_record.waterLevel,
            "phValue": latest_record.phValue,
            "relay1": relay_states['relay1'],
            "relay2": relay_states['relay2'],
            "relay3": relay_states['relay3'],
            "relay4": relay_states['relay4'],
            "relay5": relay_states['relay5'],
        }
        return jsonify(data), 200
    else:
        return jsonify({"error": "No sensor data available"}), 404


# @app.route('/sensor-data-by-date', methods=['GET'])
# def get_sensor_data_by_date():
#     """
#     Retrieve sensor data records for a specific date.
#     """
#     date_str = request.args.get('date')
#     if not date_str:
#         return jsonify({"error": "Date parameter is required"}), 400

#     try:
#         date = datetime.strptime(date_str, '%Y-%m-%d').date()
#     except ValueError:
#         return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

#     records = SensorData.query.filter(SensorData.date.like(f"{date}%")).all()
#     if records:
#         data = [
#             {
#                 "date": record.date,
#                 "time": record.time,
#                 "humidity": record.humidity,
#                 "temperature": record.temperature,
#                 "waterTemperature": record.waterTemperature,
#                 "waterLevel": record.waterLevel,
#                 "phValue": record.phValue
#             }
#             for record in records
#         ]
#         return jsonify(data), 200
#     else:
#         return jsonify({"error": "No sensor data available for the specified date"}), 404
@app.after_request
def remove_permissions_policy_header(response):
    response.headers.pop('Permissions-Policy', None)
    return response


@app.route('/sensor-data-by-date', methods=['GET'])
def get_sensor_data_by_date():
    """
    Retrieve sensor data records for a specific date and return an HTML page with graphs.
    """
    date_str = request.args.get('date')
    if not date_str:
        return jsonify({"error": "Date parameter is required"}), 400

    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    records = SensorData.query.filter(SensorData.date.like(f"{date}%")).all()
    if records:
        data = [
            {
                "date": record.date,
                "time": record.time,
                "humidity": record.humidity,
                "temperature": record.temperature,
                "waterTemperature": record.waterTemperature,
                "waterLevel": record.waterLevel,
                "phValue": record.phValue
            }
            for record in records
        ]
        return jsonify(data), 200
        # return render_template('sensor_data.html', data=data, date=date_str)
    else:
        return jsonify({"error": "No sensor data available for the specified date"}), 404


# # List to store sensor data
# sensor_data_records = []


# @app.route('/sensor-data', methods=['POST'])
# def receive_sensor_data():
#     """
#     Receives sensor data from a JSON request, adds a timestamp, 
#     appends it to the sensor data records, and saves the records to an Excel file.

#     Returns:
#         tuple: A JSON response indicating success and an HTTP status code 200.
#     """
#     data = request.json
#     timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     data_with_timestamp = {
#         "timestamp": timestamp,
#         **data
#     }
#     sensor_data_records.append(data_with_timestamp)
#     print(data_with_timestamp)
#     save_to_excel(sensor_data_records)
#     return jsonify({"status": "success"}), 200




# @app.route('/sensor-data-records', methods=['GET'])
# def get_sensor_data_records():
#     """
#     Retrieve sensor data records.

#     This function returns a JSON response containing sensor data records
#     and an HTTP status code 200.

#     Returns:
#         tuple: A tuple containing a JSON response with sensor data records
#                and an HTTP status code 200.
#     """
#     return jsonify(sensor_data_records), 200




# # Endpoint to get the latest sensor data
# @app.route('/latest-sensor-data', methods=['GET'])
# def get_latest_sensor_data():
#     """
#     Retrieve the latest sensor data record.

#     This function checks if there are any sensor data records available.
#     If records are available, it returns the latest record in JSON format with a 200 status code.
#     If no records are available, it returns an error message in JSON format with a 404 status code.

#     Returns:
#         tuple: A tuple containing a JSON response and an HTTP status code.
#     """
#     if sensor_data_records:
#         return jsonify(sensor_data_records[-1]), 200
#     else:
#         return jsonify({"error": "No sensor data available"}), 404
    



# def save_to_excel(data_records):
#     """
#     Save sensor data records to an Excel file.

#     Args:
#         data_records (list of dict): A list of dictionaries where each dictionary contains
#                                      sensor data with keys "timestamp", "humidity", "temperature",
#                                      "waterTemperature", "waterLevel", and "phValue".

#     The function creates a new Excel workbook, writes the headers and data records to the worksheet,
#     and saves the workbook with a filename that includes the current date.
#     """
#     # Create a new workbook and select the active worksheet
#     workbook = openpyxl.Workbook()
#     sheet = workbook.active

#     # Define the headers
#     headers = ["Date", "Time", "humidity", "temperature", "waterTemperature", "waterLevel", "phValue"]

#     # Write the headers to the first row
#     for col_num, header in enumerate(headers, 1):
#         sheet.cell(row=1, column=col_num, value=header)

#     # Write the data records to the worksheet
#     for row_num, record in enumerate(data_records, 2):
#         date, time = record["timestamp"].split()
#         sheet.cell(row=row_num, column=1, value=date)
#         sheet.cell(row=row_num, column=2, value=time)
#         sheet.cell(row=row_num, column=3, value=record["humidity"])
#         sheet.cell(row=row_num, column=4, value=record["temperature"])
#         sheet.cell(row=row_num, column=5, value=record["waterTemperature"])
#         sheet.cell(row=row_num, column=6, value=record["waterLevel"])
#         sheet.cell(row=row_num, column=7, value=record["phValue"])

#     # Get the current date to include in the filename
#     current_date = datetime.now().strftime('%Y-%m-%d')
#     filename = f"sensor_data_records_{current_date}.xlsx"

#     # Save the workbook to a file in the project directory
#     workbook.save(filename)


# Endpoint to control relay
@app.route('/control-relay', methods=['POST'])
def control_relay():
    """
    Controls the relays by sending commands to the ESP32.
    """
    commands = request.json.get('commands')
    if not commands:
        return jsonify({"status": "error", "message": "No commands provided"}), 400

    for relay, state in commands.items():
        if relay in relay_states:
            relay_states[relay] = state
            # Send command to ESP32 to control relay
            print(f"Relay {relay} command: {state}")
            # Here you would send the command to the ESP32, e.g., via serial or network communication

    return jsonify({"status": "success"}), 200

# Endpoint to get the status of the relay
@app.route('/relay-status', methods=['GET'])
def get_relay_status():
    return jsonify(relay_states), 200


if __name__ == '__main__':
    # socketio.run(app)
    app.run(host='0.0.0.0', port=5000,debug=True)
