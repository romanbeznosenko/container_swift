"""
Client for interacting with the SWIFT code API.
"""

import os
import httpx
from typing import Dict, Any, List
from utils.logger import setup_logger
from utils.exceptions import APIIntegrationError

logger = setup_logger("api_client")

API_URL = os.getenv("SWIFT_API_URL", "http://api:8000")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))


def log_warning(message):
    print(f"WARNING: {message}")

async def create_swift_code(swift_code_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new SWIFT code by sending data to the main API.
    
    Args:
        swift_code_data: SWIFT code data to create
        
    Returns:
        Dict containing the created SWIFT code or error information
        
    Raises:
        APIIntegrationError: If there is an error communicating with the API
    """
    url = f"{API_URL}/api/v1/swift-code/"
    logger.info(f"Creating SWIFT code at {url}: {swift_code_data['swift_code']}")
    
    api_data = {
        "swiftCode": swift_code_data["swift_code"],
        "address": swift_code_data["address"],
        "countryISO2": swift_code_data["country_ISO2"],
        "countryName": swift_code_data["country_name"],
        "isHeadquarter": swift_code_data["is_headquarter"]
    }
    
    if "bank_name" in swift_code_data:
        api_data["bankName"] = swift_code_data["bank_name"]
    
    logger.info(f"Sending data to API: {api_data}")
    
    logger.info(f"Making request to URL: {url}")
    logger.info(f"API_URL is set to: {API_URL}")
    
    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            headers = {"Content-Type": "application/json"}
            response = await client.post(url, json=api_data, headers=headers)
            
            if response.status_code == 201:
                logger.info(f"Successfully created SWIFT code: {swift_code_data['swift_code']}")
                return response.json()
            elif response.status_code == 409:
                log_warning(f"SWIFT code already exists: {swift_code_data['swift_code']}")
                return {
                    "error": "conflict", 
                    "detail": f"SWIFT code {swift_code_data['swift_code']} already exists"
                }
            else:
                logger.error(f"Error creating SWIFT code: {response.status_code} - {response.text}")
                return {
                    "error": "api_error",
                    "status_code": response.status_code,
                    "detail": response.text
                }
    except httpx.RequestError as e:
        logger.error(f"Request error creating SWIFT code: {str(e)}")
        raise APIIntegrationError(f"Error communicating with API: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error creating SWIFT code: {str(e)}")
        raise APIIntegrationError(f"Unexpected error: {str(e)}")


async def create_swift_codes_batch(swift_codes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create multiple SWIFT codes by sending them to the API one by one.
    
    Args:
        swift_codes: List of SWIFT code data to create
        
    Returns:
        Dict containing results of the batch operation
    """
    total = len(swift_codes)
    successful = 0
    failed = 0
    skipped = 0
    errors = []
    
    logger.info(f"Starting batch creation of {total} SWIFT codes")
    
    for i, code_data in enumerate(swift_codes):
        try:
            result = await create_swift_code(code_data)
            
            if "error" not in result:
                successful += 1
            elif result.get("error") == "conflict":
                skipped += 1
            else:
                failed += 1
                errors.append({
                    "swift_code": code_data["swift_code"],
                    "error": result.get("detail", "Unknown error")
                })
                
            if (i + 1) % 10 == 0 or (i + 1) == total:
                logger.info(f"Progress: {i+1}/{total} ({successful} successful, {skipped} skipped, {failed} failed)")
        except Exception as e:
            failed += 1
            errors.append({
                "swift_code": code_data["swift_code"],
                "error": str(e)
            })
            logger.error(f"Error processing {code_data['swift_code']}: {str(e)}")
    
    logger.info(f"Batch creation complete: {successful} successful, {skipped} skipped, {failed} failed")
    
    return {
        "total": total,
        "successful": successful,
        "skipped": skipped,
        "failed": failed,
        "errors": errors[:100] if errors else []
    }


async def check_api_health() -> bool:
    """
    Check if the SWIFT code API is healthy.
    
    Returns:
        bool: True if the API is healthy, False otherwise
    """
    url = f"{API_URL}/api/v1/swift-code/"
    logger.info(f"Checking API health at {url}")
    logger.info(f"API_URL is set to: {API_URL}")
    
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(url)
            is_healthy = response.status_code == 200
            logger.info(f"API health check result: {'Healthy' if is_healthy else 'Unhealthy'}")
            logger.info(f"API health check status code: {response.status_code}")
            return is_healthy
    except Exception as e:
        logger.error(f"API health check failed: {str(e)}")
        return False