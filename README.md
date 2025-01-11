# Resource Monitoring and Alerting System

A system for monitoring CPU, memory, disk, and network usage on a server. It sends email alerts when usage exceeds predefined thresholds. The system encrypts and decrypts sensitive credentials securely, and logs the usage data to a JSON file.

## Features

- Monitors **CPU**, **Memory**, **Disk**, and **Network** usage.
- Sends email alerts if resource usage exceeds set thresholds.
- Stores collected resource data in a JSON file.
- Securely encrypts and decrypts email credentials.

---

## Requirements

- Python 3.x
- Required Python libraries:
  - `psutil`
  - `cryptography`
- A Gmail account for sending email alerts.

This system has been designed for Linux and tested on CentOS 9.

---

## Modules

- **Main module**: Contains the logic for monitoring resources (CPU, memory, disk, and network usage), sending email alerts, and logging data to a JSON file.
- **encrypt_credentials.py**: Handles encryption and decryption of sensitive credentials (like Gmail login information). It encrypts email credentials to keep them secure and decrypts them when needed for sending alerts.
  
---

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/resource-monitoring.git
    cd resource-monitoring
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Prepare the credentials file (`credentials.txt`):
    - Create a `credentials.txt` file with the following format:
        ```
        FROM_EMAIL="your.email@gmail.com"
        FROM_EMAIL_TOKEN="your_email_app_token" 
        TO_EMAIL="recipient.email@example.com"
        ```
**FROM_EMAIL_TOKEN** has to be in format **XXXX XXXX XXXX XXXX**, otherwise script won't be able to encrypt and decrypt data.

4. **Run the script once** to generate the encryption key and encrypt the credentials:
    ```bash
    python encrypt_credentials.py
    ```
    This will generate a `secret.key` file and an `encrypted_credentials.txt` file with your email credentials securely stored.

---

## How to get Gmail token for SMTP configuration:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a project (or use an existing one).
3. Enable the **Gmail API** under "APIs & Services" > "Library".
4. Go to "Credentials" > "Create Credentials" > "OAuth 2.0 Client IDs".
5. Download the credentials JSON file and get the **Client ID** and **Client Secret**.
6. Follow [this guide](https://developers.google.com/gmail/api/quickstart/python) to generate an App Password (token) for Gmail.

---

## Running the script

### 1. Normal execution through Python:
   Simply run the main script:
   ```bash
   python resource_monitor.py
   ```
### 2. Running as a service on Linux (CentOS 9)

You can run the monitoring script as a background service using `systemd`. Follow these steps:

1. Create a new systemd service file:
    ```bash
    sudo nano /etc/systemd/system/resource-monitor.service
    ```

2. Paste the following configuration:
    ```makefile
    [Unit]
    Description=Resource Monitoring and Alerting Service
    After=network.target

    [Service]
    ExecStart=/usr/bin/python3 /path/to/your/repository/resource_monitor.py
    WorkingDirectory=/path/to/your/repository
    Restart=always
    User=your-username
    Group=your-group

    [Install]
    WantedBy=multi-user.target
    ```

3. Enable and start the service:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable resource-monitor.service
    sudo systemctl start resource-monitor.service
    ```

4. Check the status of the service:
    ```bash
    sudo systemctl status resource-monitor.service
    ```

### 3. Running in a Detached Screen Session

To run the script in a detached screen session, you can use the following steps:

1. Start a new or reattach to an existing screen session named `resource_monitor`:

   ```bash
   screen -DRS resource_monitor
   ```
2. Inside the screen session, run the script
    ```python
    python3 /opt/resource-monitoring/resource_monitor.py
    ```

3. Detach from the screen session (to leave it running in the background)
    ```bash
    Press Ctrl+A, then press D
    ```

4. To reattach to the session later, use
    ```
    screen -r resource_monitor
    ```
   
---

## Configurable Parameters

### Thresholds:
- **`CPU_THRESHOLD`**: The CPU usage percentage above which an alert will be sent (default: 80%).
- **`MEMORY_THRESHOLD`**: The memory usage percentage above which an alert will be sent (default: 50%).
- **`DISK_THRESHOLD`**: The disk usage percentage above which an alert will be sent (default: 80%).
- **`EMAIL_COOLDOWN`**: The cooldown time (in seconds) between sending alerts (default: 30 seconds).

### Email Configuration:
- **`FROM_EMAIL`**: The email address used to send alerts.
- **`FROM_EMAIL_TOKEN`**: The application token or app password for the Gmail account.
- **`TO_EMAIL`**: The email address to receive alerts.

### File structure:

```
resource-monitoring/
├── resource_monitor.py          # Main script for resource monitoring and alerting
├── encrypt_credentials.py       # Script for encrypting and decrypting email credentials
├── requirements.txt             # Required Python libraries
├── credentials.txt              # Plaintext credentials file (used only for initial encryption)
├── encrypted_credentials.txt    # Encrypted credentials file
├── secret.key                   # Encryption key file
└── resource_usage.json          # JSON file where resource usage data is logged
```

### License
This project is licensed under the MIT License - see the LICENSE file for details.

### Acknowledgements
Thanks to authors of **psutil** for providing the system resource monitoring library.
Thanks to authors of **cryptography** for providing secure encryption utilities.

   