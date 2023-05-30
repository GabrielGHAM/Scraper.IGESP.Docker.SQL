import logging
import sys  # Adicionado import do módulo sys
from dotenv import load_dotenv
import os
from datetime import timezone, datetime, timedelta
import glob
from modulos.database import DatabaseManager
import signal

load_dotenv()
log_file_table_name = "TB_LOG"

dataLogger_table_name = os.getenv('TB_NAME') + "_Log"
create_columns_dataLogger = [
    "ID INT IDENTITY(1,1) PRIMARY KEY",
    "URL_ORIGEM VARCHAR(MAX)",
    "NM_ARQUIVO VARCHAR(MAX)",
    "QTD_DE_LINHAS VARCHAR(MAX)",
    "STATUS VARCHAR(MAX)",
    "TEMPO_BUSCA VARCHAR(MAX)",
    "TIMESTAMP VARCHAR(MAX)"
]
columns_dataLogger= [
    'URL_ORIGEM',
    'NM_ARQUIVO',
    'QTD_DE_LINHAS',
    'STATUS',
    'TEMPO_BUSCA',
    'TIMESTAMP'
]
create_columns_log_file = [
    "ID INT IDENTITY(1,1) PRIMARY KEY",
    "DS_LOG VARCHAR(MAX)",
    "TS_LOG VARCHAR(MAX)",
    "NM_FILE VARCHAR(MAX)"
]

class DataLogger:
    def __init__(self, href=None, filename=None, qtd_linhas=None, tempo_busca=None, status=None):
        self.href = href
        self.filename = filename
        self.qtd_linhas = qtd_linhas
        self.tempo_busca = tempo_busca
        self.status = status
        self.br_timezone = timezone(timedelta(hours=-3))

    def file_log_data(self):
        return {
            'URL_ORIGEM': self.href,
            'NM_ARQUIVO': self.filename,
            'QTD_DE_LINHAS': self.qtd_linhas,
            'STATUS': self.status,
            'TEMPO_BUSCA': self.tempo_busca,
            'TIMESTAMP': datetime.now(self.br_timezone).strftime("%Y-%m-%d %H:%M:%S")
        }


class DatabaseHandler(logging.StreamHandler):
    def __init__(self, log_filename):
        super().__init__()
        self.database_manager = DatabaseManager()
        self.log_filename = log_filename
        self.br_timezone = timezone(timedelta(hours=-3))
    def emit(self, record):
        if record:
            log_data = {
                'DS_LOG': record.msg,
                'TS_LOG': datetime.now(self.br_timezone).strftime("%Y-%m-%d %H:%M:%S"),
                'NM_FILE': os.path.basename(self.log_filename)
            }
            values = tuple(log_data.values())
            self.database_manager.create_table(log_file_table_name,create_columns_log_file)
            self.database_manager.insert_data(log_file_table_name, values, list(log_data.keys()))


def logger(log_file, level=logging.INFO):
    # Create logger
    logger = logging.getLogger(__name__)
    logger.setLevel(level)

    # Create file handler
    fh = logging.FileHandler(log_file)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    # Add file handler to logger
    logger.addHandler(fh)

    # Return logger without adding the DatabaseHandler here

    return logger


def create_log_file():
    # Create log directory if it does not exist
    log_dir = 'log'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Remove old log files
    old_logs = glob.glob(os.path.join(log_dir, '*.txt'))
    for old_log in old_logs:
        os.remove(old_log)

    # Get current timestamp for logging and create log file
    now = datetime.now()
    timestamp = now.strftime('%Y-%m-%d_%H-%M-%S')
    log_filename = os.path.join(log_dir, f'log_{timestamp}.txt')

     # Set up logger
    logger_instance = logger(log_filename)

    # Customize the log filename in the database handler
    db_handler = DatabaseHandler(log_filename)
    db_handler.setLevel(logging.INFO)
    logger_instance.addHandler(db_handler)

    # Define signal handler function to send logs before exiting
    def send_logs_on_exit(signal, frame):
        logger_instance.info("Sending logs to database before exiting...")
        db_handler.flush()
        db_handler.close()
        logger_instance.info("Logs sent to database. Exiting...")
        sys.exit(0)

    # Register the signal handler
    signal.signal(signal.SIGINT, send_logs_on_exit)
    signal.signal(signal.SIGTERM, send_logs_on_exit)

    return log_filename, logger_instance