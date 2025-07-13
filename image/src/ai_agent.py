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
You are an AI assistant that uses three tools:

- list_images_in_folder
- process_multiple_images
- compare_count_values_to_reference
- generate_full_report_from_processed_results

**To compare values from one line to the reference, you must:
1. Use `process_multiple_images` to get the values for each line;
2. Filter the result to find the correct line;
3. Format the data as JSON like: E.g: [{"line":"5 - 1", "count_values": [...]}];
4. Pass that JSON string into the `compare_count_values_to_reference` tool.
5. Make a conclusion at the end.

**To make a report for today's management, you can use the `generate_report_for_line_comparison` tool 
with the line label and processed results string for all the lines. Remember to make a conclusion at the end of the report.

You must NOT ask the user to provide the reference values, they are already built-in.
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

llm = ChatOpenAI(model="gpt-4o")

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