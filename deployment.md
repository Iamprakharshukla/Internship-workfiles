# Hostinger VPS Docker Deployment Guide

This guide provides the exact steps to deploy the Udaan Society Portal to a Hostinger Virtual Private Server (VPS) using our new Docker architecture.

---

## 🏗️ 1. Server Provisioning & Initial Setup

1. **Log into Hostinger hPanel**: 
   - Purchase or navigate to your VPS plan.
   - Choose **Ubuntu 22.04 LTS** (or 24.04 LTS) as your operating system.
2. **Access your Server**:
   - Open your terminal (or Windows PowerShell/PuTTY).
   - SSH into the server using the IP address provided by Hostinger:
     ```bash
     ssh root@<YOUR_VPS_IP_ADDRESS>
     ```
3. **Update the System**:
   ```bash
   apt update && apt upgrade -y
   ```

---

## 🐳 2. Install Docker & Git

Hostinger Ubuntu servers usually come with a clean slate. You need to install Docker to run our containers.

1. **Install Git, curl, and nano**:
   ```bash
   apt install git curl nano -y
   ```
2. **Install Docker**:
   Run the official Docker installation script:
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   ```
3. **Verify Docker Status**:
   ```bash
   systemctl start docker
   systemctl enable docker
   docker --version
   docker compose version
   ```

---

## 📥 3. Clone the Project & Configure

1. **Clone your GitHub Repository**:
   Change into the `/opt` directory (or `/var/www` if you prefer) and clone the code:
   ```bash
   cd /opt
   git clone <YOUR_GITHUB_REPOSITORY_URL> udaan
   cd udaan
   ```

2. **Configure Environment Variables (CRITICAL)**:
   In a production environment, you *must not* use the default development variables.
   
   Create a `.env` file in the root directory:
   ```bash
   nano .env
   ```
   Paste the following block and modify the values (Use `Ctrl+O`, `Enter`, `Ctrl+X` to save and exit in Nano):
   ```env
   # .env
   DEBUG=False
   SECRET_KEY=generate_a_very_long_random_string_here_like_djfaus8fua98sf
   DJANGO_ALLOWED_HOSTS=<YOUR_DOMAIN.com>,<YOUR_VPS_IP_ADDRESS>
   DATABASE_URL=postgres://udaan_user:udaan_strongpassword@db:5432/udaan_db
   
   # Note: The db credentials here must match the environment variables 
   # you set for the postgres container in docker-compose.yml 
   ```

   *Optional: If you did not pass DB env vars inside `docker-compose.yml` for postgres, define them here as POSTGRES_DB=udaan_db, POSTGRES_USER=udaan_user, POSTGRES_PASSWORD=udaan_strongpassword.*

---

## 🚀 4. Build and Run the App

1. **Start the Docker Containers**:
   ```bash
   docker compose up --build -d
   ```
   *This downloads Python, PostgreSQL, Nginx, installs your packages, and starts everything in the background.*

2. **Verify Containers are Running**:
   ```bash
   docker compose ps
   ```
   *You should see `web`, `nginx`, and `db` services showing as "Up".*

---

## 🗄️ 5. Database Setup (Crucial First Time Step)

Since this is a brand new server, the PostgreSQL database is empty. You must create the schema and admin user.

1. **Run Migrations (and seed Initial Data)**:
   ```bash
   docker compose exec web python manage.py migrate
   ```
2. **Create the Admin Superuser**:
   We built a custom command to do this easily:
   ```bash
   docker compose exec web python manage.py init_admin
   ```
   *This creates the `mail@udaansociety.org` admin account with the temporary `udaanpassword123` password.*

---

## 🔒 6. Domain Setup & SSL (HTTPS)

Right now, the site works on `http://<YOUR_VPS_IP_ADDRESS>`. To use a domain name and make it secure:

1. **DNS Settings**:
   Go to your domain registrar (or Hostinger Domain Panel) and add an **A Record** pointing your domain (e.g., `@` and `www`) to `<YOUR_VPS_IP_ADDRESS>`.

2. **Wait for DNS Propagation**:
   Wait a few minutes (up to an hour) for the domain to point to your server.

3. **Enable HTTPS (Using Certbot/Let's Encrypt)**:
   Since our Nginx is running inside Docker, configuring SSL requires editing the `nginx/default.conf` to handle `certbot` challenges, or using an Nginx-Proxy-Manager. 
   
   *Tip: For easiest Hostinger Docker SSL management, we highly recommend installing **Cloudflare** in front of your domain, which provides automatic SSL and caching for free without changing your Docker configuration!*

---

🎉 **Congratulations! Your application is now Live on Hostinger!**
Log into the domain `/admin/` and change your password immediately.
