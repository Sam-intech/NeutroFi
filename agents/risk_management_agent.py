# risk_management_agent.py

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage


def create_risk_manager_agent(llm):
    def risk_manager_node(state):
        coin = state["coin"]
        current_date = state["trade_date"]

        decision = state.get("research_decision", "Hold").capitalize()
        confidence = state.get("research_confidence", 0.5)
        research_summary = state.get(
            "research_summary", "No research summary available."
        )

        # Time horizon forecasts fallback
        horizon_forecasts = state.get(
            "horizon_forecasts",
            {
                "short_term": {"recommendation": decision, "confidence": confidence},
                "medium_term": {"recommendation": decision, "confidence": confidence},
                "long_term": {"recommendation": decision, "confidence": confidence},
            },
        )

        # Normalize helper
        def norm(val):
            return val.capitalize() if isinstance(val, str) else val

        short_term_rec = norm(
            horizon_forecasts["short_term"].get("recommendation", decision)
        )
        short_term_conf = horizon_forecasts["short_term"].get("confidence", confidence)

        medium_term_rec = norm(
            horizon_forecasts["medium_term"].get("recommendation", decision)
        )
        medium_term_conf = horizon_forecasts["medium_term"].get(
            "confidence", confidence
        )

        long_term_rec = norm(
            horizon_forecasts["long_term"].get("recommendation", decision)
        )
        long_term_conf = horizon_forecasts["long_term"].get("confidence", confidence)

        # --- Risk Adjustment Rules ---
        risk_notes = []
        holder_action = decision
        buyer_action = decision
        holder_reason = ""
        buyer_reason = ""

        # -- Holder rules --
        if confidence < 0.55:
            holder_action = "Hold"
            holder_reason = "Confidence too low for action — defaulting to Hold."
            risk_notes.append(
                "Overall confidence < 0.55 — Holder action downgraded to Hold."
            )
        elif decision == "Buy" and confidence <= 0.7:
            holder_action = "Hold"
            holder_reason = (
                "Buy signal lacks strong confidence — set to Hold for caution."
            )
            risk_notes.append("Buy confidence ≤ 0.7 — Holder action adjusted to Hold.")
        elif decision == "Buy":
            holder_action = "Buy"
            holder_reason = "Strong enough research to proceed with Buy."
            risk_notes.append("Buy confirmed for holder based on overall research.")
        elif decision == "Sell":
            holder_action = "Sell"
            holder_reason = "Sell maintained to prevent downside."
            risk_notes.append("Sell preserved for downside protection.")
        else:
            holder_action = "Hold"
            holder_reason = "No major risk signals — maintaining Hold."

        # -- Buyer rules --
        if decision == "Buy" and confidence > 0.8 and long_term_conf > 0.75:
            buyer_action = "Buy"
            buyer_reason = (
                "High long-term confidence and overall conviction support new entry."
            )
            risk_notes.append("Strong long-term outlook — Buy allowed for new buyers.")
        else:
            buyer_action = "Hold"
            buyer_reason = (
                "New entry not advised unless confidence and long-term view are strong."
            )
            risk_notes.append(
                "New buyers advised to Hold unless long-term confidence is strong."
            )

        # --- Prompt for explanation generation ---
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"You are a risk management analyst. The trade date is {current_date}.",
                ),
                (
                    "user",
                    """
Evaluate the research summary and time horizon outlooks. Recommend actions for:
1. An existing holder of {coin}
2. A potential new buyer

Include:
- Rationale for each decision
- Confidence considerations
- Time horizon forecasts (short, medium, long)
- Risk notes summary

Coin: {coin}
Original Decision: {decision}
Overall Confidence: {confidence}

Horizon Forecasts:
Short-Term: {short_term_rec} ({short_term_conf})
Medium-Term: {medium_term_rec} ({medium_term_conf})
Long-Term: {long_term_rec} ({long_term_conf})

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
            short_term_rec=short_term_rec,
            short_term_conf=short_term_conf,
            medium_term_rec=medium_term_rec,
            medium_term_conf=medium_term_conf,
            long_term_rec=long_term_rec,
            long_term_conf=long_term_conf,
            summary=research_summary,
            risk_notes="\n".join(risk_notes),
        )

        chain = prompt | llm

        try:
            result = chain.invoke({"messages": state.get("messages", [])})
            return {
                "messages": [AIMessage(content=result.content)],
                "holder_recommendation": holder_action,
                "holder_reason": holder_reason,
                "buyer_recommendation": buyer_action,
                "buyer_reason": buyer_reason,
                "risk_notes": "\n".join(risk_notes),
                "final_recommendation": f"Holder: {holder_action}, Buyer: {buyer_action}",
            }
        except Exception as e:
            return {
                "messages": state.get("messages", []),
                "holder_recommendation": "Hold",
                "holder_reason": "Error during decision evaluation.",
                "buyer_recommendation": "Hold",
                "buyer_reason": "Error during decision evaluation.",
                "risk_notes": f"Error during risk check: {e}",
                "final_recommendation": "Holder: Hold, Buyer: Hold",
            }

    return risk_manager_node
