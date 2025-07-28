from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import ToolMessage
import json


def create_fundamentals_analyst(llm, toolkit):
    def fundamentals_analyst_node(state):
        coin = state["coin"]
        current_date = state["trade_date"]

        tools = [toolkit.get_crypto_fundamentals]

        # print(f"[🧪] Running fundamentals analysis for: {coin}")

        # System message for report generation
        system_message = (
            f"You are a crypto fundamentals analyst. You have called the 'get_crypto_fundamentals' tool to fetch data about {coin} "
            f"(e.g., market cap, supply, listings, token platforms). Use the provided tool output to write a detailed report. "
            f"Include a markdown table summarizing key metrics (e.g., Market Cap, Circulating Supply, Total Supply, Exchange Listings Count). "
            f"Provide a professional summary of the coin's fundamentals, highlighting its market position and potential. "
            f"If the tool output indicates an error or no data, state: 'No fundamental data available for {coin}.' "
            f"Example output:\n"
            f"## Fundamentals Report for {coin}\n"
            f"[Analysis of market cap, supply, etc. based on data]\n"
            f"| Metric | Value |\n|--------|-------|\n| Market Cap (USD) | $1,234,567,890 |\n| Circulating Supply | 18,900,000 |\n| Total Supply | 21,000,000 |\n| Exchange Listings Count | 150 |\n\n"
            f"**Summary**: [Summary of the coin's fundamentals and market position].\n"
            f"Do not call the 'get_crypto_fundamentals' tool again; use the provided tool output."
        )

        # Prompt for first LLM call (tool-calling)
        tool_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a crypto analyst AI.\n"
                    "Immediately call the 'get_crypto_fundamentals' tool to fetch data for {coin}.\n"
                    "Do not ask for clarification or additional input; use the provided coin symbol.\n"
                    "Date: {current_date}.",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        ).partial(current_date=current_date, coin=coin)

        # Prompt for second LLM call (report generation, no tools)
        report_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    system_message,
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        ).partial(current_date=current_date, coin=coin)

        # Chains
        tool_chain = tool_prompt | llm.bind_tools(tools)
        report_chain = report_prompt | llm

        # STEP 1: First LLM call to trigger tool
        result = tool_chain.invoke(state["messages"])
        # print(f"[🧪] First result.tool_calls: {result.tool_calls}")

        # STEP 2: If tools were triggered, call them and re-run LLM
        if result.tool_calls:
            tool_outputs = []
            for tool_call in result.tool_calls:
                tool_name = tool_call["name"]
                args = tool_call["args"]
                # print(f"[🧪] Calling tool: {tool_name} with args: {args}")
                tool_func = getattr(toolkit, tool_name)
                tool_output = tool_func.invoke(args)
                # print(f"[🧪] Tool output: {tool_output}")
                # Ensure tool_output is valid
                if not tool_output or tool_output.strip() == "":
                    tool_output = json.dumps({"error": f"No data available for {coin}"})
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
            # print(f"[🧪] Messages before second invoke: {state['messages']}")

            # STEP 3: Re-run LLM with report prompt (no tools)
            try:
                input_dict = {"messages": state["messages"]}
                # print(f"[🧪] Input to report_chain: {input_dict}")
                result = report_chain.invoke(input_dict)
                # print(f"[🧪] Second LLM result: {result}")
            except Exception as e:
                # print(f"[🧪] Error invoking LLM: {e}")
                return {
                    "messages": state["messages"],
                    "fundamentals_report": f"Error: Failed to generate report due to {str(e)}",
                }

            # Check for unexpected tool calls
            if result.tool_calls:
                # print(
                #     f"[🧪] Warning: Unexpected tool calls in second LLM call: {result.tool_calls}"
                # )
                # Fallback: Retry with simplified messages
                simplified_messages = [
                    state["messages"][0],  # Original HumanMessage
                    tool_outputs[0],  # ToolMessage
                ]
                try:
                    input_dict = {"messages": simplified_messages}
                    # print(f"[🧪] Retry input to report_chain: {input_dict}")
                    result = report_chain.invoke(input_dict)
                    # print(f"[🧪] Retry LLM result: {result}")
                except Exception as e:
                    # print(f"[🧪] Retry failed: {e}")
                    return {
                        "messages": state["messages"],
                        "fundamentals_report": f"Error: Failed to generate report on retry due to {str(e)}",
                    }

        report = result.content or f"No fundamental data available for {coin}."
        # print(f"[🧪] Final report: {report}")

        return {
            "messages": [result],
            "fundamentals_report": report,
        }

    return fundamentals_analyst_node
