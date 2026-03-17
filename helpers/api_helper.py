import requests
import base64
import time
import logging
import config
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)

def get_auth_headers() -> Dict[str, str]:
    """
    Generate basic authentication headers using credentials from config.
    
    Returns:
        Dict containing Authorization and Content-Type headers.
    """
    logger.debug(f"Generating auth headers for {config.EMAIL}")
    credentials = f"{config.EMAIL}:{config.PASSWORD}"
    token = base64.b64encode(credentials.encode()).decode()
    return {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json"
    }

def ingest_logs(stream_name: str, records: List[Dict[str, Any]]) -> requests.Response:
    """
    Ingest a list of log records into an OpenObserve stream.
    
    Args:
        stream_name: Name of the target stream
        records: List of dicts, each representing one log record
        
    Returns:
        requests.Response object from the ingestion API
        
    Raises:
        requests.exceptions.RequestException: If the API call fails
    """
    url = f"{config.BASE_URL}/api/{config.ORG}/{stream_name}/_json"
    logger.info(f"Ingesting {len(records)} records into stream '{stream_name}' at {url}")
    
    try:
        response = requests.post(
            url,
            headers=get_auth_headers(),
            json=records
        )
        response.raise_for_status()
        logger.info(f"Ingestion successful: HTTP {response.status_code}")
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to ingest logs into '{stream_name}': {e}")
        if hasattr(e, 'response') and e.response:
            logger.error(f"Response body: {e.response.text}")
        raise

def search_logs(stream_name: str, sql: Optional[str] = None, minutes_back: int = 15) -> List[Dict[str, Any]]:
    """
    Search logs in a specified stream.
    
    Args:
        stream_name: Name of the target stream
        sql: Optional custom SQL query. If None, selects all from stream.
        minutes_back: Time range for the search in minutes.
        
    Returns:
        List of matching log records (hits).
        
    Raises:
        requests.exceptions.RequestException: If the search API call fails
    """
    url = f"{config.BASE_URL}/api/{config.ORG}/_search?type=logs"
    
    end_time = int(time.time() * 1_000_000)
    start_time = end_time - (minutes_back * 60 * 1_000_000)

    if sql is None:
        sql = f'SELECT * FROM "{stream_name}"'
    
    logger.info(f"Searching logs in '{stream_name}' with SQL: {sql}")
    
    payload = {
        "query": {
            "sql": sql,
            "start_time": start_time,
            "end_time": end_time,
            "from": 0,
            "size": 100
        }
    }

    try:
        response = requests.post(
            url,
            headers=get_auth_headers(),
            json=payload
        )
        response.raise_for_status()
        hits = response.json().get("hits", [])
        logger.info(f"Search successful: found {len(hits)} records")
        return hits
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to search logs in '{stream_name}': {e}")
        if hasattr(e, 'response') and e.response:
            logger.error(f"Response body: {e.response.text}")
        raise