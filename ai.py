import os, json, sqlite3
from openai import OpenAI

RULES = """Constraints:
- Return ONLY a single valid SQLite SELECT. No backticks, no prose.
- Use explicit JOINs on keys (Employees.TeamID = Teams.TeamID).
- Prefer LIMIT for top-N results.
- Never write UPDATE/DELETE/INSERT.
"""

SCHEMA_HINT = """Tables:
- Teams(TeamID INTEGER PRIMARY KEY, TeamTitle TEXT, SupervisorEmail TEXT)
- Employees(NetID TEXT PRIMARY KEY, FirstName TEXT, LastName TEXT, TeamID INTEGER, HireDate TEXT, Status TEXT, FOREIGN KEY(TeamID) REFERENCES Teams(TeamID))
- PerformanceReviews(ReviewID INTEGER PRIMARY KEY, NetID TEXT, TeamID INTEGER, ReviewDate TEXT, ScoreTotal REAL, RaiseEntered INTEGER, StayingNextSemester INTEGER, Feedback TEXT, FOREIGN KEY(NetID) REFERENCES Employees(NetID), FOREIGN KEY(TeamID) REFERENCES Teams(TeamID))
"""

def client():
    return OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def ask_sql(question: str) -> str:
    prompt = f"""You translate questions to SQL for SQLite.
{RULES}

Schema:
{SCHEMA_HINT}

Question: {question}
SQL:"""
    resp = client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        temperature=0
    )
    return resp.choices[0].message.content.strip()

def synthesize_answer(question: str, rows: list[dict]) -> str:
    prompt = f"""Question: {question}
Rows (JSON): {json.dumps(rows, default=str)}

Write a concise answer (2–4 sentences) for a non-technical supervisor.
If there are no rows, say so and suggest a likely filter to change.
"""
    resp = client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        temperature=0.2
    )
    return resp.choices[0].message.content.strip()
