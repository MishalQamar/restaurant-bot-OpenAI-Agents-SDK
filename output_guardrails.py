from agents import Agent, output_guardrail, Runner, RunContextWrapper
from models import OutputGuardRailOutput, UserAccountContext
from agents import GuardrailFunctionOutput


output_guardrail_agent = Agent(
    name="Output Guardrail Agent",
    instructions="""
    You are the Output Guardrail Agent for a restaurant.
    You are responsible for ensuring that the output is related to the restaurant menu, ingredients, allergens, orders, reservations, or general questions about the restaurant.
    If the output is not related to the restaurant menu, ingredients, allergens, orders, reservations, or general questions about the restaurant, return a reason for the output guardrail.You should not help with requests that are not related to the restaurant menu, ingredients, allergens, orders, reservations, or general questions about the restaurant. You should be courteous and professional.Don't give any other information that is not related to the restaurant menu, ingredients, allergens, orders, reservations, or general questions about the restaurant.
    """,
    output_type=OutputGuardRailOutput,
)


@output_guardrail
async def off_topic_output_guardrail(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent,
    output: str,
):
    result = await Runner.run(output_guardrail_agent, output, context=wrapper.context)

    validation = result.final_output.is_off_topic
    triggered = validation is True

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=triggered,
    )
