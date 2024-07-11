from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import requests
import json
import os


def fetch_weather_data(city, api_key='5471ce6e8cefd8d140ae2505e58ab941'):
    '''
    Функция выполняет запрос к API и возвращает ответ в JSON формате.
    city - выбранный город;
    api_key - ключ для использования API(рекомендуется не задавать явно).
    '''
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()


def download_data(**kwargs):
    city = "London"
    weather_data = fetch_weather_data(city)
    
    # Определение текущей директории и создание папки tmp
    current_dir = os.getcwd()
    output_dir = os.path.join(current_dir, "tmp")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Сохранение данных в локальный файл weather_data.json
    output_path = os.path.join(output_dir, "weather_data.json")
    with open(output_path, "w") as file:
        json.dump(weather_data, file)
    
    # Сохранение пути к файлу в xcom
    kwargs['ti'].xcom_push(key='output_path', value=output_path)


def process_data(**kwargs):
    # Получение пути к файлу с данными из предыдущей задачи
    output_path = kwargs['ti'].xcom_pull(key='output_path')
    
    # Загрузка данных из локального файла weather_data.json
    with open(output_path, "r") as file:
        weather_data = json.load(file)

    # Преобразование данных в DataFrame
    df = pd.json_normalize(weather_data)

    def kelvin_to_celsius(kelvin):
        return kelvin - 273.15

    # Преобразование температур из кельвин в цельсии
    if 'main.temp' in df.columns:
        df['main.temp'] = df['main.temp'].apply(kelvin_to_celsius)
    if 'main.feels_like' in df.columns:
        df['main.feels_like'] = df['main.feels_like'].apply(kelvin_to_celsius)
    if 'main.temp_min' in df.columns:
        df['main.temp_min'] = df['main.temp_min'].apply(kelvin_to_celsius)
    if 'main.temp_max' in df.columns:
        df['main.temp_max'] = df['main.temp_max'].apply(kelvin_to_celsius)

    # Сохранение обработанных данных в файл processed_weather_data.csv
    processed_output_path = os.path.join(os.getcwd(), "processed_weather_data.csv")
    df.to_csv(processed_output_path, index=False)

    # Сохранение пути к обработанному файлу в xcom
    kwargs['ti'].xcom_push(key='processed_output_path', value=processed_output_path)


def save_data(**kwargs):
    # Получение пути к обработанному файлу processed_weather_data.csv из предыдущей задачи
    processed_output_path = kwargs['ti'].xcom_pull(key='processed_output_path')
    processed_df = pd.read_csv(processed_output_path)

    # Сохранение данных в файл Parquet
    parquet_output_path = os.path.join(os.getcwd(), "weather.parquet")
    if os.path.exists(parquet_output_path):
        existing_df = pd.read_parquet(parquet_output_path)
        processed_df = pd.concat([existing_df, processed_df], ignore_index=True)
    processed_df.to_parquet(parquet_output_path, index=False)


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 7, 11, 19, 2, 0),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'weather_data_pipeline_dag',
    default_args=default_args,
    description='A simple weather data pipeline DAG',
    schedule_interval=timedelta(minutes=1),
)

download_data_task = PythonOperator(
    task_id='download_data',
    python_callable=download_data,
    provide_context=True,
    dag=dag,
)

process_data_task = PythonOperator(
    task_id='process_data',
    python_callable=process_data,
    provide_context=True,
    dag=dag,
)

save_data_task = PythonOperator(
    task_id='save_data',
    python_callable=save_data,
    provide_context=True,
    dag=dag,
)

download_data_task >> process_data_task >> save_data_task
