"""Pydantic Request and Response Schemas for FastAPI backend."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ChatQueryRequest(BaseModel):
    query: str = Field(..., description="The user prompt or query to route through the multi-agent system")


class ChatQueryResponse(BaseModel):
    query: str
    response: str
    active_agents: List[str]
    agent_outputs: Dict[str, str]


class SendEmailModel(BaseModel):
    to: str = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Email subject line")
    body: str = Field(..., description="Email message body")
    is_html: bool = Field(False, description="Whether the email body is HTML")


class CreateEventModel(BaseModel):
    summary: str = Field(..., description="Event title or summary")
    start_time: str = Field(..., description="ISO 8601 start time or date")
    end_time: str = Field(..., description="ISO 8601 end time or date")
    description: Optional[str] = Field(None, description="Event notes or agenda")
    add_meet_link: bool = Field(True, description="Whether to generate a Google Meet video conference link")


class CreateNoteModel(BaseModel):
    title: str = Field(..., description="Note or task title")
    notes: Optional[str] = Field(None, description="Detailed notes body or checklist description")
    due_date: Optional[str] = Field(None, description="Optional due date in ISO 8601 or RFC 3339 format")
