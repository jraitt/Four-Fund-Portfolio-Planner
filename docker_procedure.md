Of course! Here is the provided text formatted into a `docker_procedure.md` file with rich markdown features, including headings, lists, code blocks with syntax highlighting, and emphasis.

---

# Docker Development & Deployment Procedure

This document outlines the procedure for containerizing the application using Docker for both local development (Windows) and server deployment (Linux).

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
        *   `image`: Change to a unique image name.
        *   `container_name`: Change to a unique container name.
    *   Update the port mapping to forward host port `8502` to the container's Streamlit port `8501`.

      ```yaml
      services:
        app:
          # ... other service configurations
          ports:
            # Map host port 8502 to container port 8501 (for the Streamlit app)
            - "8502:8501"
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

2.  **Setup Nginx Reverse Proxy**
    *   Configure Nginx to route traffic from a subdomain to the running Streamlit container.
    *   Refer to the specific server block configuration details in the `streamlit_subdomain_fourfundplanner.txt` file.

3.  **Build and Start Docker Container**
    *   Navigate to the project directory and execute the command:
      ```sh
      docker compose up -d --build
      ```
    *   This command will build the image based on the latest code and start the container, making the application live.