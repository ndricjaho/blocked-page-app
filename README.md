# Pi-hole Custom Blocked Page with Reason Display

[![GitHub release](https://img.shields.io/github/v/release/NdricJaho/Blocked-Page-App?sort=semver)](https://github.com/ndricjaho/blocked-page-app/releases/latest)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

This project provides a simple, customizable blocked page for Pi-hole, displaying the reason why a domain is blocked, fetched directly from the Pi-hole v6 API.  Instead of a generic "This site is blocked," users will see details about the blocking lists or custom rules causing the block.

**Key Features:**

*   **Displays Pi-hole Block Reasons:**  Shows detailed reasons for domain blocking using the Pi-hole v6 REST API.
*   **Customizable Blocked Page:**  Uses a simple HTML template (`templates/index.html`) that you can easily modify to match your style.
*   **Dockerized Application:**  Easily deployable using Docker and Docker Compose.
*   **Efficient Session-Based API:**  Uses the Pi-hole v6 REST API session authentication for efficient and secure communication.
*   **Clean Logging:**  Provides focused logs showing only blocked domain requests and source IPs.

## Getting Started

**Prerequisites:**

*   **Pi-hole v6 or later** is installed and configured on your network.
*   **HTTPS (recommended)** is enabled for your Pi-hole web interface (for enhanced security, especially when using passwords over the network).
*   **Docker** and **Docker Compose** are installed on the machine where you will run the blocked page application.

**Installation and Running:**

**Option 1: Using Docker Compose (Recommended)**

1.  **Clone the GitHub repository:**
    ```bash
    git clone https://github.com/ndricjaho/blocked-page-app
    cd blocked-page-app

2.  **Create a `docker-compose.yml` file (if not already present).** Example `docker-compose.yml` (adjust as needed):

    ```yaml
    version: "3.9"
    services:
      blocked-page:
        image: ghcr.io/ndricjaho/blocked-page-app:latest # Or build locally - see Option 2
        ports:
          - "80:5000" # Access blocked page on port 80 of your host
        environment:
          PIHOLE_API_URL: "[https://pihole.server.lan](https://pihole.server.lan)"  # **Replace with your Pi-hole API URL (HTTPS recommended)**
          PIHOLE_PASSWORD: "<your_pihole_web_interface_password>" # **Replace with your Pi-hole web interface password**
    ```

3.  **Run Docker Compose:**
    In the same directory as your `docker-compose.yml` file, run:
    ```bash
    docker-compose up -d
    ```
    This will download (or build) the image and start the blocked page application in the background.

**Option 2: Building Docker Image Locally (if you prefer)**

1.  **Follow steps 1 and 2 from Option 1 (clone repo, create/adjust `docker-compose.yml`).**

2.  **Build the Docker image locally:**
    In the project directory (where `Dockerfile` is located), run:
    ```bash
    docker build -t blocked-page-image . # Tag the image as 'blocked-page-image'
    ```

3.  **Update `docker-compose.yml` (if needed):**
    If you built locally, make sure your `docker-compose.yml` `image` line is set to `image: blocked-page-image:latest` (or the tag you used in `docker build -t`).

4.  **Run Docker Compose:**
    ```bash
    docker-compose up -d
    ```

**Accessing the Blocked Page:**

Once the Docker container is running, access a domain that is blocked by your Pi-hole in your web browser. Instead of the default Pi-hole blocked page, you should now see your custom blocked page, displaying the reason for the block (if available from the Pi-hole API).

**Example: Redirecting to the Blocked Page**

In order for the redirect to work, in PiHole v6+, go to Settings -> System, make sure you toggle to Expert instead of Basic on the top right corner, then go a new item will appear under settings: All settings -> set "dns.blocking.mode" to "IP" and "dns.reply.blocking.IPv4" to the host IP you access pihole from.

You can also use ngix or similar if you want to reverse proxy and/ or add valid SSL

## Configuration

The application is configured using environment variables set in your `docker-compose.yml` file:

*   **`PIHOLE_API_URL`**:  **(Required)** The base URL of your Pi-hole API endpoint.  **Include `https://` or `http://` at the beginning.**  Example: `https://pihole.example.com` or `http://192.168.1.10`.  Do *not* include `/api` or specific API paths.
*   **`PIHOLE_PASSWORD`**: **(Required)** Your Pi-hole web interface password. This is used to authenticate with the Pi-hole v6 API.

**Security Considerations:**

*   **HTTPS for `PIHOLE_API_URL` (Highly Recommended):**  It is **strongly recommended** to use `https://` for `PIHOLE_API_URL`, especially since you are passing your Pi-hole web interface password as an environment variable. HTTPS encrypts the communication between your blocked page app and your Pi-hole server, protecting your password in transit, even within your local network. Configure HTTPS for your Pi-hole web interface if you haven't already.
*   **`verify=False` in Code:** The application code currently uses `verify=False` in `requests` calls to bypass SSL certificate verification. **This is for local testing purposes only in a trusted network environment and to easily handle self-signed certificates.** **Do NOT use `verify=False` in production or public deployments where security is critical.** In a production setting with HTTPS, you should either use a valid certificate for your Pi-hole or configure proper certificate handling in your application.
*   **Password Security:** Storing passwords in environment variables is generally better than hardcoding, but still requires caution. Protect access to your `docker-compose.yml` file and the environment where your Docker container runs.

## Customization

*   **Blocked Page HTML:** You can customize the look and feel of the blocked page by modifying the `templates/index.html` file.  Feel free to change the HTML structure, CSS styles (in `static/style.css`), and content to match your preferences.

## Contributing (Optional)

[If you want to encourage contributions, add a section like this:]

Contributions are welcome!  If you have ideas for improvements, bug fixes, or new features, please feel free to submit a pull request or open an issue on GitHub.

## License

This project is licensed under the [MIT License](LICENSE) - see the [LICENSE](LICENSE) file for details.

## Author/Maintainer

Ndricim Jaho/ndricjaho