from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi.responses import HTMLResponse
from models.collections import CollectionResponse
from src.utils.qdrant_server import Qdrant, DistanceMetric
from src.models.settings import Settings
settings = Settings()

client = Qdrant(host=settings.QDRANT__SERVICE__HOST, port=settings.QDRANT__SERVICE__PORT, api_key=settings.QDRANT__SERVICE__API_KEY)

router = APIRouter(tags=["collections"])

# get all collections
@router.get("/collections", response_class=CollectionResponse)
async def collections(request: Request):
    collections: CollectionResponse = client.collections()
    return collections.model_dump()

#create a new collection
@router.post("/create-collection/")
async def create_collection(
    collection_name: str,
    vector_size: int,
    distance: DistanceMetric
):
    try:
        client.create_collection(collection_name, vector_size, distance)
        return {"message": f"Collection '{collection_name}' created successfully with distance metric '{distance}'."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating collection: {e}")