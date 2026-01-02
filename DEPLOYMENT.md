
# Deployment Guide

This guide will help you deploy your **Wisdom Companion** (Therapist Bot) to the web for free.

We will use:
1.  **Render** for the Backend (Python/FastAPI).
2.  **Vercel** for the Frontend (React).

---

## Part 1: Prepare your Code

1.  **Push your code to GitHub.**
    *   Create a new repository on GitHub.
    *   Push this entire project folder to it.
    *   *Make sure your `.env` file is NOT in the repo (it should be allowed by .gitignore).*

---

## Part 2: Deploy Backend (Render)

1.  Go to [dashboard.render.com](https://dashboard.render.com/) and create an account.
2.  Click **New +** -> **Web Service**.
3.  Connect your GitHub repository.
4.  Configure the service:
    *   **Name:** `wisdom-companion-backend` (or similar)
    *   **Root Directory:** `.` (leave empty or dot)
    *   **Runtime:** `Python 3`
    *   **Build Command:** `pip install -r requirements.txt`
    *   **Start Command:** `uvicorn main:app --host 0.0.0.0 --port 10000`
5.  **Environment Variables:**
    *   Scroll down to "Environment Variables".
    *   Add the keys from your local `.env` file:
        *   `ATLAS_URI`: (Your MongoDB Connection String)
        *   `GEMINI_API_KEY`: (Your Google Gemini API Key)
6.  Click **Create Web Service**.
7.  Wait for it to deploy. Once live, copy the **URL** (e.g., `https://wisdom-backend.onrender.com`).

---

## Part 3: Deploy Frontend (Vercel)

1.  Go to [vercel.com](https://vercel.com/) and create an account.
2.  Click **Add New...** -> **Project**.
3.  Import your GitHub repository.
4.  Configure the project:
    *   **Framework Preset:** Select `Other` (since we use custom Webpack) or leave as is if it detects it.
    *   **Root Directory:** Click "Edit" and select `frontend`.
    *   **Build Command:** `npm run build` (should be detected automatically).
    *   **Output Directory:** `dist` (This is important! Our webpack config outputs to `dist`).
5.  **Environment Variables:**
    *   Add a variable:
        *   **Name:** `REACT_APP_API_URL`
        *   **Value:** Input the **Backend URL** from Part 2 (e.g., `https://wisdom-backend.onrender.com`). *Do not add a trailing slash.*
6.  Click **Deploy**.

---

## Part 4: Final Check

1.  Open your new Vercel URL.
2.  The stars should twinkle!
3.  Ask a question. The frontend should talk to your Render backend, which talks to MongoDB and Gemini, and gives you a wise response.
