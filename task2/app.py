# task2/app.py
import streamlit as st
import pandas as pd
from datetime import datetime
import os
import json
import requests
import io

st.set_page_config(page_title="AI Feedback System", layout="wide")
st.title("AI Feedback System")

DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "submissions.csv")
os.makedirs(DATA_DIR, exist_ok=True)

# --- Helper: load/save ---
def load_data():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    else:
        return pd.DataFrame(columns=["timestamp","rating","review","ai_response","summary","actions"])

def save_submission(row: dict):
    df = load_data()
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(DATA_PATH, index=False)

def delete_all_submissions():
    if os.path.exists(DATA_PATH):
        os.remove(DATA_PATH)

# --- LLM call helper (uses HTTP to OpenAI-compatible endpoint) ---
def call_llm_text(prompt, model="gpt-3.5-turbo", timeout=15):
    """
    Tries OpenAI REST API if OPENAI_API_KEY exists.
    If not available, returns a graceful fallback message.
    """
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return None  # caller will handle fallback
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0
    }

    # Try OpenAI official endpoint first
    openai_url = "https://api.openai.com/v1/chat/completions"
    try:
        r = requests.post(openai_url, json=payload, headers=headers, timeout=timeout)
        r.raise_for_status()
        j = r.json()
        return j["choices"][0]["message"]["content"].strip()
    except Exception as e:
        # If OpenAI failed but OpenRouter key is present, try OpenRouter endpoint
        if os.getenv("OPENROUTER_API_KEY"):
            try:
                or_url = "https://openrouter.ai/v1/chat/completions"
                # openrouter uses same payload in many cases
                r2 = requests.post(or_url, json=payload, headers=headers, timeout=timeout)
                r2.raise_for_status()
                j2 = r2.json()
                return j2["choices"][0]["message"]["content"].strip()
            except Exception:
                return None
        return None

# --- Simple safe fallback producers ---
def fallback_user_response(rating, review):
    return f"Thanks for your review! We appreciate your feedback."

def fallback_summary(review):
    return review[:160] + ("..." if len(review) > 160 else "")

def fallback_actions(review, rating):
    return "- Thank the customer\n- Investigate the issue\n- Improve service based on feedback"

# --- Prompt builders ---
def user_reply_prompt(rating, review):
    return f"Write a brief friendly response a restaurant would send to a customer who left this review (one short paragraph):\n\nRating: {rating}\nReview: \"{review}\""

def summary_prompt(review):
    return f"Summarize the following review in one short sentence:\n\n\"{review}\""

def actions_prompt(review, rating):
    return f"Suggest 3 concise, actionable recommendations the restaurant owner should do based on this review. Provide bullet points only.\n\nRating: {rating}\nReview: \"{review}\""

# --- UI: Sidebar selection ---
page = st.sidebar.selectbox("Select Dashboard", ["User Dashboard", "Admin Dashboard"])

# --- User Dashboard ---
if page == "User Dashboard":
    st.header("Submit Your Review")

    rating = st.selectbox("Rating", [1, 2, 3, 4, 5], index=4)
    review = st.text_area("Write your review", height=140)

    if st.button("Submit"):
        if review.strip() == "":
            st.error("Review cannot be empty")
        else:
            st.info("Saving your review...")

            # Call LLM for 3 things: reply, summary, actions
            ai_resp = call_llm_text(user_reply_prompt(rating, review))
            summary = call_llm_text(summary_prompt(review))
            actions = call_llm_text(actions_prompt(review, rating))

            # Use fallbacks if LLM not available or failed
            if ai_resp is None:
                ai_resp = fallback_user_response(rating, review)
            if summary is None:
                summary = fallback_summary(review)
            if actions is None:
                actions = fallback_actions(review, rating)

            ts = datetime.utcnow().isoformat()
            row = {
                "timestamp": ts,
                "rating": rating,
                "review": review,
                "ai_response": ai_resp,
                "summary": summary,
                "actions": actions
            }
            save_submission(row)

            st.success("Submitted! Here is the AI response:")
            st.markdown(f"**AI reply:** {ai_resp}")
            with st.expander("View Summary & Recommended Actions"):
                st.write("**Summary:**", summary)
                st.write("**Recommended actions:**")
                st.markdown(actions.replace("\n", "\n"))

# --- Admin Dashboard ---
if page == "Admin Dashboard":
    st.header("Admin Dashboard (internal)")
    df = load_data()

    if df.empty:
        st.info("No submissions yet.")
    else:
        # Analytics row
        st.subheader("Analytics")
        cols = st.columns(3)
        counts = df["rating"].value_counts().sort_index()
        total = len(df)
        cols[0].metric("Total submissions", total)
        cols[1].metric("Avg rating", round(df["rating"].mean(), 2))
        # show counts per rating
        counts_md = "\n".join([f"**{r}★**: {int(counts.get(r,0))}" for r in range(1,6)])
        cols[2].markdown(counts_md)

        # Filters
        st.subheader("Submissions")
        filter_col, search_col = st.columns([1,2])
        selected_ratings = filter_col.multiselect("Filter by rating", options=[1,2,3,4,5], default=[1,2,3,4,5])
        q = search_col.text_input("Search reviews (simple substring)")

        filtered = df[df["rating"].isin(selected_ratings)]
        if q.strip():
            filtered = filtered[filtered["review"].str.contains(q, case=False, na=False)]

        st.dataframe(filtered.reset_index(drop=True), use_container_width=True)

        # Download CSV
        csv_buf = filtered.to_csv(index=False).encode("utf-8")
        st.download_button("Download filtered CSV", data=csv_buf, file_name="submissions_filtered.csv", mime="text/csv")

        # Delete all with confirmation
        st.markdown("---")
        if st.checkbox("I confirm I want to delete all submissions"):
            if st.button("Delete all"):
                delete_all_submissions()
                st.success("All submissions deleted. Refresh the app to see changes.")

# --- Footer note for missing API key ---
if not (os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY")):
    st.sidebar.warning("OPENAI_API_KEY or OPENROUTER_API_KEY not set. AI features will use fallback text. Set env var and restart for live AI.")
