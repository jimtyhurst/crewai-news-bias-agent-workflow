import time
import pandas as pd
import requests
from io import StringIO

from google.auth.transport.requests import AuthorizedSession
from google.oauth2.credentials import Credentials
from urllib.parse import quote
from crewai.tools import BaseTool

def download_keboola_table(table_id: str, kbc_api_token: str, kbc_api_url: str) -> pd.DataFrame:
    """
    Download a Keboola table using async export and assign columns from table metadata.
    """
    headers = {"X-StorageApi-Token": kbc_api_token}
    kbc_api_url = kbc_api_url.rstrip("/")
    max_attempts = 30

    try:
        columns = fetch_table_columns(table_id, kbc_api_token, kbc_api_url)

        print(f"Starting async export for table: {table_id}")
        export_url = f"{kbc_api_url}/v2/storage/tables/{table_id}/export-async"
        export_response = requests.post(export_url, headers=headers, json={"format": "rfc"})
        export_response.raise_for_status()
        job_id = export_response.json()["id"]

        job_url = f"{kbc_api_url}/v2/storage/jobs/{job_id}"
        for attempt in range(1, max_attempts + 1):
            job_response = requests.get(job_url, headers=headers)
            job_response.raise_for_status()
            status = job_response.json()["status"]
            print(f"[{attempt}/{max_attempts}] Job status: {status}")
            if status == "success":
                break
            elif status in {"error", "cancelled"}:
                raise Exception(f"Job failed: {job_response.json()}")
            time.sleep(2)
        else:
            raise TimeoutError("Export job did not complete in time.")

        file_id = job_response.json()["results"]["file"]["id"]
        metadata_url = f"{kbc_api_url}/v2/storage/files/{file_id}?federationToken=1"
        metadata = requests.get(metadata_url, headers=headers).json()
        manifest_url = metadata["url"]

        access_token = metadata.get("gcsCredentials", {}).get("access_token") or metadata["credentials"]["access_token"]
        creds = Credentials(token=access_token)
        authed_session = AuthorizedSession(creds)

        print(f"Downloading manifest: {manifest_url}")
        manifest = requests.get(manifest_url).json()
        entries = manifest.get("entries", [])

        merged_df = pd.DataFrame()
        for entry in entries:
            gs_url = entry["url"]
            _, path = gs_url.split("gs://", 1)
            bucket_name, *blob_parts = path.split("/")
            blob_path = "/".join(blob_parts)
            quoted_path = quote(blob_path, safe="")

            download_url = f"https://storage.googleapis.com/storage/v1/b/{bucket_name}/o/{quoted_path}?alt=media"
            response = authed_session.get(download_url)
            response.raise_for_status()

            df = pd.read_csv(StringIO(response.text), header=None)
            df.columns = columns
            merged_df = pd.concat([merged_df, df], ignore_index=True)

            print(f"Downloaded slice: {gs_url}")

        print(f"Data from {table_id} downloaded.")
        return merged_df

    except Exception as e:
        print(f"Error: {str(e)}")
        raise

def fetch_table_columns(table_id: str, kbc_api_token: str, kbc_api_url: str) -> list[str]:
    """Fetch column names from a Keboola table."""
    headers = {"X-StorageApi-Token": kbc_api_token}
    url = f"{kbc_api_url.rstrip('/')}/v2/storage/tables/{table_id}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()["columns"]