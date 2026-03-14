# Udaan Society Web Portal - Production Deployment Guide

This guide outlines the complete setup process for running the Udaan Society Web Portal in a production environment using Docker and PostgreSQL. 

The application architecture includes three dedicated containers:
- **Nginx**: Web Server (Port 80) serving static/media files and proxying requests.
- **Web (Gunicorn)**: The Django Application handling core logic (Port 8000 internally).
- **Database (PostgreSQL 15)**: The relational database managing all data.

---

## 🚀 1. Complete System Build & Startup
Whenever you deploy the code to a new server, pull updates via Git, or modify `requirements.txt`, you should run the build command.

Ensure you are inside the `/udaan` project directory and run:

```bash
docker compose up --build -d
```
*The `-d` flag runs the containers in the background (detached mode) so your terminal stays free.*

You can check if the containers are successfully running by executing:
```bash
docker compose ps
```

---

## 📦 2. Database Migrations & Seeding (First-Time Setup)
Although the Startup Script (`entrypoint.sh`) attempts to auto-migrate the database when the container boots, it's good practice to ensure everything is initialized—especially if migrations contain seed data.

Run the migrations manually inside the running web container:
```bash
docker compose exec web python manage.py migrate
```
*This command will apply your database schema and execute `populate_projects`, injecting the initial content into the Postgres database.*

---

## 👤 3. Creating the Master Admin User
Once the database is ready, you must create a Master Admin (Superuser) to log into the Django Admin dashboard and Udaan Portal.

To make this effortless, we've created a custom deployment script specifically for Udaan Society. Run this command:

```bash
docker compose exec web python manage.py init_admin
```

This will generate the default Administrative user:
- **Username**: `admin`
- **Email**: `mail@udaansociety.org`
- **Temporary Password**: `udaanpassword123`

### 🛡️ 4. Immediate Security: Changing the Admin Password
As soon as the user is generated, you must change the default password.

1. Open a web browser and navigate to: **http://localhost/admin/** or `http://<YOUR_SERVER_IP>/admin/`
2. Log in using `admin` and `udaanpassword123`.
3. In the upper-right hand corner of the dashboard, click **"CHANGE PASSWORD"**.
4. Enter the temporary password in the first box, and your new *secure* password twice.
5. Click **Change Password**.

*(Alternatively, to force a reset via the terminal if you get locked out, run: `docker compose exec web python manage.py changepassword admin`)*

---

## 🛠️ 5. Routine Maintenance Commands

### Viewing Live Logs
If the site crashes or you want to see who is visiting:
```bash
docker compose logs -f
```

### Stopping the Server
To safely shut down the containers while preserving the data:
```bash
docker compose down
```

### 🛑 Full Factory Reset (DANGER)
If you need to completely nuke the development environment, wipe the database clean, and delete all uploaded images to start fresh:
```bash
docker compose down -v
```
*Warning: This will permanently delete the PostgreSQL Volume and all uploaded media files.*
