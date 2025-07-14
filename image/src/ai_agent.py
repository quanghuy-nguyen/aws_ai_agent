import os
from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import Tool, StructuredTool
from langchain_openai import ChatOpenAI
from tools import process_multiple_images, list_images_in_folder, compare_count_values_to_reference
from tools import generate_full_report_from_processed_results

load_dotenv()

initial_message = """
You are an AI assistant that uses the following tools:

- list_images_in_folder
- process_multiple_images
- compare_count_values_to_reference
- generate_full_report_from_processed_results

Your goal is to help factory supervisors analyze production line image data.

### INSTRUCTIONS

To compare extracted count values with the reference standards:

1. Use `process_multiple_images` to extract values from the images.
2. This function will return a **JSON string** in the format:
    [{"line": "5 - 1", "count_values": [123456, 789012, ...]}, ...]
3. You must **pass this exact JSON string** to the `compare_count_values_to_reference` tool.
    Do NOT pass plain text or formatted summaries.
4. Once compared, summarize the good and bad machines per line.

To generate a full daily report:

1. Ensure that the input to `generate_full_report_from_processed_results` is also the **same JSON string** as above.
2. This tool will save the report as a .txt file and return the summary as text.

You MUST follow these data formats. Do not attempt to generate your own output format.
""".strip()




tools = [
    StructuredTool.from_function(
        name="list_images_in_folder",
        func=list_images_in_folder,
        description="Useful for when you need to list all images in a folder.",
    ),
    StructuredTool.from_function(
        name="process_multiple_images",
        func=process_multiple_images,
        description="Useful for when you need to extract data from images.",
    ),
    StructuredTool.from_function(
        name="compare_count_values_to_reference",
        func=compare_count_values_to_reference,
        description="Useful for when you need to compare count values from images to a reference number list.",
    ), 
    StructuredTool.from_function(
    func=generate_full_report_from_processed_results,
    name="generate_full_report_from_processed_results",
    description="Generate a full production report from all lines in processed result string"
    ),
]


prompt = hub.pull("hwchase17/structured-chat-agent")

llm = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))

agent = create_structured_chat_agent(llm=llm, tools=tools, prompt=prompt)

def get_agent_executor(memory: ConversationBufferMemory) -> AgentExecutor:
    return AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=True,
        memory=memory,  
        handle_parsing_errors=True,  # Handle any parsing errors gracefully
    )



def main():
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    memory.chat_memory.add_message(SystemMessage(content=initial_message))

    agent_executor = get_agent_executor(memory=memory)

    while True:
        user_input = input("User: ")
        if user_input.lower() == "exit":
            break

        memory.chat_memory.add_message(HumanMessage(content=user_input))

        response = agent_executor.invoke({"input": user_input})
        print("Bot:", response["output"])

        memory.chat_memory.add_message(AIMessage(content=response["output"]))



if __name__ == "__main__":
    main()