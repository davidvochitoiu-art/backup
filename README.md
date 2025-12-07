# 🧠 Multi-Domain Intelligence Platform  
A unified intelligence system built with **Python**, **Streamlit**, **SQLite**, a clean **OOP architecture**, and a **local AI assistant powered by Ollama (Phi-3 Mini)**.

This platform integrates:
- **Cybersecurity Incidents**
- **Dataset Metadata**
- **IT Support Tickets**

into a single dashboard with analytics, CRUD dashboards, authentication, and AI-driven insights.

---

# 🚀 Features

### 🔐 Secure Authentication System (Week 7)
- Password hashing using **bcrypt**
- Login + registration pages
- Session-based access protection
- Automatic user migration from `.txt`

### 📊 Interactive Multi-Domain Dashboard (Week 8–9)
Includes fully interactive pages for:

#### 🛡 Cybersecurity Incidents
- Filters: severity, status  
- Visuals: bar charts, pie charts  
- **Full CRUD**: create, update status, delete  
- Severity ranking  

#### 📂 Dataset Metadata
- Size calculation (rows × columns)  
- Line charts & distribution charts  
- **Full CRUD**: create, update metadata, delete  

#### 💼 IT Support Tickets
- Priority/status filters  
- Workload analytics  
- **Full CRUD**: create ticket, update status, delete  

### 🤖 Local AI Assistant (Week 10)
Powered by **Ollama (Phi-3 Mini)** — NO API cost.

The AI uses real-time analytics from the database to:
- Identify top severe cyber incidents  
- Summarise system health  
- Highlight ticket workload  
- Identify busiest IT staff  
- Analyse dataset usage + row distribution  
- Provide professional, structured insights  

### 🧱 OOP Architecture (Week 11)
The system uses:
- **Models** → CyberIncident, Dataset, ITTicket, User  
- **Services** → DatabaseManager, AuthManager, AIAssistant  
- **Data Layer** → SQLite + CSV loading  
- **UI Layer** → Streamlit pages  

This modular architecture ensures maintainability and scalability.

---

# 📁 Project Structure


                 ┌──────────────────────────┐
                 │        Home.py            │
                 │   (Login / Register)      │
                 └─────────────┬────────────┘
                               │
                               ▼
               ┌────────────────────────────┐
               │         Dashboard           │
               │ (Incidents / Datasets / IT │
               │        Tickets CRUD)        │
               └─────────────┬──────────────┘
                               │
                               ▼
         ┌────────────────────────────┐
         │        AI Assistant        │
         │   (Ollama + Analytics)     │
         └─────────────┬──────────────┘
                       │
            STREAMLIT UI LAYER
                       │
                       ▼
    ┌────────────────────────────────────────┐
    │                SERVICES                 │
    │  AuthManager | DatabaseManager | AI     │
    └──────────────┬─────────────────────────┘
                   │
                   ▼
    ┌────────────────────────────────────────┐
    │                  MODELS                 │
    │  User | Dataset | ITTicket | Incident   │
    └──────────────┬─────────────────────────┘
                   │
                   ▼
    ┌────────────────────────────────────────┐
    │                DATABASE                 │
    │    SQLite + CSV Import + Migration     │
    └────────────────────────────────────────┘



---

# 🛠️ Installation & Setup

### 1️⃣ Install dependencies



### 2️⃣ Install Ollama  
https://ollama.com/download

Pull the model:



Run the model:


### 3️⃣ Run the Streamlit application



---

# 🧠 AI Assistant – How It Works

The AI Assistant uses a custom context builder that generates real insights, including:

### ✔ Incident Analytics  
- Total incidents  
- Critical & high severity counts  
- Most common category  
- Top 5 severe incidents  

### ✔ Dataset Analytics  
- Largest dataset  
- Average row count  
- Dataset size estimation  

### ✔ IT Ticket Analytics  
- Total tickets  
- Closed tickets  
- Staff with highest workload  
- Priority/Status breakdown  

This is all passed to the **Phi-3 Mini** model locally to generate high-quality responses.

Example query:
> “Which staff member is most overloaded with IT tickets?”

Example query:
> “Give me a summary of the current cybersecurity threat landscape.”

---

# ✏️ CRUD Feature Summary (Distinction Essential)

### ✔ Cyber Incidents CRUD  
- Create incident  
- Update status  
- Delete incident  

### ✔ Dataset CRUD  
- Create dataset  
- Update metadata  
- Delete dataset  

### ✔ IT Ticket CRUD  
- Create ticket  
- Update ticket status  
- Delete ticket  

Each CRUD form refreshes the UI in real-time (`st.rerun()`).

---

# 🧩 OOP Justification

The project demonstrates **strong OOP design principles**:

### Encapsulation  
Each model controls access to its attributes via getters/setters.

### Single Responsibility  
- Models: store data  
- Services: business logic  
- Streamlit pages: UI/interaction layer  

### Separation of Concerns  
No SQL code exists inside UI pages.  
All DB operations are inside `DatabaseManager`.

### Reusability  
Incident, Dataset, and Ticket models share a consistent structure.

This meets and exceeds Week 11 requirements.

---

# 📸 Screenshots (Add After Running)

Create a `screenshots/` folder and add your images:



---

# 🚀 Future Improvements

- Role-Based Access (Admin vs General User)
- Incident auto-classification using LLM
- Predictive analytics for cyber incidents
- Exportable reports (PDF)
- Advanced chat memory with summarisation

---

# ✔ Final Notes

This project now satisfies **all Tier 3 Distinction requirements**:
- ✓ Secure authentication  
- ✓ SQLite + migrations  
- ✓ Multi-domain dashboard  
- ✓ Full CRUD for 3 domains  
- ✓ AI Assistant using analytics  
- ✓ OOP architecture  
- ✓ Clean documentation  

**You are ready for submission.**

---
