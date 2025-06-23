# Docker Development & Deployment Procedure

This document outlines the procedure for containerizing the application using Docker for both local development (Windows) and server deployment (Linux).
I have a streamlit app already running at port 8501 do this setup uses port 8502.

## ❖ Windows (Local Development)

Follow these steps to set up and run the Docker container on your local Windows machine.

1.  **Create `Dockerfile`**
    *   Copy the `Dockerfile` from a previous project as a template.
    *   Verify the `python` version specified in the `Dockerfile` matches the project's requirements.
    *   Ensure the file correctly exposes port `8501` for the Streamlit application.

2.  **Create `.dockerignore` File**
    *   Copy a standard `.dockerignore` file to prevent unnecessary files (like `.git`, `__pycache__`, virtual environments) from being copied into the image.

3.  **Create `docker-compose.yml` File**
    *   Copy the `docker-compose.yml` from a previous project.
    *   Modify the following keys for this specific project:
        *   `image`: fourfund-planner-app:latest
        *   `container_name`: fourfundplanner_app
    *   Update the port mapping to forward host port `8502` in this case, to the container's Streamlit port `8501`.

      ```yaml
        version: '3.12-slim'

        services:
        app:
            image: fourfund-planner-app:latest
            build: .
            container_name: fourfundplanner_app
            restart: unless-stopped
            ports:
            # Bind to localhost ONLY
            - "127.0.0.1:8502:8501"
            
            # RECOMMENDED: Add a healthcheck
            healthcheck:
            # Streamlit has a built-in health endpoint
            test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
            interval: 30s
            timeout: 10s
            retries: 3
      ```

4.  **Build and Run the Image**
    > **⚠️ Important:** Make sure **Docker Desktop is running** before executing any commands!

    *   Open a terminal in the project's root directory and run the following command to build the image and start the container in detached mode:
      ```sh
      docker compose up -d --build
      ```

5.  **Push to GitHub**
    *   Once the container is running successfully and the application is accessible, commit and push the new `Dockerfile`, `.dockerignore`, and `docker-compose.yml` files to the repository.

---

## ❖ Linux (Server Deployment)

Follow these steps to deploy the application on a Linux server.

1.  **Get the Project Code**
    *   **To clone the repository for the first time:**
      ```sh
      git clone https://github.com/jraitt/Four-Fund-Portfolio-Planner.git
      ```
    *   **To pull the latest updates if the repository already exists:**
      ```sh
      git pull
      ```

2.  **Add Subdomain at Your Registrar**
    *   At your domain registrar (e.g., Ionos), create a new **A Record** pointing your subdomain to the server's IP address.
      *   **Domain:** `compound-interests.com`
      *   **Subdomain:** `fourfundplanner`
      *   **Result:** `fourfundplanner.compound-interests.com`

3.  **Configure Nginx Reverse Proxy**
    *   **Create a new Nginx configuration file** for the site:
        ```sh
        sudo nano /etc/nginx/sites-available/fourfundplanner.conf
        ```
    *   **Paste the following server block** into the file. This configures Nginx to forward requests for your subdomain to the Docker container (running on port `8502`).
        ```nginx
            server {
            listen 80;
            server_name fourfundplanner.compound-interests.com;

            location / {
                proxy_pass http://127.0.0.1:8502;

                # WebSocket headers are required for Streamlit
                proxy_http_version 1.1;
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection "upgrade";

                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
                proxy_read_timeout 90;
            }
            }
        ```

4.  **Enable Site and Add SSL Certificate**
    *   **Enable the site** by creating a symbolic link to the `sites-enabled` directory:
        ```sh
        sudo ln -s /etc/nginx/sites-available/fourfundplanner.conf /etc/nginx/sites-enabled/
        ```
    *   **Test the Nginx configuration** for syntax errors:
        ```sh
        sudo nginx -t
        ```
    *   **If the test is successful, reload Nginx** to apply the changes:
        ```sh
        sudo systemctl reload nginx
        ```
    *   **Run Certbot** to automatically obtain and install a free SSL certificate from Let's Encrypt.
        > **Note:** This command will modify your Nginx configuration file (`fourfundplanner.conf`) to handle HTTPS and redirection.
        ```sh
        sudo certbot --nginx -d fourfundplanner.compound-interests.com
        ```

5.  **Build and Start Docker Container**
    *   Navigate to the project directory and execute the final command:
        ```sh
        docker compose up -d --build
        ```
    *   This will build the image from the latest code and start the container in detached mode. The application will now be live and accessible at `https://fourfundplanner.compound-interests.com`.