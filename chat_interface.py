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
    messages = client.beta.threads.messages.list(thread_id=thread.id).data
    ordered = messages[::-1]
    for message in ordered:
        print(message.content[0].text.value)
    return ordered[-1].content[0].text.value


def undo():
    messages = client.beta.threads.messages.list(thread_id=thread.id).data
    for message in messages:
        client.beta.threads.messages.delete(
            message_id=message.id, thread_id=thread.id,
        )
        if message.role == "user":
            break

def clear():
    global thread
    client.beta.threads.delete(thread_id=thread.id)
    thread = client.beta.threads.create()
    return [[None, "Hi, how can I help you?"]]

# def download_pdf():
#     return download("get_device_pdf", "868617060032986", "?start=&end=&dataType=")

def enable_button(chatbot):
    if chatbot == [] or chatbot == [[None, "Hi, how can I help you?"]]:
        return gr.Button(interactive=False), gr.Button(interactive=False)
    else:
        return gr.Button(interactive=True), gr.Button(interactive=True)

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
    undo_btn = gr.Button("Undo", size="sm", interactive=False)
    clear_btn = gr.Button("Clear", size="sm", interactive=False)
    with gr.ChatInterface(
        chat,
        title="Tag-N-Trac AI Assistant",
        chatbot=chatbot,
        retry_btn=None,
        undo_btn=undo_btn,
        clear_btn=clear_btn,
        examples=[
            "Show me alerts from my asset _ .",
            "Where is the device _ located?",
            "Get me sensor data for my asset _ .",
        ],
    ) as demo:
        pdf_btn = gr.Button("Download PDF", size="sm", interactive=False)
        undo_btn.click(undo)
        clear_btn.click(clear, outputs=chatbot)
        # pdf_btn.click(download_pdf)
        chatbot.change(enable_button, chatbot, [undo_btn, clear_btn])
    demo.launch(share=True)
