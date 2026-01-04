# Deployment Guide

This guide will help you deploy your **GuruMultibot** to the web for free.

We will use:
1.  **Render** for the Backend (Python/FastAPI).
2.  **Vercel** for the Frontend (React).

---

## Part 1: Prepare your Code

1.  **Push your code to GitHub.**
    *   Push this entire project folder to a new GitHub repository.
    *   *Make sure your `.env` file is NOT in the repo (it should be allowed by .gitignore).*

---

## Part 2: Deploy Backend (Render)

1.  Go to [dashboard.render.com](https://dashboard.render.com/) and create an account.
2.  Click **New +** -> **Web Service**.
3.  Connect your GitHub repository.
4.  Configure the service:
    *   **Name:** `guru-backend` (or similar)
    *   **Root Directory:** `backend` (Important!)
    *   **Runtime:** `Python 3`
    *   **Build Command:** `pip install -r requirements.txt`
    *   **Start Command:** `uvicorn main:app --host 0.0.0.0 --port 10000`
5.  **Environment Variables:**
    *   Scroll down to "Environment Variables".
    *   Add the keys from your local `.env` file (or required setup):
        *   `MONGODB_URI`: (Your MongoDB Connection String)
        *   `GEMINI_API_KEY`: (Your Google Gemini API Key)
        *   `ENVIRONMENT`: `production`
6.  Click **Create Web Service**.
7.  Wait for it to deploy. Once live, copy the **URL** (e.g., `https://guru-backend.onrender.com`).

---

## Part 3: Deploy Frontend (Vercel)

1.  Go to [vercel.com](https://vercel.com/) and create an account.
2.  Click **Add New...** -> **Project**.
3.  Import your GitHub repository.
4.  Configure the project:
    *   **Framework Preset:** `Create React App`
    *   **Root Directory:** Click "Edit" and select `frontend`.
    *   **Build Command:** `npm run build`
    *   **Output Directory:** `build` (Default for Create React App)
5.  **Environment Variables:**
    *   Add a variable:
        *   **Name:** `REACT_APP_API_URL`
        *   **Value:** Input the **Backend URL** from Part 2 (e.g., `https://guru-backend.onrender.com`). *Do not add a trailing slash.*
6.  Click **Deploy**.

---

## Part 4: Final Check

1.  Open your new Vercel URL.
2.  The app should load.
3.  Send a message ("Hello"). The frontend should talk to your Render backend, which talks to MongoDB and Gemini, and gives you a response.
