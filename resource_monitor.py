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


# Functions to get hardware usage
def get_cpu_usage():
    return psutil.cpu_percent(interval=1)  # Return precentage usage of CPU


def get_memory_usage():
    memory = psutil.virtual_memory()
    return memory.percent  # Return precentage usage of RAM


def get_disk_usage():
    disk = psutil.disk_usage("/")
    return disk.percent  # Return precentage usage of Hard Drive


def get_network_usage():
    net = psutil.net_io_counters()
    return {"bytes_sent": net.bytes_sent, "bytes_recv": net.bytes_recv}


def send_email(subject, body, to_email):
    from_email = FROM_EMAIL
    from_password = FROM_EMAIL_TOKEN

    # SMTP config for  Gmail

    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # Create email massage
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        # Connect to SMTP and send message
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Używamy szyfrowania TLS
        server.login(from_email, from_password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")

    except Exception as e:
        print(f"Error sending email: {e}")


def send_alert(resource, threshold):
    subject = f"ALERT: {resource} usage exceeded threshold"
    body = f'"ALERT: {resource} usage exceeded the threshold of {threshold}%. \n Please take action!'

    # Call function to send email
    send_email(subject, body, TO_EMAIL)


def monitor_resources(interval, output_file):
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
        if cpu > CPU_THRESHOLD:
            send_alert("CPU", CPU_THRESHOLD)
        if memory > MEMORY_THRESHOLD:
            send_alert("Memory", MEMORY_THRESHOLD)
        if disk > DISK_THRESHOLD:
            send_alert("Disk", DISK_THRESHOLD)

        # Check if fiile exists, save data to file
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
