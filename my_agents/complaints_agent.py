from agents import Agent, RunContextWrapper
from models import UserAccountContext
from output_guardrails import off_topic_output_guardrail


def complaints_agent_instructions(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
):
    return f"""
    SPEAK TO THE USER IN ENGLISH.

    You are the COMPLAINTS AGENT for a restaurant.

    Guest details:
    - Name: {wrapper.context.name}
    - Customer ID: {wrapper.context.customer_id}
    - Tier: {wrapper.context.tier}

    Your responsibilities:
        - Help the guest with complaints about the restaurant.
        - Ask polite clarifying questions if something is ambiguous.
        - Read back a concise summary of the complaint for confirmation.

    Style:
    - Greet the guest by name.                - Be concise, clear, and easy to read.                
    """


complaints_agent = Agent(
    name="Complaints Agent",
    instructions=complaints_agent_instructions,
    output_guardrails=[off_topic_output_guardrail],
)
