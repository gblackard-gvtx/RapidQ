from typing import Optional
from pydantic import BaseModel

class Payload(BaseModel):
    """
    Payload class represents a data payload with the following attributes:

    Attributes:
        tenet_id (str): The ID of the tenant.
        source (str): The source of the payload.
        category (Optional[str]): The category of the payload. These can be used to group documents together based on folders or tags.
        subcategory (Optional[str]): The subcategory of the payload. These can be used to further group documents within a category.

    """
    tenet_id: str
    source: str
    category: Optional[str] = None
    subcategory: Optional[str] = None

