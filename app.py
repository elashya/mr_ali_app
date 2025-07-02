import streamlit as st
from openai import OpenAI
import os
import time
import random

# === PIN Authentication ===
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.set_page_config(page_title="Mr. Ali's Writing Coach", layout="centered")
    st.title("🔐 Mr. Ali - Secure Writing Access")
    pin = st.text_input("Please enter your writing PIN:", type="password")
    if pin == st.secrets["APP_PIN"]:
        st.session_state.authenticated = True
        st.success("✅ Access granted. Welcome, Mohamad!")
        time.sleep(1)
        st.rerun()
    else:
        st.warning("Please enter the correct PIN to begin.")
        st.stop()

# === Load API Keys and Assistants ===
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=OPENAI_API_KEY)
WRITING_ASSISTANT_ID = "asst_CIL8hS7ZusGwpdXdS6eB0zAr"  # Mr. Ali
PUZZLE_ASSISTANT_ID = "asst_bnkXJguwaq1JWbMBnJDFJPxo"   # Mr. Puzzle

# === Page Config ===
st.set_page_config(page_title="Mr. Ali's Writing Coach", layout="centered")
st.title("✍️ Mr. Ali – Mohamad's Coach")

# === Themes ===
themes = {
    "Fiction": "a fun or imaginative story (e.g., magic, adventure, mystery)",
    "Non-fiction": "a real story, opinion, or personal reflection",
    "Creative Writing": "something like a poem, comic scene, diary entry, or what-if idea"
}

# === Session State Initialization ===
for key in [
    "challenge_thread_id", "challenge_text", "feedback_text",
    "feedback_main", "feedback_score", "selected_theme",
    "puzzle_text", "puzzle_thread_id", "last_type"
]:
    if key not in st.session_state:
        st.session_state[key] = ""

# === Writing Challenge ===
if st.button("🧠 Mr. Ali, what is today’s challenge?"):
    try:
        thread = client.beta.threads.create()
        st.session_state.challenge_thread_id = thread.id
        st.session_state.last_type = "challenge"
        st.session_state.puzzle_text = ""

        selected_theme = random.choice(list(themes.keys()))
        theme_description = themes[selected_theme]
        st.session_state.selected_theme = selected_theme

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
            assistant_id=WRITING_ASSISTANT_ID
        )

        while run.status != "completed":
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        messages = client.beta.threads.messages.list(thread_id=thread.id)
        for message in reversed(messages.data):
            if message.role == "assistant":
                response_text = message.content[0].text.value
                break

        st.session_state.challenge_text = f"📝 **Theme: {selected_theme}**\n\n" + response_text
        st.success("✅ Here's your writing challenge from Mr. Ali")

    except Exception as e:
        st.error(f"❌ Error getting challenge: {e}")

# === Puzzle Generator ===
if st.button("🧩 Give me a puzzle"):
    try:
        puzzle_thread = client.beta.threads.create()
        st.session_state.puzzle_thread_id = puzzle_thread.id
        st.session_state.last_type = "puzzle"
        st.session_state.challenge_text = ""
        st.session_state.feedback_main = ""
        st.session_state.feedback_score = ""

        puzzle_prompt = """
You are Mr. Puzzle, a fun and kind assistant helping a 12-year-old Muslim boy named Mohamad.

Please give him ONE short, age-appropriate brain teaser, riddle, or logic puzzle.

Rules:
- Keep it clear and fun
- Make sure it’s solvable by a smart 12-year-old
- Avoid complex math or confusing wording
- End with an upbeat sentence like “Can you figure it out?”

Only one puzzle. No explanation unless asked.
"""

        client.beta.threads.messages.create(
            thread_id=puzzle_thread.id,
            role="user",
            content=puzzle_prompt
        )

        run = client.beta.threads.runs.create(
            thread_id=puzzle_thread.id,
            assistant_id=PUZZLE_ASSISTANT_ID
        )

        while run.status != "completed":
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=puzzle_thread.id,
                run_id=run.id
            )

        messages = client.beta.threads.messages.list(thread_id=puzzle_thread.id)
        for message in reversed(messages.data):
            if message.role == "assistant":
                puzzle_text = message.content[0].text.value
                break

        st.session_state.puzzle_text = puzzle_text
        st.success("🧠 Here's your puzzle from Mr. Puzzle!")

    except Exception as e:
        st.error(f"❌ Error generating puzzle: {e}")

# === Display Either Challenge or Puzzle ===
if st.session_state.last_type == "challenge" and st.session_state.challenge_text:
    st.subheader("📜 Today's Challenge")
    st.markdown(st.session_state.challenge_text)

elif st.session_state.last_type == "puzzle" and st.session_state.puzzle_text:
    st.subheader("🧠 Brain Puzzle")
    st.markdown(st.session_state.puzzle_text)

# === Shared Input Box ===
st.subheader("✍️ Submit Your Writing or Puzzle Answer")
user_input = st.text_area("Write your story or puzzle answer here:", height=250)

if st.button("📬 Submit My Work"):
    if not user_input.strip():
        st.warning("Please write something before submitting.")

    elif st.session_state.last_type == "puzzle":
        if not st.session_state.puzzle_thread_id:
            st.warning("Please click 'Give me a puzzle' first.")
        else:
            try:
                client.beta.threads.messages.create(
                    thread_id=st.session_state.puzzle_thread_id,
                    role="user",
                    content=f"""Mohamad's answer to the puzzle is:

{user_input}

Please kindly respond:
- Was the answer correct or not?
- Explain the reasoning briefly
- Give an encouraging comment
- End with an emoji or short sticker line
"""
                )

                run = client.beta.threads.runs.create(
                    thread_id=st.session_state.puzzle_thread_id,
                    assistant_id=PUZZLE_ASSISTANT_ID
                )

                while run.status != "completed":
                    time.sleep(1)
                    run = client.beta.threads.runs.retrieve(
                        thread_id=st.session_state.puzzle_thread_id,
                        run_id=run.id
                    )

                messages = client.beta.threads.messages.list(
                    thread_id=st.session_state.puzzle_thread_id
                )
                for message in reversed(messages.data):
                    if message.role == "assistant":
                        response = message.content[0].text.value
                        break

                st.success("🧩 Mr. Puzzle’s Response")
                st.markdown(response)

            except Exception as e:
                st.error(f"❌ Error submitting puzzle answer: {e}")

    elif st.session_state.last_type == "challenge":
        if not st.session_state.challenge_thread_id:
            st.warning("Please get today's challenge first.")
        else:
            try:
                client.beta.threads.messages.create(
                    thread_id=st.session_state.challenge_thread_id,
                    role="user",
                    content=f"""Here is Mohamad’s writing:

{user_input}

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
                    assistant_id=WRITING_ASSISTANT_ID
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
                for message in reversed(messages.data):
                    if message.role == "assistant":
                        full_feedback = message.content[0].text.value
                        break

                st.session_state.feedback_text = full_feedback

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

    else:
        st.warning("Please start with either a challenge or a puzzle before submitting.")

# === Display Score if available ===
if st.session_state.feedback_score:
    st.subheader("📊 Your Score Breakdown")
    st.markdown(st.session_state.feedback_score)
