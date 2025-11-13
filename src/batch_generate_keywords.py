"""
Batch process to generate Hebrew keywords for stocks and finance industry
and store them in BigQuery
"""
import os
from datetime import datetime
from google.cloud import bigquery
from google.cloud import secretmanager
from src.generate_keywords import generate_keywords_from_gemini
from src.config import BIGQUERY_KEYWORDS_TABLE, BIGQUERY_KEYWORD_COLUMN, CHECK_DUPLICATES, KEYWORDS_PER_GENERATION


def get_secret(project_id: str, secret_id: str, version_id: str = "latest") -> str:
    """
    Retrieve a secret from GCP Secret Manager.

    Args:
        project_id: GCP project ID
        secret_id: Secret identifier
        version_id: Version of the secret (default: "latest")

    Returns:
        Secret value as string
    """
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        print(f"Error retrieving secret {secret_id}: {e}")
        raise


def get_existing_keywords(bq_client: bigquery.Client) -> set:
    """
    Retrieve all existing keywords from BigQuery to avoid duplicates.

    Args:
        bq_client: BigQuery client instance

    Returns:
        Set of existing keywords
    """
    try:
        query = f"""
        SELECT DISTINCT {BIGQUERY_KEYWORD_COLUMN}
        FROM `{BIGQUERY_KEYWORDS_TABLE}`
        WHERE {BIGQUERY_KEYWORD_COLUMN} IS NOT NULL
        """
        print("Fetching existing keywords from BigQuery...")
        result = bq_client.query(query).result()
        # Access the column dynamically using the column name
        existing_keywords = {getattr(row, BIGQUERY_KEYWORD_COLUMN) for row in result}
        print(f"Found {len(existing_keywords)} existing keywords in BigQuery")
        return existing_keywords
    except Exception as e:
        print(f"Error fetching existing keywords: {e}")
        return set()


def insert_keywords_to_bigquery(bq_client: bigquery.Client, keywords: list) -> bool:
    """
    Insert new keywords into BigQuery table.

    Args:
        bq_client: BigQuery client instance
        keywords: List of keyword dictionaries to insert

    Returns:
        True if successful, False otherwise
    """
    if not keywords:
        print("No keywords to insert")
        return True

    try:
        # Prepare rows for insertion
        rows_to_insert = []

        for keyword_data in keywords:
            row = {
                BIGQUERY_KEYWORD_COLUMN: keyword_data["keyword"]
            }
            rows_to_insert.append(row)

        print(f"Inserting {len(rows_to_insert)} new keywords into BigQuery...")
        errors = bq_client.insert_rows_json(BIGQUERY_KEYWORDS_TABLE, rows_to_insert)

        if errors:
            print(f"Errors occurred while inserting rows: {errors}")
            return False
        else:
            print(f"Successfully inserted {len(rows_to_insert)} keywords")
            return True

    except Exception as e:
        print(f"Error inserting keywords to BigQuery: {e}")
        return False


async def main():
    """
    Main orchestration function to generate and store keywords.
    """
    # Get project ID from environment
    project_id = os.getenv("GCP_PROJECT_ID")
    if not project_id:
        raise ValueError("GCP_PROJECT_ID environment variable not set.")

    print(f"Starting keyword generation job for project: {project_id}")

    # Get Gemini API key
    # Try local .env first, then Secret Manager
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("GEMINI_API_KEY not found in environment, fetching from Secret Manager...")
        try:
            gemini_api_key = get_secret(project_id, "gemini-api-key")
        except Exception as e:
            print(f"Failed to retrieve Gemini API key: {e}")
            return

    # Initialize BigQuery client
    try:
        bq_client = bigquery.Client()
        print("Successfully connected to BigQuery")
    except Exception as e:
        print(f"Failed to connect to BigQuery: {e}")
        return

    # Get existing keywords if duplicate checking is enabled
    existing_keywords = set()
    if CHECK_DUPLICATES:
        existing_keywords = get_existing_keywords(bq_client)

    # Generate keywords from Gemini
    print(f"\nGenerating {KEYWORDS_PER_GENERATION} keywords using Gemini AI...")
    generated_keywords = await generate_keywords_from_gemini(
        gemini_api_key=gemini_api_key,
        num_keywords=KEYWORDS_PER_GENERATION
    )

    if not generated_keywords:
        print("No keywords were generated. Exiting.")
        return

    # Filter out duplicates
    new_keywords = []
    duplicate_count = 0

    for keyword_data in generated_keywords:
        keyword_text = keyword_data["keyword"]
        if keyword_text not in existing_keywords:
            new_keywords.append(keyword_data)
            existing_keywords.add(keyword_text)  # Update in-memory set
        else:
            duplicate_count += 1
            print(f"  Skipping duplicate: {keyword_text}")

    print(f"\nFiltering results:")
    print(f"  Total generated: {len(generated_keywords)}")
    print(f"  Duplicates found: {duplicate_count}")
    print(f"  New keywords to insert: {len(new_keywords)}")

    # Insert new keywords to BigQuery
    if new_keywords:
        success = insert_keywords_to_bigquery(bq_client, new_keywords)
        if success:
            print("\n✓ Job completed successfully!")
        else:
            print("\n✗ Job completed with errors during insertion")
    else:
        print("\nNo new keywords to insert. All generated keywords already exist.")
        print("✓ Job completed successfully!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
