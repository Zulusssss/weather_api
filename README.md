# weather_api

git clone https://<repository-url>.git
cd weather_api

в WSL
# Обновите пакетный менеджер и установите Python и pip
sudo apt update
sudo apt install python3 python3-pip


mkdir project/
cd project

pip install virtualenv
virtualenv airflow_env
source airflow_env/bin/activate

cp '/mnt/{your path}/requirements.txt' /home/{username}/project/
pip install -r requirements.txt







git clone https://<repository-url>.git
cd /home/{username}/weather_api/

sudo apt update
sudo apt install python3 python3-pip

pip install virtualenv
virtualenv airflow_env
source airflow_env/bin/activate
pip install -r requirements.txt

airflow db migrate
airflow users create --username admin --firstname admin --lastname admin --role Admin --email youremail@email.com

nano /home/{username}/airflow/airflow.cfg
dags_folder = /home/{username}/weather_api/dags

airflow webserver --port 8080 & airflow scheduler
