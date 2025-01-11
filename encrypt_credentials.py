import os
from cryptography.fernet import Fernet


def generate_key(key_filename="secret.key"):
    key = Fernet.generate_key()
    with open(key_filename, "wb") as key_file:
        key_file.write(key)
    return key


def load_key(key_filename="secret.key"):
    with open(key_filename, "rb") as key_file:
        return key_file.read()


def encrypt_data(data, key):
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(data.encode())
    return encrypted_data


# Function to save encrypted data to file
def encrypt_file(input_file="credentials.txt", output_file="encrypted_credentials.txt"):
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"{input_file} does not exist. Create the file with your credentials.")

    key = load_key()

    # Load data from file
    with open(input_file, "r") as file:
        lines = [line.strip() for line in file.readlines()]

    if len(lines) != 3:
        raise ValueError(f"{input_file} must contain exactly 3 lines: FROM_EMAIL, FROM_EMAIL_TOKEN, TO_EMAIL")

    # Parse the data
    from_email = lines[0].split("=")[1].replace('"', "").strip()  # Removing extra spaces and quotes
    from_email_token = lines[1].split("=")[1].replace('"', "").strip()
    to_email = lines[2].split("=")[1].replace('"', "").strip()

    # Encrypt data
    encrypted_from_email = encrypt_data(from_email, key)
    encrypted_from_email_token = encrypt_data(from_email_token, key)
    encrypted_to_email = encrypt_data(to_email, key)

    # Save encrypted data to file (without the `b'` and extra quotes)
    with open(output_file, "wb") as file:
        file.write(b"ENCRYPTED\n")  # Dodaj nagłówek, aby wskazać, że plik jest zaszyfrowany
        file.write(encrypted_from_email + b"\n")
        file.write(encrypted_from_email_token + b"\n")
        file.write(encrypted_to_email + b"\n")


def decrypt_data(encrypted_data, key):
    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(encrypted_data).decode("utf-8")
    return decrypted_data


def decrypt_and_load(encrypted_file="encrypted_credentials.txt", key_filename="secret.key"):
    try:
        key = load_key(key_filename)
    except Exception as e:
        print(f"Error loading key: {e}")
        return None, None, None

    # Check if encrypted file exist
    if not os.path.exists(encrypted_file):
        raise FileNotFoundError(f"{encrypted_file} not found!")

    # Load encrypted data from file
    try:
        with open(encrypted_file, "rb") as file:
            header = file.readline().strip()  # Read the HEADER
            if header != b"ENCRYPTED":
                raise ValueError(f"The file {encrypted_file} does not contain encrypted data")

            # Read encrypted lines
            encrypted_from_email = file.readline().strip()
            encrypted_from_email_token = file.readline().strip()
            encrypted_to_email = file.readline().strip()

    except:
        print(f"Error reading file {encrypted_file}: {e}")
        return None, None, None

    try:
        from_email = decrypt_data(encrypted_from_email, key)
        from_email_token = decrypt_data(encrypted_from_email_token, key)
        to_email = decrypt_data(encrypted_to_email, key)

    except Exception as e:
        print(f"Error during decryption: {e}")
        return None, None, None

    return from_email, from_email_token, to_email
