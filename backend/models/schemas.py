from datetime import datetime

from pydantic import BaseModel

# --- Teams ---


class TeamCreate(BaseModel):
    name: str
    level: str = "unknown"


class TeamUpdate(BaseModel):
    name: str | None = None
    level: str | None = None


class TeamResponse(BaseModel):
    id: str
    name: str
    level: str
    created_at: datetime
    updated_at: datetime


# --- Roster Players ---


class RosterPlayerCreate(BaseModel):
    team_id: str
    jersey_number: str
    full_name: str
    position: str | None = None
    height: str | None = None
    dominant_hand: str | None = None
    role: str | None = None
    notes: str | None = None


class RosterPlayerUpdate(BaseModel):
    jersey_number: str | None = None
    full_name: str | None = None
    position: str | None = None
    height: str | None = None
    dominant_hand: str | None = None
    role: str | None = None
    notes: str | None = None


class RosterPlayerResponse(BaseModel):
    id: str
    team_id: str
    jersey_number: str
    full_name: str
    position: str | None
    height: str | None
    dominant_hand: str | None
    role: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


# --- Films ---


class FilmUploadInitiate(BaseModel):
    team_id: str
    file_name: str
    file_size_bytes: int


class FilmUploadInitiateResponse(BaseModel):
    film_id: str
    upload_url: str


class FilmUploadComplete(BaseModel):
    film_id: str


class FilmResponse(BaseModel):
    id: str
    team_id: str
    file_name: str
    file_size_bytes: int
    status: str
    duration_seconds: int | None
    chunk_count: int | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime


# --- Reports ---


class ReportCreate(BaseModel):
    team_id: str
    film_ids: list[str]


class ReportCreateResponse(BaseModel):
    report_id: str | None = None
    payment_required: bool = False


class ReportResponse(BaseModel):
    id: str
    team_id: str
    status: str
    title: str | None
    prompt_version: str
    error_message: str | None
    generation_time_seconds: int | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class SectionStatus(BaseModel):
    model_config = {"protected_namespaces": ()}

    section_type: str
    status: str
    model_used: str | None = None
    generation_time_seconds: int | None = None


class ReportDetailResponse(ReportResponse):
    sections: list[SectionStatus] = []
    pdf_url: str | None = None


# --- Stripe ---


class CheckoutSessionCreate(BaseModel):
    team_id: str
    film_ids: list[str]


class CheckoutSessionResponse(BaseModel):
    checkout_url: str
    payment_id: str
