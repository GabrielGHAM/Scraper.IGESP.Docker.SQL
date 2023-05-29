from modulos.scraping import Scraper
from modulos.logs import create_log_file

if __name__ == '__main__':
    log_file, logger_instance = create_log_file()
    scraper = Scraper(logger_instance)
    scraper.run_scraping()
