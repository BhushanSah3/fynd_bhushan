# Fynd AI Engineering Intern 

This repository contains my submission for the Fynd AI Engineering Intern take-home assessment. It includes prompt-based rating prediction experiments and a deployed two-dashboard AI feedback system.
---

## 🧠 Task 1 – Rating Prediction via Prompting

**Objective:**  
Classify Yelp reviews into 1–5 star ratings using prompt-based LLM approaches.

**Approach:**
- Sampled 200 reviews from the Yelp dataset
- Designed 3 different prompt strategies:
  - V1: Zero-shot strict JSON
  - V2: Few-shot prompting
  - V3: Reasoned prompting
- Evaluated each on:
  - Accuracy
  - JSON validity
  - Reliability

**Results Summary:**

| Prompt | Accuracy | JSON Validity |
|------|----------|---------------|
| V1 Zero-shot | 0.695 | 1.00 |
| V2 Few-shot | 0.405 | 0.64 |
| V3 Reasoned | 0.660 | 1.00 |

All experiments and evaluation code are in the notebook.

---

## 🌐 Task 2 – Two-Dashboard AI Feedback System

### User Dashboard (Public)
- Select star rating
- Submit textual review
- Receive AI-generated response
- Submission stored persistently

### Admin Dashboard (Internal)
- Live-updating submissions table
- AI-generated summaries
- AI-suggested recommended actions
- Basic analytics (counts, averages)
- CSV download option

### Tech Stack
- Python
- Streamlit
- CSV-based persistence
- LLM-powered responses (with safe fallback)

---

## 🚀 Deployment

- **User Dashboard URL:** <https://fyndbhushan-j3tlxzse4wvmab9nkv8jdv.streamlit.app/>
- **Admin Dashboard URL:** <https://fyndbhushan-j3tlxzse4wvmab9nkv8jdv.streamlit.app/>

Both dashboards are publicly accessible and deployed.

---

## 🔐 Environment Variables

For full AI functionality:
OPENAI_API_KEY= ....


If not set, the app falls back to predefined responses to ensure reliability.

---

## 👤 Author
**Bhushan Sah**  
AI Engineering Intern Applicant  
