# RapidQ: FastAPI Wrapper for Qdrant Python SDK

RapidQ is a FastAPI wrapper around the Qdrant Python SDK. It provides an interface for creating and modifying Qdrant collections, handling multi-tenancy, and supporting ETL processes for managing data in Qdrant. RapidQ is designed to simplify the management of vector-based data in Qdrant, enabling seamless integration and efficient data operations.

## Features

- Create and Modify Qdrant Collections: Easily create and manage Qdrant collections with configurable vector sizes and distance metrics.
- Multitenancy Support: Load and manage embeddings with tenant-specific payloads, allowing for isolated data management and vector search capabilities across multiple tenants.
- ETL Processes for Qdrant: Tailored functionality for extracting, transforming, and loading data into Qdrant, including support for managing data from PDFs and JSON.
- Flexible Payload Structure: Use customizable payloads to include additional metadata, enabling detailed filtering and search capabilities.

## Requirements

- Python 3.7+
- qdrant-client library for interacting with the Qdrant vector database.
- fastembed library for generating text embeddings.
- PyMuPDF library (fitz) for extracting text from PDFs.
- pydantic library for defining structured payloads.

## Installation

Install the required Python libraries:

```bash
pip install qdrant-client fastembed PyMuPDF pydantic
```

## Usage

1. Initialize the Qdrant Class
    Initialize the Qdrant client with the server host, port, and API key.

    ```python
    from src.utils.qdrant_server import Qdrant

    # Initialize Qdrant with host, port, and API key

    qdrant_instance = Qdrant(host="localhost", port=6333, api_key="your_api_key")
    ```

2. Create a Collection in Qdrant

    Create a collection in Qdrant to store vectors, specifying the collection name, vector size, and distance metric.

    ```python
    qdrant_instance.create_collection(collection_name="your_collection", vector_size=384, distance="Cosine")
    collection_name: Name of the collection.
    vector_size: The size of the vectors (e.g., 384 for the model used).
    distance: The distance metric to use (e.g., "Cosine").
    ```

3. Process PDFs and Load Embeddings into Qdrant
    Process PDF files in a specified folder and load the resulting embeddings into a Qdrant collection.

    ```python
    pdf_folder = "path/to/pdf_folder"
    qdrant_instance.process_pdfs_and_load_to_qdrant(pdf_folder, collection_name="your_collection", group_id="user_1")
    pdf_folder: Path to the folder containing PDF files.
    collection_name: The Qdrant collection name where embeddings will be stored.
    group_id: A unique identifier for grouping vectors, supporting multitenancy.
    ```

4. Manage JSON Data in Qdrant
    Create embeddings from JSON data and update Qdrant collections.

    ```python
    json_data = [
        {"id": "1", "content": "This is the first document."},
        {"id": "2", "content": "This is the second document."}
    ]

    qdrant_instance.create_embeddings_from_json(json_data, text_key="content", collection_name="json_collection", tenant_id="tenant_1")
    json_data: List of dictionaries representing the JSON data.
    text_key: Key in the JSON data that contains the text for which embeddings will be generated.
    collection_name: The Qdrant collection name where embeddings will be stored.
    tenant_id: A unique identifier for the tenant.
    ```

Class Methods
__init__(self, host: str, port: int, api_key: str)
Initializes the Qdrant client and the text embedding model.

host: The hostname or IP address of the Qdrant server.
port: The port number on which the Qdrant server is running.
api_key: API key for authenticating with the Qdrant server.
create_collection(self, collection_name: str, vector_size: int, distance: DistanceMetric)
Creates a new collection in Qdrant.

collection_name: Name of the collection to create.
vector_size: Dimension size of the vectors to be stored in the collection.
distance: Distance metric for vector similarity (e.g., "Cosine").
extract_text_from_pdf(self, pdf_path: str) -> str
Extracts text from a PDF file.

pdf_path: Path to the PDF file.
create_embeddings_from_json(self, json_data: List[Dict[str, Any]], text_key: str, collection_name: str, tenant_id: str)
Creates embeddings from JSON data and updates Qdrant collections.

json_data: List of dictionaries representing the JSON data.
text_key: Key in the JSON data that contains the text for which embeddings will be generated.
collection_name: The Qdrant collection name where embeddings will be stored.
tenant_id: A unique identifier for the tenant.
process_pdfs_and_load_to_qdrant(self, pdf_folder: str, collection_name: str, group_id: str)
Combines extraction, embedding, and loading into a single process for ease of use.

pdf_folder: Path to the folder containing PDF files.
collection_name: The Qdrant collection name where embeddings will be stored.
group_id: A unique identifier for grouping vectors.
Payload Structure
When loading embeddings into Qdrant, the payload structure includes the tenant_id field for multitenancy support. The tenant_id field allows you to group vectors based on a unique identifier, enabling separation of data for different users or applications.

I have also added category and subcategory to the payload structure to allow for more detailed filtering and search capabilities. The payload is a Pydantic model that can be easily extended to include additional fields as needed.

Example Payload Structure
python
Copy code
from typing import Optional
from pydantic import BaseModel

class Payload(BaseModel):
    """
    Payload class represents a data payload with the following attributes:

    Attributes:
        tenant_id (str): The ID of the tenant.
        source (str): The source of the payload.
        category (Optional[str]): The category of the payload, used to group documents together based on folders or tags.
        subcategory (Optional[str]): The subcategory of the payload, used to further group documents within a category.
    """
    tenant_id: str
    source: str
    category: Optional[str] = None
    subcategory: Optional[str] = None
Example
python
Copy code
# Initialize Qdrant
qdrant_instance = Qdrant(host="localhost", port=6333, api_key="your_api_key")

# Create a collection
qdrant_instance.create_collection(collection_name="your_collection", vector_size=384, distance="Cosine")

# Process PDFs and load into Qdrant
pdf_folder = "path/to/pdf_folder"
qdrant_instance.process_pdfs_and_load_to_qdrant(pdf_folder, collection_name="your_collection", group_id="user_1")

# Process JSON data and load into Qdrant
json_data = [
    {"id": "1", "content": "This is the first document."},
    {"id": "2", "content": "This is the second document."}
]
qdrant_instance.create_embeddings_from_json(json_data, text_key="content", collection_name="json_collection", tenant_id="tenant_1")
License
This project is licensed under the MIT License. See the LICENSE file for more details.

Contact
For any questions or issues, please contact [Your Name].

This README now reflects the expanded functionality of RapidQ, highlighting its capabilities for managing Qdrant collections, supporting multitenancy, and handling ETL processes with FastAPI.