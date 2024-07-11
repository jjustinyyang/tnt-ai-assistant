import time
import json
import gradio as gr
from openai_assistant import client, assistant
from tnt_api_integration import get_function_output

thread = client.beta.threads.create()


def chat(user_input, chat_history):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_input
    )
    run = client.beta.threads.runs.create(
        thread_id=thread.id, assistant_id=assistant.id
    )
    while run.status not in ["completed", "failed", "requires_action"]:
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        print("responding to user input " + run.status)
    while run.status == "requires_action":
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        tool_outputs = []
        for tool_call in tool_calls:
            print(tool_call.function)
            function_output = json.dumps(get_function_output(tool_call.function))
            print(function_output)
            tool_outputs.append(
                {"tool_call_id": tool_call.id, "output": function_output}
            )
        run = client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs
        )
        while run.status not in ["completed", "failed", "requires_action"]:
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            print("function submission " + run.status)
    messages = list(client.beta.threads.messages.list(thread_id=thread.id))
    print(messages)
    return messages[0].content[0].text.value


def clear_chat():
    # thread = client.beta.threads.create()
    return [[None, "Hi, how can I help you?"]]


if __name__ == "__main__":
    chatbot = gr.Chatbot(
        value=[[None, "Hi, how can I help you?"]],
        height="70vh",
        show_copy_button=True,
        likeable=True,
        avatar_images=[
            "https://t3.ftcdn.net/jpg/05/53/79/60/360_F_553796090_XHrE6R9jwmBJUMo9HKl41hyHJ5gqt9oz.jpg",
            "https://mms.businesswire.com/media/20220125006080/en/1338748/22/Tag-N-Trac.jpg",
        ],
    )
    retry_btn = gr.Button("Retry", size="sm")
    undo_btn = gr.Button("Undo", size="sm")
    clear_btn = gr.Button("Clear", size="sm")
    with gr.ChatInterface(
        chat,
        title="Tag-N-Trac AI Assistant",
        chatbot=chatbot,
        retry_btn=retry_btn,
        undo_btn=undo_btn,
        clear_btn=clear_btn,
        examples=[
            "Show me alerts from my asset _ .",
            "Where is the device _ located?",
            "Get me sensor data for my asset _ .",
        ],
    ) as demo:
        clear_btn.click(clear_chat, outputs=chatbot)
    demo.launch(share=True)
