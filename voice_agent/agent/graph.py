from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage

from agent.state import AgentState
from agent.nodes import (
    load_catalogue,
    extract_conversation,
    process_items,
    process_customer,
    prepare_order,
    submit_order
)
from services.gumasta_api import GumastaAPI


def build_agent_graph(api: GumastaAPI):

    async def catalogue_node(state: AgentState):

        result = await load_catalogue(state, api)

        print("CATALOGUE:", result["catalogue"])

        return {
            **result,
        "   errors": []
        }

    async def extraction_node(state: AgentState):

        extracted = await extract_conversation(state)

        print("EXTRACTED:", extracted.model_dump_json(indent=2))

        return {"extracted": extracted}

    async def process_intent_node(state: AgentState):

        extracted = state["extracted"]

        if extracted.intent == "cancel_order":
            return {
                "status": "cancelled",
                "confirmed": False
            }

        item_updates = process_items(
            state, extracted
        )

        print("ITEM UPDATES:", item_updates)
        updated_state = {
            **state,
            **item_updates
        }

        customer_updates = await process_customer(
            updated_state,
            extracted,
            api
        )

        updated_state.update(customer_updates)

        errors = (
            item_updates.get("errors", [])
            + customer_updates.get("errors", [])
        )

        
        confirmed = (
            extracted.intent == "confirm_order"
            and state["status"] == "awaiting_confirmation"
            and updated_state["status"] == "awaiting_confirmation"
            and updated_state["order_draft"] is not None
            and not extracted.items
            and not errors
        )

        return {
            **item_updates,
            **customer_updates,
            "errors": errors,
            "confirmed": confirmed
        }

    def route_intent(state: AgentState):

        if state["status"] == "cancelled":
            return "cancel"

        if state["confirmed"]:
            return "submit"

        return "prepare"

    async def prepare_node(state: AgentState):

        return await prepare_order(state, api)

    async def submit_node(state: AgentState):

        try:
            return await submit_order(state, api)

        except Exception as exc:

            return {
                "status": "failed",
                "confirmed": False,
                "errors": [type(exc).__name__],
                "response": (
                    "I could not confirm that your order "
                    "was placed. Please ask the shop owner "
                    "to check before trying again."
                )
            }

    def cancel_node(state: AgentState):

        return {
            "requested_items": [],
            "order_draft": None,
            "confirmed": False,
            "response": "Your order draft has been cancelled."
        }

    graph = StateGraph(AgentState)

    graph.add_node("load_catalogue", catalogue_node)
    graph.add_node("extract_conversation", extraction_node)
    graph.add_node("process_intent", process_intent_node)
    graph.add_node("prepare_order", prepare_node)
    graph.add_node("submit_order", submit_node)
    graph.add_node("cancel_order", cancel_node)

    graph.add_edge(START, "load_catalogue")

    graph.add_edge(
        "load_catalogue",
        "extract_conversation"
    )

    graph.add_edge(
        "extract_conversation",
        "process_intent"
    )

    graph.add_conditional_edges(
        "process_intent",
        route_intent,
        {
            "prepare": "prepare_order",
            "submit": "submit_order",
            "cancel": "cancel_order"
        }
    )

    graph.add_edge("prepare_order", END)
    graph.add_edge("submit_order", END)
    graph.add_edge("cancel_order", END)

    return graph.compile()

async def run_conversation(
    graph,
    state: AgentState,
    message: str
):

    if state["status"] in {
        "completed",
        "cancelled",
        "failed"
    }:
        return {
            **state,
            "response": (
                "This conversation has ended. "
                "Please start a new conversation."
            )
        }

    input_state = {
        **state,
        "messages": [
            *state["messages"],
            HumanMessage(content=message)
        ]
    }

    result = await graph.ainvoke(input_state)

    result["messages"] = [
        *result["messages"],
        AIMessage(content=result["response"])
    ]

    return result