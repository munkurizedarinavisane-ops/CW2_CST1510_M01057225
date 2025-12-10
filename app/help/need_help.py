import streamlit as st
from google import genai

# -------------------------
# Gemini API Client Setup
# -------------------------
API_KEY = st.secrets["GEMINI"]["API_KEY"]
client = genai.Client(api_key=API_KEY)
MODEL_NAME = "gemini-2.5-flash"

# -------------------------
# Helper: Generate response from Gemini
# -------------------------
def generate_gemini_response(messages, model=MODEL_NAME):
    """
    messages: list of dicts with 'role' and 'content'
    Converts chat history to a single text prompt for Gemini 2.5 API
    """
    # Combine all messages into a single string
    prompt = ""
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        prompt += f"{role.upper()}: {content}\n"
    prompt += "ASSISTANT:"

    # Generate response
    response = client.models.generate_content(
        model=model,
        contents=prompt  # use contents, not messages
    )

    return response.text

# -------------------------
# Streamlit Page
# -------------------------
def show_need_help_page():
    st.title(" Need Help? — AI Assistant")
    st.write("Ask anything about the dashboard, cyber security, IT operations, datasets, or the system.")

    # Initialize chat history if missing or None
    if "help_messages" not in st.session_state or st.session_state.help_messages is None:
        st.session_state.help_messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert assistant helping users navigate a multi-domain intelligence dashboard. "
                    "Give clear, concise replies, tailored to the context of the platform."
                )
            }
        ]

    # Display chat history (skip system message)
    for msg in st.session_state.help_messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # User input
    prompt = st.chat_input("How can I help?")
    if prompt:
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Save user message
        st.session_state.help_messages.append({"role": "user", "content": prompt})

        # Generate AI response
        with st.spinner("Generating AI response..."):
            reply_text = generate_gemini_response(st.session_state.help_messages)

        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(reply_text)

        # Save assistant response
        st.session_state.help_messages.append({"role": "assistant", "content": reply_text})
