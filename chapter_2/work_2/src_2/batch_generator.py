import random
import csv
import logging
import uuid
import polars as pl

from faker import Faker
from datetime import date, datetime, timedelta

# Configure logging.
logging.basicConfig(
    level=logging.INFO,                    
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler()]
)

def create_data(locale: str) -> Faker:
    """
    Creates a Faker instance for generating localized fake data.
    Args:
        locale (str): The locale code for the desired fake data language/region.
    Returns:
        Faker: An instance of the Faker class configured with the specified locale.
    """
    # Log the action.
    logging.info(f"Created synthetic data for {locale.split('_')[-1]} country code.")
    return Faker(locale)

def generate_record(fake: Faker) -> list:
    """
    Generates a single fake user record.
    Args:
        fake (Faker): A Faker instance for generating random data.
    Returns:
        list: A list containing various fake user details such as name, username, email, etc.
    """
    # Generate random personal data.
    person_name = fake.name()
    user_name = person_name.replace(" ", "").lower()  # Create a lowercase username without spaces.
    email = f"{user_name}@{fake.free_email_domain()}"  # Combine the username with a random email domain.
    personal_number = fake.ssn()  # Generate a random social security number.
    birth_date = fake.date_of_birth()  # Generate a random birth date.
    address = fake.address().replace("\n", ", ")  # Replace newlines in the address with commas.
    phone_number = fake.phone_number()  # Generate a random phone number.
    mac_address = fake.mac_address()  # Generate a random MAC address.
    ip_address = fake.ipv4()  # Generate a random IPv4 address.
    iban = fake.iban()  # Generate a random IBAN.
    accessed_at = fake.date_time_between("-1y")  # Generate a random date within the last year.
    session_duration = random.randint(0, 36_000)  # Random session duration in seconds (up to 10 hours).
    download_speed = random.randint(0, 1_000)  # Random download speed in Mbps.
    upload_speed = random.randint(0, 800)  # Random upload speed in Mbps.
    consumed_traffic = random.randint(0, 2_000_000)  # Random consumed traffic in kB.

    # Return all the generated data as a list.
    return [
        person_name, user_name, email, personal_number, birth_date,
        address, phone_number, mac_address, ip_address, iban, accessed_at,
        session_duration, download_speed, upload_speed, consumed_traffic
    ]

def write_to_csv(file_path: str, rows: int) -> None:
    """
    Generates multiple fake user records and writes them to a CSV file.
    Args:
        file_path (str): The path where the CSV file will be saved.
        rows (int): The number of fake user records to generate.
    """
    # Create a Faker instance with Romanian data.
    fake = create_data("ro_RO")
    
    # Define the CSV headers.
    headers = [
        "person_name", "user_name", "email", "personal_number", "birth_date", "address",
        "phone", "mac_address", "ip_address", "iban", "accessed_at",
        "session_duration", "download_speed", "upload_speed", "consumed_traffic"
    ]

    # Open the CSV file for writing.
    with open(file_path, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        
        # Generate and write each record to the CSV.
        for _ in range(rows):
            writer.writerow(generate_record(fake))
    # Log the action.
    logging.info(f"Written {rows} records to the CSV file.")

def add_id(file_name) -> None:
    """
    Adds a unique UUID to each row in a CSV file.
    Args:
        file_name (str): The path to the CSV file to be processed.
    """
    # Load the CSV into a Polars DataFrame.
    df = pl.read_csv(file_name)
    # Generate a list of UUIDs (one for each row).
    uuid_list = [str(uuid.uuid4()) for _ in range(df.height)]
    # Add a new column with unique IDs.
    df = df.with_columns(pl.Series("unique_id", uuid_list))
    # Save the updated DataFrame back to a CSV.
    df.write_csv(file_name)
    # Log the action.
    logging.info("Added UUID to the dataset.")

def update_datetime(file_name: str, run: str) -> None:
    """
    Update the 'accessed_at' column in a CSV file with the appropriate timestamp.
    Args:
        file_name (str): The path to the CSV file to be updated.
        run (str): Specifies the timestamp to be used.
    """
    if run == "next":
        # Get the current time without milliseconds and calculate yesterday's time.
        current_time = datetime.now().replace(microsecond=0)
        yesterday_time = str(current_time - timedelta(days=1))
        # Load the CSV into a Polars DataFrame.
        df = pl.read_csv(file_name)
        # Replace all values in the 'accessed_at' column with yesterday's timestamp.
        df = df.with_columns(pl.lit(yesterday_time).alias("accessed_at"))
        # Save the updated DataFrame back to a CSV file.
        df.write_csv(file_name)
        # Log the action.
        logging.info("Updated accessed timestamp.")

if __name__ == "__main__":

    # Logging starting of the process.
    logging.info(f"Started batch processing for {date.today()}.")

    # Define the output file name with today's date.
    # ¡Importante! Ajusta esta ruta según tu estructura real.
    # Si 'data_2' está en 'work_2' y 'src_2' está en 'work_2', la ruta relativa desde 'src_2' debe ser '../data_2/'
    output_file = f"../data_2/batch_{date.today()}.csv" # <--- ¡Cambiado aquí!

    # Define number of records: first run - 10_372; next runs random number.
    # Nota: La fecha "2024-09-14" es la fecha de referencia para la "primera ejecución".
    # Cuando lo ejecutes por primera vez, si la fecha actual no es 2024-09-14,
    # ejecutará la lógica de "next run". Esto es para simular el escenario.
    if str(date.today()) == "2025-06-20": # Esta fecha es un marcador para la primera carga
        records = random.randint(100_372, 100_372) # Siempre 100,372 para la primera carga
        run_type = "first"
    else:
        records = random.randint(0, 1_101) # Entre 0 y 1,100 (aproximadamente 1,000 + margen) para cargas siguientes
        run_type = "next"
    
    # Generate and write records to the CSV.
    # Aquí se genera el archivo CSV con los datos.
    write_to_csv(output_file, records)

    # Add UUID to dataset.
    # Aquí se añade la columna 'unique_id' con UUIDs.
    add_id(output_file)

    # Update the timestamp.
    # Si es una "next run", la columna 'accessed_at' se actualizará a la fecha de ayer.
    update_datetime(output_file, run_type)

    # Logging ending of the process.
    logging.info(f"Finished batch processing {date.today()}.")
