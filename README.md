This project is a Multi-Domain Intelligence Platform built using Python and Streamlit.
It integrates cybersecurity incident analytics, IT ticketing, and dataset insights into a
single dashboard. The system uses an Object-Oriented Architecture with models, services,
and pages to ensure clean separation of concerns. A local AI assistant powered by 
Ollama (Phi-3 Mini) provides intelligent insights based on system data. User 
authentication is implemented using bcrypt hashing for secure login and registration.


- 🔐 Secure login and registration (bcrypt)
- 📊 Dashboard: Incidents, datasets, and tickets
- 🤖 Local AI assistant using Ollama Phi-3 Mini
- 🧠 Multi-domain contextual reasoning
- 🗄️ SQLite persistent database
- 🧱 Fully OOP architecture (models + services)
- 🧩 Clean Streamlit UI with tabs/sections
 

 app/
 ├── models/
 │    ├── User.py
 │    ├── security_incident.py
 │    ├── dataset.py
 │    └── it_ticket.py
 ├── services/
 │    ├── database_manager.py
 │    ├── auth_manager.py
 │    └── ai_assistant.py
 └── data/
      ├── users.py
      ├── incidents.py
      ├── datasets.py
      ├── tickets.py
      └── db.py

pages/
 ├── 1_Dashboard.py
 └── 2_AI_Assistant.py

Home.py
DATA/
 ├── intelligence_platform.db
 ├── cyber_incidents.csv
 ├── datasets_metadata.csv
 └── it_tickets.csv


1. Install dependencies:
   pip install -r requirements.txt

2. Start the local Ollama server (required for AI):
   ollama run phi3:mini

3. Run the application:
   streamlit run Home.py


The project uses a clear separation of concerns:

Models (Entities)
-----------------
Represent domain objects such as User, SecurityIncident, Dataset, and ITTicket.
These classes contain attributes and domain methods only.

Services (Logic Layer)
----------------------
- DatabaseManager handles all SQL operations.
- AuthManager manages registration, login, password hashing.
- AIAssistant communicates with the local LLM (Ollama).

Pages (Presentation Layer)
--------------------------
- Home.py manages login and registration.
- 1_Dashboard.py displays incidents, datasets, and tickets using OOP objects.
- 2_AI_Assistant.py provides AI chat functionality.

This layered architecture makes the system cleaner, scalable, and easier to maintain.


Home.py → AuthManager → DatabaseManager → Models

1_Dashboard.py → DatabaseManager → Models → Streamlit UI

2_AI_Assistant.py → AIAssistant → DatabaseManager → Models


- Add CRUD operations to create/update/delete incidents and tickets.
- Implement role-based access (Admin vs Analyst users).
- Add dataset upload functionality.
- Improve dashboard visualizations (KPIs, charts, filters).
- Add caching for faster AI context building.
