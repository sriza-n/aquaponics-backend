import requests
import pandas as pd
import matplotlib.pyplot as plt

def get_sensor_data_by_date(date):
    response = requests.get(f'http://192.168.1.5:5000/sensor-data-by-date?date={date}')
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching data:", response.json())
        return []

def process_sensor_data(sensor_data):
    df = pd.DataFrame(sensor_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def plot_sensor_data(df):
    plt.figure(figsize=(12, 8))

    plt.subplot(2, 3, 1)
    plt.plot(df['timestamp'], df['humidity'], label='Humidity')
    plt.xlabel('Timestamp')
    plt.ylabel('Humidity')
    plt.title('Humidity Over Time')
    plt.legend()

    plt.subplot(2, 3, 2)
    plt.plot(df['timestamp'], df['temperature'], label='Temperature')
    plt.xlabel('Timestamp')
    plt.ylabel('Temperature')
    plt.title('Temperature Over Time')
    plt.legend()

    plt.subplot(2, 3, 3)
    plt.plot(df['timestamp'], df['waterTemperature'], label='Water Temperature')
    plt.xlabel('Timestamp')
    plt.ylabel('Water Temperature')
    plt.title('Water Temperature Over Time')
    plt.legend()

    plt.subplot(2, 3, 4)
    plt.plot(df['timestamp'], df['waterLevel'], label='Water Level')
    plt.xlabel('Timestamp')
    plt.ylabel('Water Level')
    plt.title('Water Level Over Time')
    plt.legend()

    plt.subplot(2, 3, 5)
    plt.plot(df['timestamp'], df['phValue'], label='pH Value')
    plt.xlabel('Timestamp')
    plt.ylabel('pH Value')
    plt.title('pH Value Over Time')
    plt.legend()

    plt.tight_layout()
    plt.show()

# Example usage
date = '2024-6-21'
sensor_data = get_sensor_data_by_date(date)
df = process_sensor_data(sensor_data)
plot_sensor_data(df)
