# 🚀 FASTAPI DEPLOY CHEATSHEET (Linux + Docker + Nginx)

## 🧭 Навігація в терміналі

* pwd                 # показати поточну директорію
* ls -la              # список файлів з деталями
* cd /path/to/project # перейти в каталог проекту
* cd ..               # на рівень вище
* 

## 🗂 Робота з файлами

* cat .env                # переглянути файл .env
* nano .env               # відредагувати .env
* touch Dockerfile        # створити новий файл
* mkdir app               # створити папку
* rm -rf old_folder       # видалити папку з вмістом
* mv old.py new.py        # перейменувати або перемістити файл

## ⚙️ Python / FastAPI локально

* python3 -m venv .venv
* source .venv/bin/activate
* pip install -r requirements.txt
* 
* uvicorn main:app --host 0.0.0.0 --port 8000 --reload

## 🐳 Docker / Docker Compose

* docker compose build                # зібрати образи
* docker compose up -d                # запустити контейнери у фоні
* docker compose down                 # зупинити і видалити контейнери
* docker compose logs backend         # подивитись логи бекенду
* docker compose exec backend bash    # зайти в контейнер бекенду
* docker ps                           # перевірити, що контейнери працюють

## 🌐 Nginx

## 📄 Конфіг приклад:

`server {
    server_name example.com;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}`

## 📋 Команди:

`sudo nginx -t  `                 # перевірити конфігурацію
`sudo systemctl restart nginx`    # перезапустити nginx
`sudo systemctl status nginx   `  # перевірити статус

## 🔥 Systemd (якщо запускаєш без Docker)

* /etc/systemd/system/fastapi.service
* [Unit]
* Description=FastAPI App
* After=network.target
* 
* [Service]
* User=ubuntu
* WorkingDirectory=/home/ubuntu/app
* ExecStart=/home/ubuntu/app/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
* Restart=always
* 
* [Install]
* WantedBy=multi-user.target

## 📋 Команди:

`sudo systemctl daemon-reload`
`sudo systemctl enable fastapi`
`sudo systemctl start fastapi`
`sudo systemctl status fastapi`
`sudo journalctl -u fastapi -f `   # перегляд логів у реальному часі

## 🧩 Перевірка портів і мережі

* curl http://localhost:8000/docs
* ping google.com
* netstat -tulnp | grep 8000

## 🪣 Керування правами

* sudo chown -R $USER:$USER /path/to/project
* chmod +x start.sh
* 

## 💡 Корисне

* sudo apt update && sudo apt upgrade -y
* sudo apt install docker docker-compose nginx -y
* htop                     # перегляд процесів
* df -h                    # перевірити вільне місце
* 