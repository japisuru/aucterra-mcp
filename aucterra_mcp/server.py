import os
import base64
import re
from typing import List, Dict, Any, Union, Type
import httpx
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("aucterra")

API_KEY = os.getenv("AUCTERRA_API_KEY")
EXTRACTION_URL = "https://5gn4u7v34c2pabqoqudprz4szq0ygrdt.lambda-url.us-east-1.on.aws/parser/document-extract"
CLASSIFICATION_URL = "https://5gn4u7v34c2pabqoqudprz4szq0ygrdt.lambda-url.us-east-1.on.aws/parser/document-classify"


def is_base64(s: str) -> bool:
    try:
        return base64.b64encode(base64.b64decode(s)).decode("utf-8") == s
    except Exception:
        return False


def encode_file_to_base64(file_path: str) -> str:
    with open(file_path, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")


async def prepare_input_data(input_data: str) -> str:
    if os.path.exists(input_data):
        return encode_file_to_base64(input_data)
    if is_base64(input_data):
        return input_data
    if re.match(r"^https?://", input_data):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(input_data)
                response.raise_for_status()
                return base64.b64encode(response.content).decode("utf-8")
        except Exception as e:
            raise ValueError(f"Failed to download document from URL: {e}")
    raise ValueError("Invalid input_data: must be a local path, base64 string, or a valid URL.")


# -------------------------------
# 🛠 Document Extraction Tool
# -------------------------------
class ExtractionInput(BaseModel):
    input_data: str = Field(..., description="Document to extract from. Accepts a local file path, URL, or base64 string.")
    fields: List[Dict[str, Any]] = Field(..., description="List of field definitions to extract. Can be nested.")
    document_id: str = Field("123", description="Unique identifier for the document.")
    extraction_type: str = Field("generic", description="Extraction type: 'generic' or 'specific'.")

@mcp.tool()
async def document_extraction_tool(
    input_data: str,
    fields: List[Dict[str, Any]],
    document_id: str = "123",
    extraction_type: str = "generic"
) -> Union[Dict[str, Any], str]:
    name: str = "document_extraction_tool"
    description: str = (
        "Extracts structured data from documents using a parsing service. Supports nested fields and multiple input types."
    )
    args_schema: Type[BaseModel] = ExtractionInput
    try:
        input_data = await prepare_input_data(input_data)
    except Exception as e:
        return f"Invalid input_data: {str(e)}"

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


# -------------------------------
# 🧠 Document Classification Tool
# -------------------------------
class ClassificationInput(BaseModel):
    input_data: str = Field(..., description="Document to classify. Accepts a local file path, URL, or base64 string.")
    classes: List[str] = Field(..., description="List of possible document classes.")
    document_id: str = Field("123", description="Unique identifier for the document.")

@mcp.tool()
async def document_classification_tool(
    input_data: str,
    classes: List[str],
    document_id: str = "123"
) -> Union[Dict[str, Any], str]:
    name: str = "document_classification_tool"
    description: str = "Classifies the document into a predefined category using the classification service."
    args_schema: Type[BaseModel] = ClassificationInput
    try:
        input_data = await prepare_input_data(input_data)
    except Exception as e:
        return f"Invalid input_data: {str(e)}"

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
