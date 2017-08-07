import json
import os
import unittest
from healthtools.scrapers.base_scraper import Scraper
from healthtools.scrapers.doctors import DoctorsScraper
from healthtools.scrapers.foreign_doctors import ForeignDoctorsScraper
from healthtools.scrapers.clinical_officers import ClinicalOfficersScraper
from healthtools.scrapers.health_facilities import HealthFacilitiesScraper
from healthtools.scrapers.nhif_inpatient import NhifInpatientScraper
from healthtools.scrapers.nhif_outpatient import NhifOutpatientScraper
from healthtools.scrapers.nhif_outpatient_cs import NhifOutpatientCsScraper
from healthtools.config import SLACK, AWS, ES


class TestScrapers(unittest.TestCase):

    def setUp(self):
        self.TEST_DATA = os.getcwd() + "/healthtools/tests/"
        self.base_scraper = Scraper()
        self.doctors_scraper = DoctorsScraper()
        self.foreign_doctors_scraper = ForeignDoctorsScraper()
        self.clinical_officers_scraper = ClinicalOfficersScraper()
        self.health_facilities_scraper = HealthFacilitiesScraper()
        self.nhif_inpatient_scraper = NhifInpatientScraper()
        self.nhif_outpatient_scraper = NhifOutpatientScraper()
        self.nhif_outpatient_cs_scraper = NhifOutpatientCsScraper()

    def test_it_gets_the_total_number_of_pages(self):
        self.doctors_scraper.set_site_pages_no()
        self.assertIsNotNone(self.doctors_scraper.site_pages_no)

    def test_it_scrapes_doctors_page(self):
        entries = self.doctors_scraper.scrape_page(
            "http://medicalboard.co.ke/online-services/retention/?currpage=1", 5)
        self.assertTrue(len(entries[1]) == 60)

    def test_it_scrapes_foreign_doctors_page(self):
        entries = self.foreign_doctors_scraper.scrape_page(
            "http://medicalboard.co.ke/online-services/foreign-doctors-license-register/?currpage=1", 5)
        self.assertTrue(len(entries[1]) == 60)

    def test_it_scrapes_clinical_officers_page(self):
        entries = self.clinical_officers_scraper.scrape_page(
            "http://clinicalofficerscouncil.org/online-services/retention/?currpage=1", 5)
        self.assertTrue(len(entries[1]) == 60)

    def test_it_scrapes_nhif_inpatient_page(self):
        entries = self.nhif_inpatient_scraper.scrape_page(1, 5)
        self.assertTrue(len(entries) > 1)

    def test_it_scrapes_nhif_outpatient_page(self):
        entries = self.nhif_outpatient_scraper.scrape_page(1, 5)
        self.assertTrue(len(entries) > 1)

    def test_it_scrapes_nhif_outpatient_cs_page(self):
        entries = self.nhif_outpatient_cs_scraper.scrape_page(1, 5)
        self.assertTrue(len(entries) > 1)

    def test_doctors_scraper_uploads_to_elasticsearch(self):
        self.doctors_scraper.es_index = "healthtools-test"
        with open(self.TEST_DATA + "dummy_files/doctors.json", "r") as my_file:
            data = my_file.read()
            response = self.doctors_scraper.elasticsearch_index(json.loads(data))
            self.assertEqual(response["items"][0]["index"]["_shards"]["successful"], 1)

    def test_foreign_doctors_scraper_uploads_to_elasticsearch(self):
        self.foreign_doctors_scraper.es_index = "healthtools-test"
        with open(self.TEST_DATA + "dummy_files/foreign_doctors.json", "r") as my_file:
            data = my_file.read()
            response = self.foreign_doctors_scraper.elasticsearch_index(json.loads(data))
            self.assertEqual(response["items"][0]["index"]["_shards"]["successful"], 1)

    def test_clinical_officers_scraper_uploads_to_elasticsearch(self):
        self.clinical_officers_scraper.es_index = "healthtools-test"
        with open(self.TEST_DATA + "dummy_files/clinical_officers.json", "r") as my_file:
            data = my_file.read()
            response = self.clinical_officers_scraper.elasticsearch_index(json.loads(data))
            self.assertEqual(response["items"][0]["index"]["_shards"]["successful"], 1)

    def test_health_facilities_scraper_uploads_to_elasticsearch(self):
        self.health_facilities_scraper.es_index = "healthtools-test"
        with open(self.TEST_DATA + "dummy_files/health_facilities.json", "r") as my_file:
            data = my_file.read()
            response = self.health_facilities_scraper.elasticsearch_index(json.loads(data))
            self.assertEqual(response["items"][0]["index"]["_shards"]["successful"], 1)

    def test_nhif_inpatient_scraper_uploads_to_elasticsearch(self):
        self.nhif_inpatient_scraper.es_index = "healthtools-test"
        with open(self.TEST_DATA + "dummy_files/nhif_inpatient.json", "r") as my_file:
            data = my_file.read()
            response = self.nhif_inpatient_scraper.elasticsearch_index(json.loads(data))
            self.assertEqual(response["items"][0]["index"]["_shards"]["successful"], 1)

    def test_nhif_outpatient_scraper_uploads_to_elasticsearch(self):
        self.nhif_outpatient_scraper.es_index = "healthtools-test"
        with open(self.TEST_DATA + "dummy_files/nhif_outpatient.json", "r") as my_file:
            data = my_file.read()
            response = self.nhif_outpatient_scraper.elasticsearch_index(json.loads(data))
            self.assertEqual(response["items"][0]["index"]["_shards"]["successful"], 1)

    def test_nhif_outpatient_cs_scraper_uploads_to_elasticsearch(self):
        self.nhif_outpatient_cs_scraper.es_index = "healthtools-test"
        with open(self.TEST_DATA + "dummy_files/nhif_outpatient_cs.json", "r") as my_file:
            data = my_file.read()
            response = self.nhif_outpatient_cs_scraper.elasticsearch_index(json.loads(data))
            self.assertEqual(response["items"][0]["index"]["_shards"]["successful"], 1)

    def test_doctors_scraper_archives_to_s3(self):
        self.doctors_scraper.data_key = "test/doctors.json"
        self.doctors_scraper.data_archive_key = "test/" + self.doctors_scraper.data_archive_key
        with open(self.TEST_DATA + "dummy_files/doctors.json", "r") as my_file:
            data = my_file.read()
            self.doctors_scraper.archive_data(data)
        uploaded_data = self.doctors_scraper.s3.get_object(
            Bucket=AWS["s3_bucket"],
            Key=self.doctors_scraper.data_key
            )["Body"].read() if AWS["s3_bucket"] else json.load(open(self.doctors_scraper.data_key))
        self.assertEqual(len(json.loads(uploaded_data)), len(json.loads(data)))

    def test_foreign_doctors_scraper_archives_to_s3(self):
        self.foreign_doctors_scraper.data_key = "test/foreign_doctors.json"
        self.foreign_doctors_scraper.data_archive_key = "test/" + self.foreign_doctors_scraper.data_archive_key
        with open(self.TEST_DATA + "dummy_files/foreign_doctors.json", "r") as my_file:
            data = my_file.read()
            self.foreign_doctors_scraper.archive_data(data)
        uploaded_data = self.foreign_doctors_scraper.s3.get_object(
            Bucket=AWS["s3_bucket"],
            Key=self.foreign_doctors_scraper.data_key
            )["Body"].read() if AWS["s3_bucket"] else json.load(open(self.foreign_doctors_scraper.data_key))
        self.assertEqual(len(json.loads(uploaded_data)), len(json.loads(data)))

    def test_clinical_officers_scraper_archives_to_s3(self):
        self.clinical_officers_scraper.data_key = "test/clinical_officers.json"
        self.clinical_officers_scraper.data_archive_key = "test/" + self.clinical_officers_scraper.data_archive_key
        with open(self.TEST_DATA + "dummy_files/clinical_officers.json", "r") as my_file:
            data = my_file.read()
            self.clinical_officers_scraper.archive_data(data)
        uploaded_data = self.clinical_officers_scraper.s3.get_object(
            Bucket=AWS["s3_bucket"],
            Key=self.clinical_officers_scraper.data_key
            )["Body"].read() if AWS["s3_bucket"] else json.load(open(self.clinical_officers_scraper.data_key))
        self.assertEqual(len(json.loads(uploaded_data)), len(json.loads(data)))

    def test_health_facilities_scraper_gets_token(self):
        self.health_facilities_scraper.get_token()
        self.assertIsNotNone(self.health_facilities_scraper.access_token)

    def test_scrapper_prints_notification_on_error(self):
        response = self.base_scraper.print_error("Testing Error - Error - Tests - Error posted:Error occurred")
        if SLACK["url"]:
            self.assertEqual(response.status_code, 200)
        else:
            self.assertIsNone(response)

    def test_delete_doctors_documents_from_elasticsearch(self):
        self.doctors_scraper.es_index = "healthtools-test"
        self.doctors_scraper.elasticsearch_delete_docs()  # make sure doc_type is empty
        with open(self.TEST_DATA + "/dummy_files/doctors.json", "r") as my_file:
            data = my_file.read()
        upload_response = self.doctors_scraper.elasticsearch_index(json.loads(data))
        delete_response = self.doctors_scraper.elasticsearch_delete_docs()
        self.assertEqual(len(upload_response["items"]), delete_response["deleted"])

    def test_delete_foreign_doctors_documents_from_elasticsearch(self):
        self.foreign_doctors_scraper.es_index = "healthtools-test"
        with open(self.TEST_DATA + "/dummy_files/foreign_doctors.json", "r") as my_file:
            data = my_file.read()
        upload_response = self.foreign_doctors_scraper.elasticsearch_index(json.loads(data))
        delete_response = self.foreign_doctors_scraper.elasticsearch_delete_docs()
        self.assertEqual(len(upload_response["items"]), delete_response["deleted"])

    def test_delete_clinical_officers_documents_from_elasticsearch(self):
        self.clinical_officers_scraper.es_index = "healthtools-test"
        with open(self.TEST_DATA + "/dummy_files/clinical_officers.json", "r") as my_file:
            data = my_file.read()
        upload_response = self.clinical_officers_scraper.elasticsearch_index(json.loads(data))
        delete_response = self.clinical_officers_scraper.elasticsearch_delete_docs()
        self.assertEqual(len(upload_response["items"]), delete_response["deleted"])

    def test_delete_health_facilities_documents_from_elasticsearch(self):
        self.health_facilities_scraper.es_index = "healthtools-test"
        with open(self.TEST_DATA + "/dummy_files/health_facilities.json", "r") as my_file:
            data = my_file.read()
        upload_response = self.health_facilities_scraper.elasticsearch_index(json.loads(data))
        delete_response = self.health_facilities_scraper.elasticsearch_delete_docs()
        self.assertEqual(len(upload_response["items"]), delete_response["deleted"])

    def test_delete_nhif_inpatient_documents_from_elasticsearch(self):
        self.nhif_inpatient_scraper.es_index = "healthtools-test"
        with open(self.TEST_DATA + "/dummy_files/nhif_inpatient.json", "r") as my_file:
            data = my_file.read()
        upload_response = self.nhif_inpatient_scraper.elasticsearch_index(json.loads(data))
        delete_response = self.nhif_inpatient_scraper.elasticsearch_delete_docs()
        self.assertEqual(len(upload_response["items"]), delete_response["deleted"])

    def test_delete_nhif_outpatient_documents_from_elasticsearch(self):
        self.nhif_outpatient_scraper.es_index = "healthtools-test"
        with open(self.TEST_DATA + "/dummy_files/nhif_outpatient.json", "r") as my_file:
            data = my_file.read()
        upload_response = self.nhif_outpatient_scraper.elasticsearch_index(json.loads(data))
        delete_response = self.nhif_outpatient_scraper.elasticsearch_delete_docs()
        self.assertEqual(len(upload_response["items"]), delete_response["deleted"])

    def test_delete_nhif_outpatient_cs_documents_from_elasticsearch(self):
        self.nhif_outpatient_cs_scraper.es_index = "healthtools-test"
        with open(self.TEST_DATA + "/dummy_files/nhif_outpatient_cs.json", "r") as my_file:
            data = my_file.read()
        upload_response = self.nhif_outpatient_cs_scraper.elasticsearch_index(json.loads(data))
        delete_response = self.nhif_outpatient_cs_scraper.elasticsearch_delete_docs()
        self.assertEqual(len(upload_response["items"]), delete_response["deleted"])
