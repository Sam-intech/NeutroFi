# agents/social_media_agent.py

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import ToolMessage


def create_sentiment_analyst(llm, toolkit):
    def sentiment_analyst_node(state):
        coin = state["coin"]
        current_date = state["trade_date"]

        tools = [toolkit.get_reddit_sentiment_posts]

        print(f"[🧪] Running sentiment analysis for: {coin}")

        system_message = (
            f"You are a social media sentiment analyst. You have called the 'get_reddit_sentiment_posts' tool to fetch recent Reddit posts related to {coin}. "
            f"The tool output is provided in the messages. Classify each post as Positive (e.g., optimistic, bullish), Negative (e.g., critical, bearish), or Neutral (e.g., factual, no strong opinion). "
            f"Provide a markdown table with columns: Post (short excerpt, max 50 characters), Sentiment, Reason. "
            f"Summarize the overall market mood (e.g., Bullish, Bearish, Neutral). "
            f"If the tool output is 'No recent posts found for this coin.', return a report stating:\n"
            f"| Post | Sentiment | Reason |\n|------|-----------|--------|\n| No posts found | Neutral | No recent posts available |\n\n**Summary**: No recent posts found for {coin}. Consider checking other sources like X or news articles.\n"
            f"Example output:\n"
            f"| Post | Sentiment | Reason |\n|------|-----------|--------|\n| Bitcoin to the moon! | Positive | Optimistic about price |\n| BTC is crashing | Negative | Bearish sentiment |\n\n**Summary**: Mixed sentiment with cautious outlook.\n"
            f"Do not call the 'get_reddit_sentiment_posts' tool again; use the provided tool output to generate the report."
        )

        # Prompt for first LLM call (with tool-calling)
        tool_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI sentiment analyst.\n"
                    "You have access to the following tools: {tool_names}.\n"
                    "Use the 'get_reddit_sentiment_posts' tool to fetch Reddit posts for {coin}.\n"
                    "Date: {current_date}.",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        ).partial(
            current_date=current_date,
            tool_names=", ".join([tool.name for tool in tools]),
            coin=coin,
        )

        # Prompt for second LLM call (without tool-calling)
        report_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    system_message,
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        ).partial(current_date=current_date, coin=coin)

        # Chain for first call (with tools)
        tool_chain = tool_prompt | llm.bind_tools(tools)

        # Chain for second call (no tools to prevent re-triggering)
        report_chain = report_prompt | llm

        # STEP 1: First LLM call triggers tool
        result = tool_chain.invoke(state["messages"])
        print("[🧪] First result.tool_calls:", result.tool_calls)

        # STEP 2: If tools were triggered, call them and re-run LLM
        if result.tool_calls:
            tool_outputs = []
            for tool_call in result.tool_calls:
                tool_name = tool_call["name"]
                args = tool_call["args"]
                print(f"[🧪] Calling tool: {tool_name} with args: {args}")
                tool_func = getattr(toolkit, tool_name)
                tool_output = tool_func.invoke(args)
                print(f"[🧪] Tool output: {tool_output}")
                # Ensure tool_output is not empty
                if not tool_output or tool_output.strip() == "":
                    tool_output = "No recent posts found for this coin."
                # Wrap tool output as ToolMessage
                tool_outputs.append(
                    ToolMessage(
                        content=tool_output,
                        tool_call_id=tool_call["id"],
                        name=tool_name,
                    )
                )

            state["messages"].append(result)  # Append tool_call (AIMessage)
            state["messages"].append(tool_outputs[0])  # Append ToolMessage

            # Log messages before second invoke
            print(f"[🧪] Messages before second invoke: {state['messages']}")

            # STEP 3: Re-run LLM with report prompt (no tools)
            try:
                result = report_chain.invoke(state["messages"])
                print(f"[🧪] Second LLM result: {result}")
            except Exception as e:
                print(f"[🧪] Error invoking LLM: {e}")
                return {
                    "messages": state["messages"],
                    "sentiment_report": f"Error: Failed to generate report due to {str(e)}",
                }

            # Check for unexpected tool calls
            if result.tool_calls:
                print(
                    f"[🧪] Warning: Unexpected tool calls in second LLM call: {result.tool_calls}"
                )
                # Fallback: Retry with simplified messages
                simplified_messages = [
                    state["messages"][0],  # Original HumanMessage
                    tool_outputs[0],  # ToolMessage
                ]
                try:
                    result = report_chain.invoke(simplified_messages)
                    print(f"[🧪] Retry LLM result: {result}")
                except Exception as e:
                    print(f"[🧪] Retry failed: {e}")
                    return {
                        "messages": state["messages"],
                        "sentiment_report": f"Error: Failed to generate report on retry due to {str(e)}",
                    }

        report = result.content or "⚠️ No report generated."
        print(f"[🧪] Final report: {report}")

        return {
            "messages": [result],
            "sentiment_report": report,
        }

    return sentiment_analyst_node
