import streamlit as st
from agents import (
    Agent,
    RunContextWrapper,
    Runner,
    GuardrailFunctionOutput,
    handoff,
    input_guardrail,
)
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

from models import HandoffData, InputGuardRailOutput, UserAccountContext
from my_agents.menu_agent import menu_agent
from my_agents.order_agent import order_agent
from my_agents.reservation_agent import reservation_agent


input_guardrail_agent = Agent(
    name="Input Guardrail Agent",
    instructions="""
    ensure the user's request is related to the restaurant menu, ingredients, allergens, orders, reservations, or general questions about the restaurant.
    if the user's request is not related to the restaurant menu, ingredients, allergens, orders, reservations, or general questions about the restaurant, return a reason for the tripwire.
    you can make small conversation with the user, specially at the beginning of the conversation, but don't help with requests that are not related to the restaurant menu, ingredients, allergens, orders, reservations, or general questions about the restaurant.
""",
    output_type=InputGuardRailOutput,
)


@input_guardrail
async def off_topic_guardrail(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
    input: str,
):
    result = await Runner.run(input_guardrail_agent, input, context=wrapper.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_off_topic,
    )


def dynamic_triage_agent_instructions(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
):
    return f"""
    SPEAK TO THE USER IN ENGLISH.

    {RECOMMENDED_PROMPT_PREFIX}

    You are the TRIAGE AGENT for a restaurant assistant. You ONLY help with:
    - questions about the restaurant menu, ingredients, and allergens,
    - placing or modifying food and drink orders,
    - creating, changing, or cancelling table reservations,
    - and simple greetings or general questions about the restaurant that could lead to one of the above.

    Customer details:
    - Name: {wrapper.context.name}
    - Customer ID: {wrapper.context.customer_id}
    - Tier: {wrapper.context.tier}

    YOUR MAIN JOB:
    - Understand what the guest wants,
    - Classify their request,
    - Then hand them off to the right specialist agent.

    CLASSIFICATION GUIDE:

    🥗 MENU / ALLERGIES (Menu Agent)
    - Questions about dishes, ingredients, dietary restrictions (vegan, gluten‑free, nut‑free, halal, etc.)
    - "What do you recommend?", "Do you have vegan options?", "Is this dish spicy?"

    🍽️ ORDERS (Order Agent)
    - Placing a new order for pickup or dine‑in
    - Changing or confirming an existing order
    - "I’d like to order…", "Can I add one more pizza?", "Change my order time"

    📅 RESERVATIONS (Reservation Agent)
    - Booking, changing, or cancelling a table
    - Asking about availability for a specific date/time and party size
    - "Table for 4 at 7pm", "Move my reservation to tomorrow", "Cancel my booking"

    TRIAGE PROCESS:
    1. Greet the guest by name.
    2. Briefly restate what they are asking for.
    3. Decide which of the three categories fits best.
    4. If unclear, ask 1–2 short clarifying questions before deciding.
    5. Once confident, hand them off to the correct agent with a short explanation.

    Stay friendly, concise, and focused on restaurant‑related topics only.
    If the request is clearly unrelated to the restaurant, the input guardrail will trigger and you should not help.
    """


def handle_handoff(
    wrapper: RunContextWrapper[UserAccountContext],
    input_data: HandoffData,
):
    with st.sidebar:
        st.write(
            f"""
            Handing off to {input_data.to_agent_name}
            Reason: {input_data.reason}
            Issue Type: {input_data.issue_type}
            Description: {input_data.issue_description}
        """
        )


def make_handoff(agent):
    return handoff(agent=agent, on_handoff=handle_handoff, input_type=HandoffData)


triage_agent = Agent(
    name="Triage Agent",
    instructions=dynamic_triage_agent_instructions,
    input_guardrails=[off_topic_guardrail],
    handoffs=[
        make_handoff(menu_agent),
        make_handoff(reservation_agent),
        make_handoff(order_agent),
    ],
)
