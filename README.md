## Инструкция по запуску(WSL/Linux)
Клонируйте репозиторий:
```
git clone https://<repository-url>.git
cd /home/{username}/weather_api/
```

Обновите пакетный менеджер и установите Python и pip:
```
sudo apt update
sudo apt install python3 python3-pip
```

Создайте виртульное окружение и установите зависимости:
```
pip install virtualenv
virtualenv airflow_env
source airflow_env/bin/activate
pip install -r requirements.txt
```

Создайте базу данных для airflow:
```
airflow db migrate
```

Создайте учётную запись администратора:
```
airflow users create --username admin --firstname admin --lastname admin --role Admin --email youremail@email.com
```

Измените значение dags_folder в airflow.cfg, чтобы стал доступен ваш DAG:
```
nano /home/{username}/airflow/airflow.cfg
dags_folder = /home/{username}/weather_api/dags
```

Запустите веб-сервер и планировщик airflow:
```
airflow webserver --port 8080 & airflow scheduler
```
