import streamlit as st
import google.generativeai as genai

# -------------------------
# App Configuration & Setup
# -------------------------
# Configure the page
st.set_page_config(
    page_title="AI Academic Assistant",
    page_icon="🎓",
    layout="centered"
)

# You provided an API key starting with 'AIzaSy', which indicates it's a Google Gemini API key.
# We will use the google-generativeai SDK instead of OpenAI for this reason.
API_KEY = "AIzaSyAw0rXEAAC1m2NwEpGI9Wbm1EexKhL5JS0"

try:
    genai.configure(api_key=API_KEY)
    # Using gemini-2.5-flash as it is supported by the provided API key
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    st.error(f"Failed to initialize the AI model. Error: {e}")

# -------------------------
# Frontend: UI & Styling
# -------------------------
st.title("🎓 AI Academic Assistant")
st.markdown("Your personal AI tutor. I can help answer questions, summarize topics, create quizzes, and plan your study schedule.")

# Sidebar
with st.sidebar:
    st.header("🛠️ Tools & Features")
    st.write("Select an operation mode:")
    
    # Selection box for features
    mode = st.selectbox(
        "Choose an action:",
        ["General Chat", "Generate Notes", "Create Quiz", "Study Plan"]
    )
    
    st.divider()
    st.caption("Tip: Pick a tool above and type your topic in the chat below! To reset the chat, refresh the page.")

# -------------------------
# Backend Logic & History
# -------------------------
# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -------------------------
# User Input Processing
# -------------------------
# Streamlit's chat_input automatically creates an input box and a send button
if prompt := st.chat_input("Enter your topic or question here..."):
    
    # 1. Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # 2. Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 3. Create a customized prompt based on the chosen mode from the sidebar
    if mode == "Generate Notes":
        system_prompt = f"Act as an expert academic tutor. Generate short, clear, and concise study notes on the following topic: '{prompt}'. Format the notes well using Markdown, bullet points, and bold text for key terms."
    elif mode == "Create Quiz":
        system_prompt = f"Act as an academic examiner. Create a 5-question multiple choice quiz based on the following topic: '{prompt}'. Include clear options for each question (A, B, C, D) and provide the correct answers clearly at the bottom."
    elif mode == "Study Plan":
        system_prompt = f"Act as a professional academic planner. Generate a highly structured, day-by-day, 7-day study plan to master the following topic: '{prompt}'. Make it realistic, actionable, and formatted nicely."
    else:
        system_prompt = f"Act as a helpful and knowledgeable academic assistant. Answer the following query accurately and clearly: '{prompt}'"

    # 4. Generate AI response and stream/display it
    with st.chat_message("assistant"):
        try:
            # Display a spinner while waiting for the API
            with st.spinner("Generating response..."):
                response = model.generate_content(system_prompt)
                full_response = response.text
                
            # Render the response
            st.markdown(full_response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            # Handle API errors gracefully
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower():
                st.error("⏳ **API Quota Exceeded:** You have reached the rate limit for your Gemini API key's free tier (often 15 requests per minute). Please wait about 1 minute and try again!")
            else:
                error_msg = f"Sorry, I encountered an error. Please try again later. \n\n**Details:** {error_str}"
                st.error(error_msg)
