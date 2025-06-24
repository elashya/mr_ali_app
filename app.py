# app.py
import streamlit as st
from openai import OpenAI
#from dotenv import load_dotenv
import os
import time
import random

# === Load API Key ===
#load_dotenv()
#OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
ASSISTANT_ID = "asst_CIL8hS7ZusGwpdXdS6eB0zAr"  # Replace with your Assistant ID

client = OpenAI(api_key=OPENAI_API_KEY)

# === Page Config ===
st.set_page_config(page_title="Mr. Ali's Writing Coach", layout="centered")
st.title("✍️ Mr. Ali – Writing Coach for Mohamad")

# === Themes ===
themes = {
    "Fiction": "a fun or imaginative story (e.g., magic, adventure, mystery)",
    "Non-fiction": "a real story, opinion, or personal reflection",
    "Creative Writing": "something like a poem, comic scene, diary entry, or what-if idea"
}

# === Session State Initialization ===
if "challenge_thread_id" not in st.session_state:
    st.session_state.challenge_thread_id = None
if "challenge_text" not in st.session_state:
    st.session_state.challenge_text = ""
if "feedback_text" not in st.session_state:
    st.session_state.feedback_text = ""
if "feedback_main" not in st.session_state:
    st.session_state.feedback_main = ""
if "feedback_score" not in st.session_state:
    st.session_state.feedback_score = ""
if "selected_theme" not in st.session_state:
    st.session_state.selected_theme = ""

# === Get Writing Challenge ===
if st.button("🧠 Mr. Ali, what is today’s challenge?"):
    try:
        thread = client.beta.threads.create()
        st.session_state.challenge_thread_id = thread.id

        # Randomly choose a writing theme
        selected_theme = random.choice(list(themes.keys()))
        theme_description = themes[selected_theme]
        st.session_state.selected_theme = selected_theme

        # Compose prompt
        prompt = f"""
You are a kind writing coach helping a 12-year-old Muslim boy named Mohamad.

Today's selected writing theme is: **{selected_theme}** ({theme_description})

Please create a unique, age-appropriate challenge in this theme. Avoid repeating topics like "animals talking" or "magical pets".

The challenge should:
- Encourage creativity and Islamic values
- Include 2–3 simple writing goals (like use WOW words, a strong opening, full sentences)
- Be short and motivating
- End with a cheerful sentence encouraging Mohamad to submit his writing

Only give **one** challenge. Do not give options.
"""

        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=prompt
        )

        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )

        while run.status != "completed":
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        messages = client.beta.threads.messages.list(thread_id=thread.id)
        response_text = messages.data[0].content[0].text.value
        st.session_state.challenge_text = f"📝 **Theme: {selected_theme}**\n\n" + response_text
        st.success("✅ Here's your writing challenge from Mr. Ali")

    except Exception as e:
        st.error(f"❌ Error getting challenge: {e}")

# === Display Challenge if available ===
if st.session_state.challenge_text:
    st.subheader("📜 Today's Challenge")
    st.markdown(st.session_state.challenge_text)

# === Submit Writing ===
st.subheader("✍️ Submit Your Writing")
user_writing = st.text_area("Write your paragraph or story here:", height=250)

if st.button("📬 Submit My Work"):
    if not user_writing.strip():
        st.warning("Please write something before submitting.")
    elif not st.session_state.challenge_thread_id:
        st.warning("Please get today's challenge first.")
    else:
        try:
            # Add writing to the same thread
            client.beta.threads.messages.create(
                thread_id=st.session_state.challenge_thread_id,
                role="user",
                content=f"""Here is Mohamad’s writing:

{user_writing}

Please give kind and constructive feedback in this format:
- Two things he did well
- Two gentle suggestions for improvement
- One bonus tip
- One ASCII art sticker
- Then end with this labeled section:

Score:

Vocabulary:
Sentence Structure:
Punctuation:
Creativity:
Focus & Clarity:
"""
            )

            run = client.beta.threads.runs.create(
                thread_id=st.session_state.challenge_thread_id,
                assistant_id=ASSISTANT_ID
            )

            while run.status != "completed":
                time.sleep(1)
                run = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.challenge_thread_id,
                    run_id=run.id
                )

            messages = client.beta.threads.messages.list(
                thread_id=st.session_state.challenge_thread_id
            )
            full_feedback = messages.data[0].content[0].text.value
            st.session_state.feedback_text = full_feedback

            # === Separate the "Score" section ===
            if "Score:" in full_feedback:
                feedback_part, score_part = full_feedback.split("Score:", 1)
                st.session_state.feedback_main = feedback_part.strip()
                st.session_state.feedback_score = "Score:\n" + score_part.strip()
            else:
                st.session_state.feedback_main = full_feedback
                st.session_state.feedback_score = ""

            st.success("💡 Mr. Ali’s Feedback")
            st.markdown(st.session_state.feedback_main)

        except Exception as e:
            st.error(f"❌ Error submitting writing: {e}")

# === Display Score if available ===
if st.session_state.feedback_score:
    st.subheader("📊 Your Score Breakdown")
    st.markdown(st.session_state.feedback_score)
