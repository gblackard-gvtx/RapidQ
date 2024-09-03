from pydantic import BaseModel
from typing import Any, Dict, List

class Collection(BaseModel):
    name: str

class Result(BaseModel):
    collections: List[Collection]

class CollectionResponse(BaseModel):
    time: float
    status: str
    result: Result
#Below is the classes for collection config
class ScalarConfig(BaseModel):
    type: str

class QuantizationConfig(BaseModel):
    scalar: ScalarConfig

class WalConfig(BaseModel):
    wal_capacity_mb: int
    wal_segments_ahead: int

class OptimizerConfig(BaseModel):
    deleted_threshold: float
    vacuum_min_vector_number: int
    default_segment_number: int
    flush_interval_sec: int

class HnswConfig(BaseModel):
    m: int
    ef_construct: int
    full_scan_threshold: int

class ConfigParams(BaseModel):
    params: Dict[str, Any] = {}

class Config(BaseModel):
    params: ConfigParams
    hnsw_config: HnswConfig
    optimizer_config: OptimizerConfig
    wal_config: WalConfig
    quantization_config: QuantizationConfig

class PayloadSchema(BaseModel):
    data_type: str
    points: int

class ConfigResult(BaseModel):
    status: str
    optimizer_status: str
    segments_count: int
    config: Config
    payload_schema: PayloadSchema
    vectors_count: int
    indexed_vectors_count: int
    points_count: int

class CollectionConfig(BaseModel):
    time: float
    status: str
    result: ConfigResult