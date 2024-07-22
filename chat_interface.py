import json
import time
import gradio as gr
from openai_assistant import client, assistant
from tnt_api_integration import get_function_output

# Create a new thread for the assistant
thread = client.beta.threads.create()

def get_assistant_response(user_input, chat_history):
    """
    This function gets the assistant's response to the user's input and updates the chat history.
    
    Args:
    - user_input: A dictionary containing the user's input.
    - chat_history: A list of previous chat messages.

    Returns:
    - A tuple containing the updated user input (cleared), updated chat history, and the download button.
    """
    show_download_btn = False

    # Create a message with the user's input
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_input["text"]
    )
    
    # Run the assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id, assistant_id=assistant.id
    )

    # Wait for the run to complete or fail
    while run.status not in ["completed", "failed", "requires_action"]:
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        print("responding to user input " + run.status)
    
    # Handle required actions
    while run.status == "requires_action":
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        tool_outputs = []
        
        # Process each tool call
        for tool_call in tool_calls:
            print(tool_call.function)
            if tool_call.function.name == "get_report_pdf":
                show_download_btn, function_output = get_function_output(
                    tool_call.function
                )
            else:
                function_output = json.dumps(get_function_output(tool_call.function))
            print(function_output)
            tool_outputs.append(
                {"tool_call_id": tool_call.id, "output": function_output}
            )
        
        # Submit tool outputs and wait for the run to complete or fail
        run = client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs
        )
        while run.status not in ["completed", "failed", "requires_action"]:
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            print("function submission " + run.status)

    # Create a download button if a PDF is available
    download_btn = gr.DownloadButton(value="report.pdf", visible=show_download_btn)

    # Retrieve the list of messages from the thread and reverse the order
    messages = client.beta.threads.messages.list(thread_id=thread.id).data
    ordered = messages[::-1]
    for message in ordered:
        print(message.content[0].text.value)
    
    # Append the assistant's response to the chat history
    assistant_response = ordered[-1].content[0].text.value
    chat_history.append([user_input["text"], assistant_response])
    print(chat_history)
    
    return {"text": "", "files": []}, chat_history, download_btn

if __name__ == "__main__":
    def undo_prev(chat_history):
        """
        This function undoes the previous user input and assistant response.
        
        Args:
        - chat_history: A list of previous chat messages.

        Returns:
        - A tuple containing the previous user input and the updated chat history.
        """
        messages = client.beta.threads.messages.list(thread_id=thread.id).data
        for message in messages:
            client.beta.threads.messages.delete(
                message_id=message.id,
                thread_id=thread.id,
            )
            if message.role == "user":
                break
        return chat_history[:-1], {"text": chat_history[-1][0], "files": []}, gr.DownloadButton(visible=False)

    def clear_chat():
        """
        This function clears the chat history by deleting the current thread and creating a new one.

        Returns:
        - A list with the initial assistant greeting.
        """
        global thread
        client.beta.threads.delete(thread_id=thread.id)
        thread = client.beta.threads.create()
        return [[None, "Hi, how can I help you?"]], gr.DownloadButton(visible=False)

    def enable_buttons(chatbot):
        """
        This function enables or disables the undo and clear buttons based on the chat history.

        Args:
        - chatbot: The current chat history.

        Returns:
        - A tuple containing the undo and clear buttons with updated interactivity.
        """
        if chatbot == [] or chatbot == [[None, "Hi, how can I help you?"]]:
            return gr.Button(interactive=False), gr.Button(interactive=False)
        else:
            return gr.Button(interactive=True), gr.Button(interactive=True)

    # Build the Gradio interface
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

        # Set up event handlers
        user_input.submit(
            get_assistant_response,
            inputs=[user_input, chatbot],
            outputs=[user_input, chatbot, download_btn],
        )

        chatbot.change(
            enable_buttons, chatbot, [undo_btn, clear_btn], scroll_to_output=True
        )
        undo_btn.click(undo_prev, inputs=chatbot, outputs=[chatbot, user_input, download_btn])
        clear_btn.click(clear_chat, outputs=[chatbot, download_btn])
    demo.launch(share=True)
