# -*- coding: utf-8 -*-
"""
Created on Wed Jul 30 17:20:46 2025

@author: miroz
"""

# FINAL Version - DON`T TOUCH!!!!!!!


# --- Imports: Core Python, environmental variables, UI, APIs, and date/time for filenames ---
import os # provides functions for interacting with the operating system
from dotenv import load_dotenv # allows you to load environment variables from a .env file
import streamlit as st
import openai
from datetime import datetime

# --- CSS to remove Streamlit's "Ctrl+Enter" helper hints from all text fields ---
st.markdown("""
    <style>
    /* Target hints under all text input and text area fields */
    .e1bc0bcm0, .stTextArea [data-baseweb="textarea"]+div, .stTextInput [data-baseweb="input"]+div {
        visibility: hidden; height: 0px !important; pointer-events: none;
    }
    </style>
""", unsafe_allow_html=True)

# --- Top-of-app Infographic/Workflow Graphic ---
# Shows the main user flow visually at the very top
st.image("generated-image.png", use_container_width=True)  # Change the filename as needed to match your image
# CSS tweak to move title up closer under the image
st.markdown("""
    <style>
    .block-container img {
        margin-bottom: 0.5rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Load environment variables (like API keys) from .env file in the current directory ---
dotenv_path = os.path.join(os.getcwd(), '.env')
load_dotenv(dotenv_path=dotenv_path)

# --- Create a folder to store session reports if it doesn't exist ---
SAVE_DIR = r"C:\Users\miroz\first_principles_sessions"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# --- The core "FirstPrinciplesSolver" class: Handles all OpenAI API interactions ---
class FirstPrinciplesSolver:
    def __init__(self):
        # Try to get the OpenAI API key from environment. Halt app if not present.
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.error(
                "OPENAI_API_KEY is missing. "
                "Your .env must be in the SAME folder and contain: OPENAI_API_KEY=sk-...")
            raise RuntimeError("OPENAI_API_KEY missing")
        # Set up OpenAI client for later prompt calls
        self.client = openai.OpenAI(api_key=api_key)

    def analyze_problem(self, problem):
        # Compose detailed prompt for first-principles analysis.
        prompt = f"""
        You are an expert in first-principles thinking. Analyze this problem: "{problem}"
        Provide structured analysis with:
        1. Problem Domain: What category does this belong to?
        2. Fundamental Elements: 4-5 core components that drive this problem
        3. Hidden Assumptions: 2-3 assumptions the person might not realize they're making
        4. Key Questions: 3 specific questions to help them think deeper
        Be practical and specific. Format your response clearly.
        """
        try:
            # Call OpenAI API, get model response, extract content only (not full metadata)
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400, temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error analyzing problem: {e}"

    def challenge_assumption(self, assumption, context):
        # Prompt to critically challenge an assumption via first principles
        prompt = f"""
        Challenge this assumption: "{assumption}"
        In the context of: "{context}"
        Generate 2-3 thought-provoking questions that:
        - Question why this assumption exists
        - Explore what would happen if it weren't true
        - Suggest alternative perspectives
        Be specific and practical.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200, temperature=0.8
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error challenging assumption: {e}"

    def generate_solutions(self, problem, facts, elements):
        # Prompt the AI for unconventional, creative, first-principles solutions
        prompt = f"""
        Using first-principles thinking, generate creative solutions for: "{problem}"
        Given these facts: {facts}
        And these key elements: {elements}
        Suggest 3-4 unconventional approaches that:
        1. Question the problem definition
        2. Eliminate unnecessary constraints
        3. Recombine elements in new ways
        4. Draw inspiration from other domains
        Be specific and actionable.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400, temperature=0.8
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating solutions: {e}"

# --- Streamlit page config and headers ---
st.set_page_config(page_title="First Principles Problem Solving", page_icon="🧠", layout="centered")
st.title("🧠 First Principles Problem Solving")
st.write("Apply first principles thinking to clarify any challenge, step by step.")

# --- Set up and verify the solver (API connection) ---
try:
    solver = FirstPrinciplesSolver()
except Exception:
    st.stop()  # If missing key, stop the app, error already shown

# --- Define all session state variables needed for full dialog flow and reset ---
defaults = {
    "problem_input": "",            # The user's core problem statement
    "analysis": None,               # AI's first-principles analysis output
    "assumption_input": "",         # User's stated hidden assumption
    "challenge": None,              # AI's assumption challenge
    "facts_input": "",              # User's list of relevant facts
    "elements_input": "",           # User's list of main elements/drivers
    "solutions": None,              # AI's creative solutions
    "show_exit": False,             # Whether to display exit instructions
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --- Cross-version helper: rerun the app (after updating session state) ---
def rerun():
    try:
        st.rerun()    # Streamlit >=1.27
    except AttributeError:
        st.experimental_rerun()  # Streamlit <1.27

# --------------- Multi-step interactive UI ---------------
# STEP 1: User enters the problem statement
if not st.session_state.analysis:
    with st.form("problem_form", clear_on_submit=False):
        problem = st.text_area(
            "📝 State your challenge, question, or problem:",
            value=st.session_state.problem_input,
            help=" "  # disables input hint
        )
        # User clicks button to submit the problem (no accidental submit on Enter)
        next1 = st.form_submit_button("Next: Analyze with First Principles", type="primary")
        if next1 and problem.strip():
            # Show spinner while AI processes input
            with st.spinner("Analyzing your problem with first principles..."):
                analysis = solver.analyze_problem(problem)
            # Store everything; clear downstream session state for proper step flow
            st.session_state.problem_input = problem
            st.session_state.analysis = analysis
            st.session_state.assumption_input = ""
            st.session_state.challenge = None
            st.session_state.facts_input = ""
            st.session_state.elements_input = ""
            st.session_state.solutions = None
            st.session_state.show_exit = False
            rerun()  # Immediately rerun, now displaying the next step

# STEP 2: Show analysis, ask for one assumption, collect and handle via button
elif st.session_state.analysis and not st.session_state.challenge:
    st.markdown("### First Principles Analysis")
    st.write(st.session_state.analysis)
    st.markdown("---")
    with st.form("assumption_form", clear_on_submit=False):
        assumption = st.text_input(
            "🤔 State one assumption you're making about this problem:",
            value=st.session_state.assumption_input,
            help=" "
        )
        next2 = st.form_submit_button("Next: Challenge Assumption", type="primary")
        if next2 and assumption.strip():
            with st.spinner("Challenging your assumption (first principles)..."):
                challenge = solver.challenge_assumption(assumption, st.session_state.problem_input)
            st.session_state.assumption_input = assumption
            st.session_state.challenge = challenge
            st.session_state.facts_input = ""
            st.session_state.elements_input = ""
            st.session_state.solutions = None
            st.session_state.show_exit = False
            rerun()

# STEP 3: Show challenge, ask for facts/elements; collect user input, process on button
elif st.session_state.challenge and not st.session_state.solutions:
    st.markdown("### Assumption Challenge")
    st.write(st.session_state.challenge)
    st.markdown("---")
    with st.form("facts_form", clear_on_submit=False):
        facts = st.text_area(
            "📊 List relevant facts you know about this situation:",
            value=st.session_state.facts_input,
            help=" "
        )
        elements = st.text_area(
            "🧩 List the main elements or drivers involved:",
            value=st.session_state.elements_input,
            help=" "
        )
        next3 = st.form_submit_button("Next: Generate First Principles Solutions", type="primary")
        if next3 and facts.strip() and elements.strip():
            with st.spinner("Generating creative first-principles solutions..."):
                solutions = solver.generate_solutions(
                    st.session_state.problem_input,
                    facts, elements
                )
            st.session_state.facts_input = facts
            st.session_state.elements_input = elements
            st.session_state.solutions = solutions
            rerun()

# STEP 4: All steps complete: show all results/answers and save .txt report, with extra options/buttons
elif st.session_state.solutions:
    # Display all results (analysis, challenge, solutions) for review
    st.markdown("### First Principles Analysis")
    st.write(st.session_state.analysis)
    st.markdown("### Assumption Challenge")
    st.write(st.session_state.challenge)
    st.markdown("### Creative Solutions")
    st.write(st.session_state.solutions)
    st.markdown("---")

    # Format the full report for downloading and saving to disk
    session_txt = f"""First Principles Problem Solving Session
========================================

Problem: {st.session_state.problem_input}

First Principles Analysis:
{st.session_state.analysis}

Challenged Assumption: {st.session_state.assumption_input}
Challenge Response:
{st.session_state.challenge}

Creative Solutions:
{st.session_state.solutions}
"""
    # Write .txt session to the fixed folder with a time-stamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"first_principles_session_{timestamp}.txt"
    abs_path = os.path.join(SAVE_DIR, filename)
    try:
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(session_txt)
        st.success(f"Session automatically saved as **{filename}**.")
        st.caption(f"Full path: {abs_path}")
    except Exception as e:
        st.error(f"Could not save file: {e}")

    # Let user also download it instantly from browser if desired
    st.download_button("💾 Download Session Report", session_txt, file_name=filename)

    # Two columns: continue (reset session_state), exit (show instructions)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Continue with another problem 🚀"):
            for k in list(st.session_state.keys()):
                st.session_state[k] = defaults.get(k, None)  # reset to initial state
            rerun()
    with col2:
        if st.button("Show Exit Instructions ❌"):
            st.session_state.show_exit = True

    # If "exit" is pressed, explain how to close the tab and stop Streamlit
    if st.session_state.show_exit:
        st.info(
            "To close the app: **close this browser tab/window**. "
            "Then, in your terminal, press **Ctrl+C** to stop the server."
        )

# --- UI/UX tip at the bottom at all times ---
st.markdown("---")
st.info("If you want to reset the session, refresh the page.")
