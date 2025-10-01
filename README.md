# BatMon 🦇

**BatMon** is an open-source status page and monitoring platform built with Django.  
It continuously checks your services (**Ping, HTTP, TCP**) and provides a clean status dashboard with uptime history and beautiful charts.  

---

## ✨ Features
- 🔍 **Service monitoring**: ping, HTTP requests, TCP checks  
- 📊 **Historical data & charts**: latency, uptime, and response times  
- 🌐 **Public status page**: real-time updates for your users  
- 📢 **Alerting system**: email, Telegram, webhooks, or custom commands  
- ⚡ **Smart triggers**: conditions like N failures in a row, recovery events  
- 🛠️ **Scheduled maintenance**: mark services as “under maintenance” to avoid false alarms  
- 📋 **Admin dashboard**: manage services, alerts, and maintenance windows  
- 🔌 **Extensible**: add new check types or alert integrations  

---

## 🛠️ Tech stack
- [Django 5](https://www.djangoproject.com/)  
- [Celery](https://docs.celeryq.dev/) + [Redis](https://redis.io/) (async tasks & scheduling)  
- [PostgreSQL](https://www.postgresql.org/)  
- [Bootstrap 5](https://getbootstrap.com/) + [Chart.js](https://www.chartjs.org/) (frontend)  
- [Docker Compose](https://docs.docker.com/compose/) (deployment)  

---

## 🚀 Quick start (with Docker)

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/batmon.git
   cd batmon

2. Start the services with Docker:
    ```bash
    docker-compose up -d


3. Run migrations and create a superuser:
    ```bash
    docker-compose exec web python manage.py migrate
    docker-compose exec web python manage.py createsuperuser


4. Access:
    ```bash
    Admin dashboard → http://localhost:8000/admin/

    Status page → http://localhost:8000/status/

📂 Project structure

    batmon/
    ├── checks/          # Monitoring checks (Ping, HTTP, TCP)
    ├── alerts/          # Alert integrations (Email, Telegram, Webhook, Commands)
    ├── maintenance/     # Scheduled maintenance windows
    ├── dashboard/       # Internal dashboard views
    ├── statuspage/      # Public status page
    ├── docker-compose.yml
    └── README.md

🤝 Contributing

    Contributions, issues, and feature requests are welcome!
    Feel free to open an issue
    or submit a pull request.

📜 License

    This project is licensed under the Apache License 2.0 – see the LICENSE
    file for details.

💡 Inspiration

    The name BatMon comes from bats, animals that use echolocation (sonar) to navigate and detect obstacles — just like BatMon continuously checks and detects the health of your services.