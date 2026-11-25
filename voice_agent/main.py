import asyncio
import uuid

import httpx

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from agent.state import initialize_state
from agent.graph import build_agent_graph, run_conversation
from services.gumasta_api import GumastaAPI


app = FastAPI(
    title="Gumasta Voice Agent",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

security = HTTPBearer()

sessions = {}


class CreateSessionRequest(BaseModel):
    shop_id: str


class MessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/sessions", status_code=201)
async def create_session(
    request: CreateSessionRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    api = GumastaAPI(credentials.credentials)

    try:
        user = await api.get_current_user()
        await api.get_shop(request.shop_id)

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail="Unable to access shop"
        )

    session_id = str(uuid.uuid4())

    sessions[session_id] = {
        "owner_id": user["id"],
        "state": initialize_state(request.shop_id),
        "lock": asyncio.Lock()
    }

    return {
        "session_id": session_id,
        "response": "Welcome! What would you like to order?",
        "status": "collecting_details"
    }


@app.post("/sessions/{session_id}/message")
async def send_message(
    session_id: str,
    request: MessageRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    session = sessions.get(session_id)

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    api = GumastaAPI(credentials.credentials)

    try:
        user = await api.get_current_user()

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail="Authentication failed"
        )

    if session["owner_id"] != user["id"]:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    if not request.message.strip():
        raise HTTPException(
            status_code=422,
            detail="Message cannot be empty"
        )

    async with session["lock"]:

        graph = build_agent_graph(api)

        try:
            result = await run_conversation(
                graph,
                session["state"],
                request.message.strip()
            )

        except Exception:
            raise HTTPException(
                status_code=502,
                detail="Unable to process message"
            )

        session["state"] = result

        return {
            "session_id": session_id,
            "response": result["response"],
            "status": result["status"],
            "order_draft": result["order_draft"],
            "order_id": result["order_id"]
        }