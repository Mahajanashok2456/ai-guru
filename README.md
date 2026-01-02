# Mitra: The Wisdom Companion 🌌

> *"Ancient wisdom for modern life."*

**Mitra** (Sanskrit for "Friend") is an AI-powered empathetic therapist and wisdom companion. It bridges the gap between ancient philosophy and modern mental wellness by providing guidance rooted in the timeless epics of the **Mahabharata** and **Ramayana**.

Unlike standard chatbots, Mitra doesn't just "search and quote." It **internalizes** the wisdom, analyzes your emotional state, and offers compassionate, practical advice as a true friend would—without overwhelming you with citations or religious text.

---

## ✨ Key Features

### 🧠 Adaptive Contextual Engine
Mitra doesn't just answer questions; it understands **Intent** and **Tone**.
*   **Emotional Resonance:** If you are sad, it speaks with empathy and gentleness. If you are curious, it speaks with scholarly precision.
*   **Seamless Wisdom:** It weaves ancient principles (Dharma, Karma, Resilience) naturally into conversation without sounding preachy.

### 📚 RAG (Retrieval-Augmented Generation) Architecture
*   **Vector Database:** The entire texts of the Mahabharata and Ramayana have been embedded and stored in **MongoDB Atlas**.
*   **Smart Retrieval:** When you ask a question, Mitra searches for the specific "spiritual DNA" of your problem in these texts.
*   **Intelligent Fallback:** If specific text is elusive, Mitra relies on its deep internal model knowledge of the epics to ensure you always get a helpful answer.

### 🎨 Modern Ethereal UI
*   **Immersive Experience:** Deep "Cosmic Midnight" background with dynamic, twinkling stars that drift across the screen.
*   **Glassmorphism:** A floating, transparent interface that feels light and non-intrusive.
*   **Calming Aesthetics:** A "Moonlight Cyan" color palette designed to induce relaxation and focus.

---

## 🛠️ Technology Stack

### Frontend
*   **React.js**: For a responsive, dynamic user interface.
*   **Custom Webpack**: Optimized build process.
*   **CSS3**: Custom "Ethereal" design system (Variables, Animations, Flexbox).

### Backend
*   **FastAPI (Python)**: High-performance async API framework.
*   **Google Gemini (2.5 Flash)**: The brain behind the understanding and generation.
*   **MongoDB Atlas**: Vector search capability for the knowledge base.
*   **PyMongo**: Database connectivity.

---

## 🚀 How It Works

1.  **User Input:** You type: *"I feel overwhelmed by my duty."*
2.  **Vector Search:** The backend converts this feeling into a mathematical vector and searches MongoDB for similar themes (e.g., Arjuna's despair on the battlefield).
3.  **Tone Analysis:** The AI assesses your tone (Anxious/overwhelmed).
4.  **Synthesis:**
    *   *Context:* It pulls the specific verses about doing one's duty without attachment.
    *   *Persona:* It adopts the voice of a compassionate guide.
5.  **Response:** *"It is natural to feel the weight of the world. Like the warrior who once stood frozen before battle, remember that your only true task is the effort itself, not the outcome. Breathe, and take just one step."*

---

## 💻 Local Setup Guide

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/Mahajanashok2456/mitra.git
    cd mitra
    ```

2.  **Backend Setup**
    *   Create a virtual environment (optional but recommended):
        ```bash
        python -m venv venv
        # Windows: venv\Scripts\activate
        # Mac/Linux: source venv/bin/activate
        ```
    *   Install dependencies:
        ```bash
        pip install -r requirements.txt
        ```
    *   Create a `.env` file in the root directory:
        ```bash
        ATLAS_URI=your_mongodb_connection_string
        GEMINI_API_KEY=your_google_gemini_key
        ```
    *   Run the server:
        ```bash
        python main.py
        ```
    *   *Server runs on `http://localhost:8000`*

3.  **Frontend Setup**
    *   Navigate to the frontend folder:
        ```bash
        cd frontend
        ```
    *   Install dependencies:
        ```bash
        npm install
        ```
    *   Start the app:
        ```bash
        npm start
        ```
    *   *App runs on `http://localhost:3000`*

---

## 🌐 Deployment

This project is optimized for a hybrid deployment:
*   **Frontend:** Vercel
*   **Backend:** Render

See [DEPLOYMENT.md](./DEPLOYMENT.md) for a detailed step-by-step guide.

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
1.  Fork the repository.
2.  Create a feature branch.
3.  Submit a Pull Request.

---

*Created with ❤️ by Ashok Mahajan*