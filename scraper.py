import json
from time import time, gmtime, strftime
import logging
import logging.config

from healthtools.scrapers import *

from healthtools.config import LOGGING


def setup_logging(default_level=logging.INFO):
    """
    Setup logging configuration
    """
    try:
        logging.config.dictConfig(LOGGING)
    except Exception as ex:
        logging.basicConfig(level=default_level)

    
if __name__ == "__main__":
    
    setup_logging()
    time_start = time()

    # Initialize the Scrapers
    doctors_scraper = DoctorsScraper()
    foreign_doctors_scraper = ForeignDoctorsScraper()
    clinical_officers_scraper = ClinicalOfficersScraper()
    healthfacilities_scraper = HealthFacilitiesScraper()

    nhif_inpatient_scraper = NhifInpatientScraper()
    nhif_outpatient_scraper = NhifOutpatientScraper()
    nhif_outpatient_cs_scraper = NhifOutpatientCsScraper()

    # Run the scrapers

    '''
    Doctors Scraper
    ---------------
    Doctors are a combination of local and foreign doctors. If the local
    doctors' scraper fails, we shouldn't scrape the foreign doctors.

    FIX: For now we are storing the doctors and foreign doctors in separate
    doc types. We shall combine results in API result.
    '''
    doctors_result = doctors_scraper.run_scraper()
    foreign_docs_result = foreign_doctors_scraper.run_scraper()

    '''
    Clinical Officers Scraper
    -------------------------
    Scrapes the clinical officers website.
    '''
    clinical_officers_result = clinical_officers_scraper.run_scraper()

    '''
    Health Facilities Scraper
    -------------------------
    Scrapes the government's Kenya Health Facilities Master List.
    '''
    healthfacilities_result = healthfacilities_scraper.run_scraper()

    '''
    NHIF Scraper
    ------------
    Scrapes the NHIF website for accredited hospital / facitilities.
    '''
    nhif_inpatient_result = nhif_inpatient_scraper.run_scraper()
    nhif_outpatient_result = nhif_outpatient_scraper.run_scraper()
    nhif_outpatient_cs_result = nhif_outpatient_cs_scraper.run_scraper()


    '''
    STATS
    -----
    Log time taken and other stats
    '''
    # TODO: Move this to its own module
    time_total = time() - time_start
    m, s = divmod(time_total, 60)
    h, m = divmod(m, 60)
    time_total_formatted = "%dhr:%02dmin:%02dsec" % (
        h, m, s) if time_total > 60 else '{} seconds'.format(time_total)

    scraping_statistics = {
        'Total time Scraping took': time_total_formatted,
        'Last successfull Scrape was': strftime("%Y-%m-%d %H:%M:%S", gmtime()),
        'doctors_scraper': doctors_scraper.stat_log,
        'foreign_doctors_scraper': foreign_doctors_scraper.stat_log,
        'clinical_officers_scraper': clinical_officers_scraper.stat_log,
        'healthfacilities_scraper': healthfacilities_scraper.stat_log,
        'nhif_inpatient_scraper': nhif_inpatient_scraper.stat_log,
        'nhif_outpatient_cs_scraper': nhif_outpatient_cs_scraper.stat_log,
        'nhif_outpatient_scraper': nhif_outpatient_scraper.stat_log,
    }

    # initialize a scraper to index scraper statistics
    scraper_stats = Scraper()
    scraper_stats.data_key = "stats.json"
    scraper_stats.data_archive_key = "stats/stats-{}.json"
    scraper_stats.archive_data(json.dumps(scraping_statistics))
