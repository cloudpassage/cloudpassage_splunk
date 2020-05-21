import logging
import os


def log(log_file_name, level, message):
    log_file_name = os.path.join(os.environ["SPLUNK_HOME"], "var", "log", "splunk", log_file_name)
    if level.__eq__("INFO"):
      logging.basicConfig(filename=log_file_name, filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
      logging.info(message)
    if level.__eq__("WARNING"):
      logging.basicConfig(filename=log_file_name, filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.WARNING)
      logging.warning(message)
    if level.__eq__("ERROR"):
      logging.basicConfig(filename=log_file_name, filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.ERROR)
      logging.error(message)