import psutil
import time
import json
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

CPU_THRESHOLD = 80
MEMORY_THRESHOLD = 50
DISK_THRESHOLD = 80

FROM_EMAIL = "ENTER EMAIL HERE"
FROM_EMAIL_TOKEN = "ENTER TOKEN HERE"
TO_EMAIL = "ENTER EMAIL HERE"

# Time cooldown in seconds between sending alerts
EMAIL_COOLDOWN = 30  # 1 minute cooldown

# Initialize the last email sent time
last_email_time = 0
last_email_sent_cpu = 0
last_email_sent_memory = 0
last_email_sent_disk = 0


# Functions to get hardware usage
def get_cpu_usage():
    return psutil.cpu_percent(interval=1)  # Return percentage usage of CPU


def get_memory_usage():
    memory = psutil.virtual_memory()
    return memory.percent  # Return percentage usage of RAM


def get_disk_usage():
    disk = psutil.disk_usage("/")
    return disk.percent  # Return percentage usage of Hard Drive


def get_network_usage():
    net = psutil.net_io_counters()
    return {"bytes_sent": net.bytes_sent, "bytes_recv": net.bytes_recv}


def send_email(subject, body, to_email):
    from_email = FROM_EMAIL
    from_password = FROM_EMAIL_TOKEN

    # SMTP config for email
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # Create email message
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        # Connect to SMTP and send message
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(from_email, from_password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()

        # Add timestamp to the email sent success message
        current_time = datetime.now().strftime("%H:%M:%S %d-%m-%Y")
        print(f"{current_time} Email sent successfully!")

    except Exception as e:
        print(f"Error sending email: {e}")


def send_alert(resource, threshold, last_email_time):
    global last_email_sent_cpu, last_email_sent_memory, last_email_sent_disk

    # Check if enough time has passed since the last email was sent
    current_time = time.time()

    subject = f"ALERT: {resource} usage exceeded threshold"
    body = f"ALERT: {resource} usage exceeded the threshold of {threshold}%. \nPlease take action!"

    current_time = time.time()

    if current_time - last_email_time >= EMAIL_COOLDOWN:
        send_email(subject, body, TO_EMAIL)

        # Update the last email sent time for the resource that triggered the alert
        if resource == "CPU":
            last_email_sent_cpu = current_time
        elif resource == "Memory":
            last_email_sent_memory = current_time
        elif resource == "Disk":
            last_email_sent_disk = current_time

        return current_time  # Return current time to update the last sent time

    return last_email_time  # Return the last email time if cooldown hasn't passed


def monitor_resources(interval, output_file):
    global last_email_sent_cpu, last_email_sent_memory, last_email_sent_disk

    while True:
        # Fetching data
        cpu = get_cpu_usage()
        memory = get_memory_usage()
        disk = get_disk_usage()
        network = get_network_usage()

        # Save all data in one dictionary
        resource_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "cpu_usage": cpu,
            "memory_usage": memory,
            "disk_usage": disk,
            "network_usage": network,
        }

        # Check if any threshold was exceeded
        if cpu > CPU_THRESHOLD and (time.time() - last_email_sent_cpu >= EMAIL_COOLDOWN):
            last_email_sent_cpu = send_alert("CPU", CPU_THRESHOLD, last_email_sent_cpu)

        # Check if any threshold was exceeded for Memory
        if memory > MEMORY_THRESHOLD and (time.time() - last_email_sent_memory >= EMAIL_COOLDOWN):
            last_email_sent_memory = send_alert("Memory", MEMORY_THRESHOLD, last_email_sent_memory)

        # Check if any threshold was exceeded for Disk
        if disk > DISK_THRESHOLD and (time.time() - last_email_sent_disk >= EMAIL_COOLDOWN):
            last_email_sent_disk = send_alert("Disk", DISK_THRESHOLD, last_email_sent_disk)

        # Check if file exists, save data to file
        if not os.path.exists(output_file):
            with open(output_file, "w") as f:
                json.dump([resource_data], f, indent=4)
        else:
            with open(output_file, "r+") as f:
                data = json.load(f)
                data.append(resource_data)
                f.seek(0)
                json.dump(data, f, indent=4)

        print(f"Data collected at {resource_data['timestamp']}: CPU {cpu}%, RAM {memory}%, Disk {disk}%")

        # Wait for another cycle
        time.sleep(interval)


if __name__ == "__main__":
    interval = 10  # Time interval between fetching data (in seconds)
    output_file = "resource_usage.json"  # File, to which data is saved.

    monitor_resources(interval, output_file)
