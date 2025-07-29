import re
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage


def create_research_analyst_agent(llm):
    def research_analyst_node(state):
        coin = state["coin"]
        current_date = state["trade_date"]

        fundamentals = state.get(
            "fundamentals_report", "No fundamentals report available."
        )
        news = state.get("news_report", "No news report available.")
        sentiment = state.get("sentiment_report", "No sentiment report available.")
        technical = state.get("technical_report", "No technical report available.")

        combined_data = f"""
[FUNDAMENTALS]
{fundamentals}

[NEWS]
{news}

[SENTIMENT]
{sentiment}

[TECHNICAL]
{technical}
        """

        system_message = f"""
You are a senior crypto research analyst. Based on the following reports (fundamentals, news, sentiment, technical), produce a structured market view for {coin} as of {current_date}.

You MUST return:

1. A professional summary of the market outlook. Summarize each section in bullet points.
2. Short-Term (0–2 weeks) Recommendation: Buy, Hold, or Sell + Confidence score (0.0 to 1.0)
3. Medium-Term (2 weeks–2 months) Recommendation + Confidence
4. Long-Term (2+ months) Recommendation + Confidence
5. If already holding the coin, give advice using: Buy (Add), Hold, or Sell, AND include a short reason
6. If not holding the coin, give advice using: Buy, Hold, or Avoid, AND include a short reason

Your output must follow this format:

---
Market Summary:
• [Bullet 1]
• [Bullet 2]
...

Short-Term Recommendation: <Buy/Hold/Sell>, Confidence: <score>
Medium-Term Recommendation: <Buy/Hold/Sell>, Confidence: <score>
Long-Term Recommendation: <Buy/Hold/Sell>, Confidence: <score>

Existing Holder Advice: <Buy/Hold/Sell/Add> — Reason: <one-sentence reason>
New Investor Advice: <Buy/Hold/Avoid> — Reason: <one-sentence reason>
---

Be clear, structured, and concise.
        """

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_message.strip()),
                ("user", "{combined_data}"),
                MessagesPlaceholder(variable_name="messages"),
            ]
        ).partial(combined_data=combined_data)

        chain = prompt | llm

        try:
            result = chain.invoke({"messages": state["messages"]})
            content = result.content.strip()

            def extract_recommendation(label):
                match = re.search(
                    rf"{label} Recommendation:\s*(Buy|Hold|Sell)",
                    content,
                    re.IGNORECASE,
                )
                return match.group(1).capitalize() if match else "Hold"

            def extract_confidence(label):
                match = re.search(
                    rf"{label} Recommendation:.*?Confidence:\s*([0-1](?:\.\d+)?)",
                    content,
                    re.IGNORECASE,
                )
                return float(match.group(1)) if match else 0.5

            def extract_advice_with_reason(label, allowed_terms):
                pattern = (
                    rf"{label} Advice:\s*({'|'.join(allowed_terms)}).*?Reason:\s*(.+)"
                )
                match = re.search(pattern, content, re.IGNORECASE)
                decision = match.group(1).capitalize() if match else "Hold"
                reason = match.group(2).strip() if match else "Not specified."
                return decision, reason

            # Extract time-based decisions
            short_term = extract_recommendation("Short-Term")
            medium_term = extract_recommendation("Medium-Term")
            long_term = extract_recommendation("Long-Term")

            conf_short = extract_confidence("Short-Term")
            conf_medium = extract_confidence("Medium-Term")
            conf_long = extract_confidence("Long-Term")

            # Extract advice with reasons
            existing_holder_action, existing_holder_reason = extract_advice_with_reason(
                "Existing Holder", ["Buy", "Hold", "Sell", "Add"]
            )
            new_investor_action, new_investor_reason = extract_advice_with_reason(
                "New Investor", ["Buy", "Hold", "Avoid"]
            )

            # Set overall decision to long-term recommendation
            overall_decision = long_term
            overall_confidence = conf_long

            return {
                "messages": [AIMessage(content=content)],
                "research_summary": content,
                "research_decision": overall_decision,
                "research_confidence": overall_confidence,
                "short_term_decision": short_term,
                "short_term_confidence": conf_short,
                "medium_term_decision": medium_term,
                "medium_term_confidence": conf_medium,
                "long_term_decision": long_term,
                "long_term_confidence": conf_long,
                "existing_holder_advice": existing_holder_action,
                "existing_holder_reason": existing_holder_reason,
                "new_investor_advice": new_investor_action,
                "new_investor_reason": new_investor_reason,
            }

        except Exception as e:
            return {
                "messages": state.get("messages", []),
                "research_summary": f"Error: {str(e)}",
                "research_decision": "Hold",
                "research_confidence": 0.5,
                "short_term_decision": "Hold",
                "short_term_confidence": 0.5,
                "medium_term_decision": "Hold",
                "medium_term_confidence": 0.5,
                "long_term_decision": "Hold",
                "long_term_confidence": 0.5,
                "existing_holder_advice": "Hold",
                "existing_holder_reason": "Error extracting reason.",
                "new_investor_advice": "Hold",
                "new_investor_reason": "Error extracting reason.",
            }

    return research_analyst_node
