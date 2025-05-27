import os
import base64
from typing import Dict, Any, List
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("aucterra")

API_KEY = os.getenv("AUCTERRA_API_KEY")
EXTRACTION_URL = "https://5gn4u7v34c2pabqoqudprz4szq0ygrdt.lambda-url.us-east-1.on.aws/parser/document-extract"
CLASSIFICATION_URL = "https://5gn4u7v34c2pabqoqudprz4szq0ygrdt.lambda-url.us-east-1.on.aws/parser/document-classify"


def encode_file_to_base64(file_path: str) -> str:
    with open(file_path, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")


@mcp.tool()
async def document_extraction_tool(
        input_data: str,
        fields: List[Dict[str, Any]],
        document_id: str = "123",
        extraction_type: str = "generic"
) -> Dict[str, Any] | str:
    """Extract structured data from documents. Supports nested fields."""

    if os.path.exists(input_data):
        input_data = encode_file_to_base64(input_data)

    payload = {
        "input_data": input_data,
        "fields": fields,
        "document_id": document_id,
        "extraction_type": extraction_type,
        "advanced_ocr": "disable"
    }

    headers = {
        "accept": "application/json",
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(EXTRACTION_URL, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return f"Extraction failed: {str(e)}"


@mcp.tool()
async def document_classification_tool(
    input_data: str,
    classes: List[str],
    document_id: str = "123"
) -> Dict[str, Any] | str:
    """Classify document into a predefined class."""

    if os.path.exists(input_data):
        input_data = encode_file_to_base64(input_data)

    payload = {
        "input_data": input_data,
        "classes": classes,
        "document_id": document_id
    }

    headers = {
        "accept": "application/json",
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(CLASSIFICATION_URL, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return f"Classification failed: {str(e)}"
