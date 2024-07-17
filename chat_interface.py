import json
import time
import gradio as gr
from openai_assistant import client, assistant
from tnt_api_integration import get_function_output

thread = client.beta.threads.create()


def get_assistant_response(user_input, chat_history):
    show_download_btn = False

    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_input["text"]
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
            if tool_call.function.name == "get_device_pdf":
                show_download_btn, function_output = get_function_output(
                    tool_call.function
                )
            else:
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

    download_btn = gr.DownloadButton(value="device_info.pdf", visible=show_download_btn)

    messages = client.beta.threads.messages.list(thread_id=thread.id).data
    ordered = messages[::-1]
    for message in ordered:
        print(message.content[0].text.value)
    # chat_history.append([user_input["text"], None])
    # new_query = False
    # for message in ordered:
    #     if new_query:
    #         chat_history.append([None, message.content[0].text.value])
    #         continue
    #     elif message.content[0].text.value == user_input["text"]:
    #         new_query = True
    assistant_response = ordered[-1].content[0].text.value
    chat_history.append([user_input["text"], assistant_response])
    print(chat_history)
    return {"text": "", "files": []}, chat_history, download_btn


if __name__ == "__main__":

    def undo_prev(chat_history):
        messages = client.beta.threads.messages.list(thread_id=thread.id).data
        for message in messages:
            client.beta.threads.messages.delete(
                message_id=message.id,
                thread_id=thread.id,
            )
            if message.role == "user":
                break
        return {"text": chat_history[-1][0], "files": []}, chat_history[:-1]

    def clear_chat():
        global thread
        client.beta.threads.delete(thread_id=thread.id)
        thread = client.beta.threads.create()
        return [[None, "Hi, how can I help you?"]]

    def enable_buttons(chatbot):
        if chatbot == [] or chatbot == [[None, "Hi, how can I help you?"]]:
            return gr.Button(interactive=False), gr.Button(interactive=False)
        else:
            return gr.Button(interactive=True), gr.Button(interactive=True)

    with gr.Blocks() as demo:
        title = gr.Markdown("## Tag-N-Trac AI Assistant")
        chatbot = gr.Chatbot(
            value=[[None, "Hi, how can I help you?"]],
            height="59vh",
            show_copy_button=True,
            likeable=True,
            avatar_images=[
                "https://t3.ftcdn.net/jpg/05/53/79/60/360_F_553796090_XHrE6R9jwmBJUMo9HKl41hyHJ5gqt9oz.jpg",
                "https://mms.businesswire.com/media/20220125006080/en/1338748/22/Tag-N-Trac.jpg",
            ],
        )
        download_btn = gr.DownloadButton(label="Download PDF", size="sm", visible=False)
        user_input = gr.MultimodalTextbox(show_label=False, autofocus=True)
        with gr.Row():
            undo_btn = gr.Button("Undo", size="sm", interactive=False)
            clear_btn = gr.Button("Clear", size="sm", interactive=False)
        examples = gr.Examples(
            examples=[
                {"text": "Show me alerts from my asset _ ."},
                {"text": "Where is the device _ located?"},
                {"text": "Get me sensor data for my asset _ ."},
            ],
            inputs=user_input,
        )

        user_input.submit(
            get_assistant_response,
            inputs=[user_input, chatbot],
            outputs=[user_input, chatbot, download_btn],
        )

        chatbot.change(
            enable_buttons, chatbot, [undo_btn, clear_btn], scroll_to_output=True
        )
        undo_btn.click(undo_prev, inputs=chatbot, outputs=[user_input, chatbot])
        clear_btn.click(clear_chat, outputs=chatbot)
    demo.launch()
