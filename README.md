to run on https -> https://ngrok.com/download
pip3 install -r requirements.txt
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver localhost:1234
ngrok http 1234