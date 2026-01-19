from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="Texto para análise")
    lang: str | None = Field("en", description="Idioma (en apenas)")


class PredictResponse(BaseModel):
    inference_id: str
    label: str = Field(..., description="Sentimento: positive, neutral, negative")
    score: float = Field(..., description="Confiança 0-1")
    model_version: str = Field(..., description="Versão do modelo/serviço")
    inference_time_ms: float = Field(..., description="Tempo de inferência (ms)")


class HealthResponse(BaseModel):
    status: str
    version: str
    model_ready: bool


class ErrorResponse(BaseModel):
    error: str
    detail: str
