import streamlit as st
import requests
import random

API_URL_INTERVIEW_GAME = "https://flowise-9kx9.onrender.com/api/v1/prediction/cbf21cc5-8823-46a5-af90-66fca1c9ee32"

home_title = "Interview Game"

st.markdown(
    f"""<h1 style='display: inline;'>{home_title} <span style='color:#2E9BF5; font-size: 0.6em;'>Beta</span></h1>""",
    unsafe_allow_html=True
)

st.markdown(
    """
    ---
    Welcome to the Interview Game! This is a competitive interview experience where you go head to head with Alex to answer
    investment banking interview questions under simulated high-stakes conditions. See how you stack up and learn as you go.
    
    - 💬 Answer each question as you would in a real interview.
    - 🏆 A winner will be decided for every round. Feedback will be provided.
    - 📈 Track your progress and improve your responses. Practice makes perfect.
    
    Let's begin!
    """
)

thinking_messages = [
    "Alex is Crunching the numbers…",
    "Evaluating responses, will you stand out?",
    "Checking with the HR team…",
]

# Initialize session state for chat messages, resume, and question tracking
if "interview_game_messages" not in st.session_state:
    st.session_state.interview_game_messages = [
        {"role": "assistant", "content": "Welcome! Ready to challenge yourself and improve your interview skills?"}
    ]
if "resume" not in st.session_state:
    st.session_state.resume = ""
if "asked_questions" not in st.session_state:
    st.session_state.asked_questions = set()  # Store unique questions to avoid repetition

# Sidebar for customization
with st.sidebar:
    st.header("Customize Your Interview Game")
    question_types = {
        "Behavioral": st.checkbox("Behavioral", value=True),
        "Technical": st.checkbox("Technical", value=True),
        "Fit": st.checkbox("Fit", value=True),
        "Resume": st.checkbox("Resume (for personalized questions)")
    }

    if question_types["Resume"]:
        resume_text = st.text_area("Paste your resume here.")
        if st.button("📄 Send Resume"):
            if resume_text.strip():
                st.session_state.resume = resume_text
                st.success("Resume sent successfully!")
                st.session_state.interview_game_messages.append({
                    "role": "system",
                    "content": "Resume uploaded."
                })
            else:
                st.warning("No resume detected. Paste your resume and try again.")

# Function to query the Interview Game API
def query_interview_game(context, prompt, question_types):
    # Construct instructions based on selected question types
    types_instructions = " ".join(
        [f"Include {key} questions." for key, selected in question_types.items() if selected and key != "Resume"]
    )
    resume_text = st.session_state.resume
    if resume_text:
        types_instructions += "Generate questions based on unique experiences from the resume."

    # Prepare payload with tracked questions to reduce repeats
    payload = {
        "question": f"{context}\n\nUser Question: {prompt}\n\n{types_instructions}\nResume:\n{resume_text}",
        "asked_questions": list(st.session_state.asked_questions)  # Send list of asked questions to API
    }

    #Debugging output to check the payload before sending
    #st.write("Sending payload:", payload)
    
    response = requests.post(API_URL_INTERVIEW_GAME, json=payload)
    if response.status_code == 200:
        return response.json().get("text", "Error: No response text")
    else:
        return f"Error: {response.status_code}"

# Display chat history
for message in st.session_state.interview_game_messages:
    role = message["role"]
    avatar_url = (
        "https://github.com/Reese0301/GIS-AI-Agent/blob/main/JackIcon.png?raw=true"
        if role == "assistant" else
        "https://github.com/Reese0301/GIS-AI-Agent/blob/main/FoxUser.png?raw=true"
    )
    with st.chat_message(role, avatar=avatar_url):
        st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("Answer here..."):
    st.session_state.interview_game_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="https://github.com/Reese0301/GIS-AI-Agent/blob/main/FoxUser.png?raw=true"):
        st.markdown(prompt)

    thinking_message = random.choice(thinking_messages)
    thinking_placeholder = st.empty()
    thinking_placeholder.markdown(f"💭 **{thinking_message}**")

    CONTEXT_LIMIT = 6
    context = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state.interview_game_messages[-CONTEXT_LIMIT:]])

    # Query the Interview Game API
    response_content = query_interview_game(context, prompt, question_types)
    thinking_placeholder.empty()

    # Display Alex's response and track the question to avoid repetition
    with st.chat_message("assistant", avatar="https://github.com/Reese0301/GIS-AI-Agent/blob/main/JackIcon.png?raw=true"):
        st.markdown(response_content)

    # Save Alex's response and track it to avoid repetition
    st.session_state.interview_game_messages.append({"role": "assistant", "content": response_content})
    st.session_state.asked_questions.add(response_content)  # Add to asked questions set to avoid repeats
