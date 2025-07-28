# research_analyst_agent.py

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
You are a crypto research analyst. Based on the following reports from different analysts (fundamentals, news, sentiment, technical), synthesize a unified market view.

Your output must include:
1. A professional summary of the market outlook for {coin}
2. A recommended action: Buy, Hold, or Sell
3. A confidence score between 0.0 and 1.0 on the decision.

Be clear and structured.
        """

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_message),
                ("user", "{combined_data}"),
                MessagesPlaceholder(variable_name="messages"),
            ]
        ).partial(combined_data=combined_data)

        chain = prompt | llm

        try:
            result = chain.invoke({"messages": state["messages"]})
            content = result.content

            # Use regex to extract decision and confidence robustly
            decision_match = re.search(
                r"\b(Decision|Recommendation):?\s*(Buy|Hold|Sell)\b",
                content,
                re.IGNORECASE,
            )
            confidence_match = re.search(
                r"\bConfidence\s*(Score)?[:=\-]?\s*([0-1](?:\.\d+)?)\b",
                content,
                re.IGNORECASE,
            )

            decision = (
                decision_match.group(2).capitalize() if decision_match else "Hold"
            )
            confidence = float(confidence_match.group(2)) if confidence_match else 0.5

            return {
                "messages": [AIMessage(content=content)],
                "research_summary": content,
                "research_decision": decision,
                "research_confidence": confidence,
            }

        except Exception as e:
            return {
                "messages": state.get("messages", []),
                "research_summary": f"Error: {str(e)}",
                "research_decision": "Hold",
                "research_confidence": 0.5,
            }

    return research_analyst_node
