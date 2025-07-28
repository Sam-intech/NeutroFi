from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage


def create_risk_manager_agent(llm):
    def risk_manager_node(state):
        coin = state["coin"]
        current_date = state["trade_date"]

        decision = state.get("research_decision", "Hold")
        confidence = state.get("research_confidence", 0.5)
        research_summary = state.get(
            "research_summary", "No research summary available."
        )

        # Risk decision logic
        risk_notes = []
        adjusted_decision = decision

        if confidence < 0.55:
            adjusted_decision = "Hold"
            risk_notes.append("Confidence below 0.55 — downgrading to Hold.")
        elif decision == "Buy" and confidence < 0.7:
            adjusted_decision = "Hold"
            risk_notes.append("Buy confidence below 0.7 — adjusting to Hold.")
        elif decision == "Buy" and confidence >= 0.7:
            adjusted_decision = "Buy"
            risk_notes.append("Buy confirmed with sufficient confidence.")
        elif decision == "Sell":
            risk_notes.append("Sell preserved for downside protection.")
        else:
            risk_notes.append("Hold maintained with moderate confidence.")

        # Construct explanation prompt
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"You are a risk management analyst. The trade date is {current_date}.",
                ),
                (
                    "user",
                    """
You will review a research summary and explain whether the decision should be adjusted due to risk concerns.

Coin: {coin}
Original Decision: {decision}
Confidence: {confidence}

Research Summary:
{summary}

Risk Notes:
{risk_notes}
                    """,
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        ).partial(
            coin=coin,
            decision=decision,
            confidence=confidence,
            summary=research_summary,
            risk_notes="\n".join(risk_notes),
        )

        chain = prompt | llm

        try:
            result = chain.invoke({"messages": state["messages"]})
            return {
                "messages": [AIMessage(content=result.content)],
                "risk_adjusted_decision": adjusted_decision,
                "risk_notes": "\n".join(risk_notes),
                "final_recommendation": adjusted_decision,
            }
        except Exception as e:
            return {
                "messages": state.get("messages", []),
                "risk_adjusted_decision": "Hold",
                "risk_notes": f"Error during risk check: {e}",
                "final_recommendation": "Hold",
            }

    return risk_manager_node
