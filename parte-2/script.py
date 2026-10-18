import requests
from datetime import datetime
from google.cloud import bigquery
import os
from dotenv import load_dotenv

load_dotenv()

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_data(self, endpoint):
        response = requests.get(f"{self.base_url}/{endpoint}")
        return response.json()
    
    def transform_data(self, data):
        rows = []
        for ep in data["results"]:
            row = {
                "id": ep["id"],
                "name": ep["name"],
                "air_date": ep["air_date"],
                "episode": ep["episode"],
                "character_ids": [int(url.rstrip("/").split("/")[-1]) for url in ep["characters"]],
                "url": ep["url"],
                "created": ep["created"],
                "date_upload": datetime.now().strftime("%Y-%m-%d")
            }
            rows.append(row)

        return rows

    def load_all_data(self):
        all_rows = []
        for page in range(1, 4):
            data = self.get_data(f"episode?page={page}")
            all_rows.extend(self.transform_data(data))
        return all_rows

class BigqueryClient:
    def __init__(self, table_id, credentials_path):
        self.table_id = table_id
        self.client = bigquery.Client.from_service_account_json(credentials_path)
    def insert_data(self, data):
        try:
            schema = [
                bigquery.SchemaField("id", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("name", "STRING"),
                bigquery.SchemaField("air_date", "STRING"),
                bigquery.SchemaField("episode", "STRING"),
                bigquery.SchemaField("character_ids", "INTEGER", mode="REPEATED"),
                bigquery.SchemaField("url", "STRING"),
                bigquery.SchemaField("created", "TIMESTAMP"),
                bigquery.SchemaField("date_upload", "DATE"),
            ]
            job_config = bigquery.LoadJobConfig( schema=schema, write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE)
            job = self.client.load_table_from_json(data, self.table_id, job_config=job_config)
            job.result()
            print(f"Cargadas {job.output_rows} filas en {self.table_id}")

        except Exception as e:
            print(f"ERROR AL SUBIR DATOS: {e}")


GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
API_URL = "https://rickandmortyapi.com/api"
TABLE_ID = "just-program-384022.RAW.SANDBOX_RICK_MORTY"

api_client = APIClient(API_URL)
row_data = api_client.load_all_data()
bq = BigqueryClient(TABLE_ID, GOOGLE_APPLICATION_CREDENTIALS)
bq.insert_data(row_data)