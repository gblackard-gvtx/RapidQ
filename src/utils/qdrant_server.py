from enum import Enum
from qdrant_client import QdrantClient, models
from fastembed import TextEmbedding
from typing import List, Optional
import fitz  # PyMuPDF
import os
import uuid
import logging
from src.models.payload import Payload
from src.models.collections import CollectionResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Define the DistanceMetric enum
class DistanceMetric(str, Enum):
    EUCLID = models.Distance.EUCLID
    COSINE = models.Distance.COSINE
    DOT = models.Distance.DOT

class Qdrant:
    """
    Class to interact with Qdrant for managing embeddings with multitenancy support.
    """

    def __init__(self, host: str, port: int, api_key: Optional[str] = None):
        self.host = host
        self.port = port
        self.api_key = api_key
        self.client = self._initialize_client()
        self.embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

    def _initialize_client(self) -> QdrantClient:
        try:
            client = QdrantClient(
                url=f"http://{self.host}:{self.port}",
                api_key=self.api_key,
            )
            logger.info("Qdrant client initialized successfully.")
            return client
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant client: {e}")
            raise

    def collections(self) -> CollectionResponse:
        """List all collections in Qdrant."""
        try:
            collections = self.client.get_collections()
            logger.info(f"Retrieved collections: {collections}")
            return collections
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            return []
        
    def get_collection_details(self, collection_name: str) -> dict:
        """Retrieve the details of a Qdrant collection."""
        try:
            collection_info = self.client.get_collection(collection_name)
            logger.info(f"Retrieved collection details for '{collection_name}'.")
            return collection_info
        except Exception as e:
            logger.error(f"Error retrieving collection '{collection_name}': {e}")
            raise

    def create_collection(self, collection_name: str, vector_size: int, distance: DistanceMetric):
        try:
            # Check if the collection already exists
            if not self.client.check_collection_exists(collection_name):
                # Create collection with specified vector size and distance
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(size=vector_size, distance=distance.value)
                )
                logger.info(f"Collection '{collection_name}' created successfully with distance metric '{distance.value}'.")
            else:
                logger.info(f"Collection '{collection_name}' already exists.")
        except Exception as e:
            logger.error(f"Error creating collection '{collection_name}': {e}")

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from a PDF file."""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                text += page.get_text()
            doc.close()
            logger.info(f"Text extracted from PDF: {pdf_path}")
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF '{pdf_path}': {e}")
            return ""

    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create dense embeddings from a list of texts."""
        try:
            embeddings = list(self.embedding_model.embed(texts))
            logger.info("Embeddings created successfully.")
            return embeddings
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            return []

    def update_pdf_embeddings(self, pdf_folder: str, collection_name: str, tenant_id: str):
        """Update embeddings for all PDFs in the specified folder for a specific tenant."""
        try:
            # Track existing points
            existing_points = self._get_existing_points(collection_name, tenant_id)
            
            # Generate embeddings for all PDFs
            for pdf_file in os.listdir(pdf_folder):
                if pdf_file.endswith('.pdf'):
                    pdf_path = os.path.join(pdf_folder, pdf_file)
                    text = self.extract_text_from_pdf(pdf_path)
                    if text:
                        embeddings = self.create_embeddings([text])
                        
                        # Check if point exists for the PDF file
                        point_id = self._generate_point_id(pdf_file)
                        
                        if point_id in existing_points:
                            # Update existing point
                            self._update_point(collection_name, point_id, embeddings[0], tenant_id)
                        else:
                            # Insert new point
                            self._insert_point(collection_name, point_id, embeddings[0], tenant_id)
            logger.info(f"PDF embeddings updated for tenant '{tenant_id}' in collection '{collection_name}'.")
        except Exception as e:
            logger.error(f"Error updating PDF embeddings for tenant '{tenant_id}': {e}")

    def _get_existing_points(self, collection_name: str, tenant_id: str) -> set:
        """Retrieve existing point IDs in a collection for a specific tenant."""
        try:
            response = self.client.scroll(
                collection_name=collection_name,
                filter=models.Filter(
                    must=[models.FieldCondition(
                        key="tenant_id",
                        match=models.MatchValue(value=tenant_id)
                    )]
                )
            )
            point_ids = set(point.id for point in response.result.points)
            logger.info(f"Retrieved existing point IDs for tenant '{tenant_id}'.")
            return point_ids
        except Exception as e:
            logger.error(f"Error retrieving existing points for tenant '{tenant_id}': {e}")
            return set()

    def _generate_point_id(self, pdf_file: str) -> str:
        """Generate a unique point ID from a PDF file name."""
        try:
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, pdf_file))
            logger.info(f"Generated point ID for file '{pdf_file}': {point_id}")
            return point_id
        except Exception as e:
            logger.error(f"Error generating point ID for file '{pdf_file}': {e}")
            return ""

    def _insert_point(self, collection_name: str, point_id: str, vector: List[float], tenant_id: str, payload:Payload):
        """Insert a new point into the collection for a specific tenant."""
        try:
            self.client.upsert(
                collection_name=collection_name,
                points=[
                    models.PointStruct(
                        id=point_id,
                        vector=vector,
                        payload=payload.model_dump()
                    )
                ]
            )
            logger.info(f"Inserted new point '{point_id}' for tenant '{payload.tenant_id}' in collection '{collection_name}'.")
        except Exception as e:
            logger.error(f"Error inserting point '{point_id}' for tenant '{payload.tenant_id}': {e}")

    def _update_point(self, collection_name: str, point_id: str, vector: List[float], payload:Payload):
        """Update an existing point's vector in the collection for a specific tenant."""
        try:
            self.client.upsert(
                collection_name=collection_name,
                points=[
                    models.PointStruct(
                        id=point_id,
                        vector=vector,
                        payload=payload.tenent_id
                    )
                ]
            )
            logger.info(f"Updated point '{point_id}' for tenant '{payload.tenant_id}' in collection '{collection_name}'.")
        except Exception as e:
            logger.error(f"Error updating point '{point_id}' for tenant '{payload.tenant_id}': {e}")
