# Fireworks Shop Bot — Telegram Bot and FastAPI API for Fireworks Sales

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/fastapi-%2300C7B7.svg?style=for-the-badge&logo=fastapi&logoColor=white)
![Telegram Bot](https://img.shields.io/badge/python--telegram--bot-%2300A1E0.svg?style=for-the-badge&logo=telegram&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/postgresql-%23336791.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![NGINX](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/sqlalchemy-%23F47216.svg?style=for-the-badge&logo=python&logoColor=white)
![Alembic](https://img.shields.io/badge/alembic-%230071C5.svg?style=for-the-badge&logo=alembic&logoColor=white)
![APScheduler](https://img.shields.io/badge/apscheduler-%2300A1E0.svg?style=for-the-badge&logo=python&logoColor=white)
![SQLAdmin](https://img.shields.io/badge/sqladmin-%2300C7B7.svg?style=for-the-badge&logo=fastapi&logoColor=white)

---

## Project Description

The project was developed on behalf of a fireworks supplier to automate retail order processing through a Telegram bot.
The goal is to provide users with an easy way to choose and purchase fireworks, and to give administrators convenient tools for managing products and newsletters.
Access to ordering is available only to users over 18 years old.
The backend is implemented with FastAPI, responsible solely for processing requests from the bot via the server's local API address.

Main functionality:
- Viewing products, filtering by categories, tags, prices, and other characteristics.
- Placing and tracking orders via the Telegram bot.
- Sending newsletters to users using APScheduler, with advanced recipient filtering.
- Database administration via the SQLAdmin-based management panel.
- Asynchronous service operation using FastAPI and SQLAlchemy.

## ⚠️ Project Status

This project is currently under active development.  
Some features in the Telegram bot are temporarily unavailable — for example, the order placement and certain buttons are disabled.

Please note that the current version is not final.

## Getting Started

### Deploying the Project to a Server
Deployment is configured through GitHub Actions. When pushing to branches develop, master, or feature/develop, images are automatically built and delivered to the server.

Requirements for proper operation:
- Docker and Docker Compose must be installed on the server.
- A project directory must exist on the server at /opt/fireworks_shop_bot/.
- A .env file must be located in this directory, based on infra/.env.example.
- Ensure that the TELEGRAM_BOT_TOKEN variable is set in the .env file.
- GitHub repository secrets must be configured:
  - HOST — server IP address
  - USER — SSH username
  - SSH_KEY — private SSH key
  - SSH_PASSPHRASE — password for the SSH key (if applicable)
  - DOCKER_USERNAME and DOCKER_PASSWORD — Docker Hub credentials

Deployment process:

After committing to the specified branches, GitHub Actions:

- builds images for the application, bot, and nginx
- pushes them to Docker Hub
- connects to the server via SSH
- copies docker-compose.yaml to the server
- executes the following commands:

### Local Project Launch (for Development Purposes Only)
⚠️ The project uses nginx for request proxying and Webhook for Telegram bot operation.
A public IP address is required for full functionality.
Local launch is possible only after making the following changes:
- Replace all references to nginx:8000 with 127.0.0.1:8000 in the code.
- Switch the Telegram bot to Polling mode instead of Webhook:
  - navigate to src/bot/main.py, comment out the run_webhook block, and uncomment the polling block.

Steps for local development:
1. Install Python version 3.12+
2. Clone the repository
```bash
- git clone https://github.com/your_username/fireworks-shop-bot.git
```
Navigate to the created local repository.

3. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

4. Update pip if necessary
```bash
pip install --upgrade pip
```

5. Install dependencies
```bash
pip install -r src/requirements.txt
pip install -r requirements_style.txt  # for development purposes
```

6. Create a .env file:
- Based on infra/.env.example, create a .env file in the same folder.
- Fill it in with the required data.

7. Start the project using Docker Compose
(Ensure Docker is running.)
```bash
docker compose -f infra/docker-compose.local.yaml up -d
```

### Additional Information
API documentation is available after launching the server at:
- `http://localhost:8000/docs` — Swagger UI
- `http://localhost:8000/redoc` — Redoc UI

### Project Team
- Team Lead Alexander Kelesidis [Keleseth](https://github.com/Keleseth)
- Developer Konstantin Pohodyaev [KonstantinPohodyaev](https://github.com/KonstantinPohodyaev)
- Developer Evgeniy Lepyokha [Evgn22](https://github.com/Evgn22)
- Developer Sergey Varyukhov [s1zeist](https://github.com/s1zeist)
- Developer Savva Velikorodov [OoopsDope](https://github.com/OoopsDope)
- Developer Stepan Gerasimov [Stepan22042004](https://github.com/Stepan22042004)
- Developer Vadim Pronkin [mrvadzzz](https://github.com/mrvadzzz)
