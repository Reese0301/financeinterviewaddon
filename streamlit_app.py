import streamlit as st
import requests
import random
import time

# Define the API URL for the Interview Game model
API_URL_INTERVIEW_GAME = "https://flowise-9kx9.onrender.com/api/v1/prediction/cbf21cc5-8823-46a5-af90-66fca1c9ee32"

# Additional title with a smaller "Beta" tag
home_title = "Interview Game"  # Replace with the actual title you want to use

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

# List of randomized "thinking" messages
thinking_messages = [
    "Alex is Crunching the numbers…",
    "Alex: Try but you won't win.",
    "Evaluating responses, will you stand out?",
    "Checking with the HR team…",
    "The competition's heating up… recalculating strategies!",
    "Sending return offers.."
]

# Initialize session state for chat messages and resume if not already set
if "interview_game_messages" not in st.session_state:
    st.session_state.interview_game_messages = []
    st.session_state.interview_game_messages.append({
        "role": "assistant", 
        "content": "Welcome to the interview game! Ready to see how you stack up in a simulated interview against Alex?"
    })
if "resume" not in st.session_state:
    st.session_state.resume = ""  # Placeholder for resume content

# Sidebar for customizing the interview game and uploading resume
with st.sidebar:
    st.header("Customize Your Interview Game")
    question_types = {
        "Behavioral": st.checkbox("Behavioral", value=True),
        "Technical": st.checkbox("Technical", value=True),
        "Fit": st.checkbox("Fit", value=True),
        "Resume": st.checkbox("Resume (In Progress, may experience memory related issues.)")
    }
    
    # Resume text area and button for storing resume content
    if question_types["Resume"]:
        resume_text = st.text_area("Paste your resume here for personalize questions.")
        
        # Button to submit resume content
        if st.button("📄 Send Resume"):
            if resume_text.strip():  # Check if there is any text in the resume field
                st.session_state.resume = resume_text
                st.success("Resume sent successfully!")
                
                # Update system message to emphasize resume-based questions
                st.session_state.interview_game_messages.append({
                    "role": "system",
                    "content": "The user has uploaded their resume."
                })
            else:
                st.warning("No resume detected. Please paste your resume in the text area before sending.")

# Function to query the Interview Game API
def query_interview_game(context, prompt, question_types):
    # Construct type-specific instructions based on user selections
    types_instructions = " ".join(
        [f"Include {key} questions." for key, selected in question_types.items() if selected and key != "Resume"]
    )
    resume_text = st.session_state.resume
    if resume_text:
        types_instructions += "Generate interview questions regarding the user's resume contents and experiences. Use the information in the resume below to ask resume related interview questions. For example: In your resume, you mentioned...can you elaborate on..."
    
    # Prepare payload with specific instructions based on toggled question types
    payload = {
        "question": f"{context}\n\nUser Question: {prompt}\n\n{types_instructions}\nResume:\n{resume_text}"
    }

    #Debugging output to check the payload before sending
    #st.write("Sending payload:", payload)

    # Send request to API and get the response
    response = requests.post(API_URL_INTERVIEW_GAME, json=payload)
    if response.status_code == 200:
        return response.json().get("text", "Error: No response text")
    else:
        return f"Error: {response.status_code}"

# Display the chat history for the Interview Game
for message in st.session_state.interview_game_messages:
    role = message["role"]
    avatar_url = "https://github.com/Reese0301/GIS-AI-Agent/blob/main/JackIcon.png?raw=true" if role == "assistant" else "https://github.com/Reese0301/GIS-AI-Agent/blob/main/FoxUser.png?raw=true"
    
    with st.chat_message(role, avatar=avatar_url):
        st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("Answer here..."):
    st.session_state.interview_game_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="https://github.com/Reese0301/GIS-AI-Agent/blob/main/FoxUser.png?raw=true"):
        st.markdown(prompt)

    # Show thinking message while awaiting response
    thinking_message = random.choice(thinking_messages)
    thinking_placeholder = st.empty()
    thinking_placeholder.markdown(f"💭 **{thinking_message}**")

    # Prepare context by limiting to the last few messages
    CONTEXT_LIMIT = 6
    context = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state.interview_game_messages[-CONTEXT_LIMIT:]])

    # Query the Interview Game API
    response_content = query_interview_game(context, prompt, question_types)
    thinking_placeholder.empty()

    # Display Alex's response
    with st.chat_message("assistant", avatar="https://github.com/Reese0301/GIS-AI-Agent/blob/main/JackIcon.png?raw=true"):
        st.markdown(response_content)

    # Add Alex's response to chat history
    st.session_state.interview_game_messages.append({"role": "assistant", "content": response_content})
