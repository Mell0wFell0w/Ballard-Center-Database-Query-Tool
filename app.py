import os, sqlite3, json
from dotenv import load_dotenv
from graph_client import GraphClient
from sharepoint_fetch import fetch_lists
from db_loader import load_from_sharepoint
from ai import ask_sql, synthesize_answer

def connect_db():
    mode = os.getenv("DB_MODE", "memory")
    if mode == "file":
        db_path = os.getenv("DB_FILE", "ballard_center.db")
        cx = sqlite3.connect(db_path)
    else:
        cx = sqlite3.connect(":memory:")
    cx.row_factory = sqlite3.Row
    return cx

def main():
    load_dotenv("config/.env")

    tenant = os.getenv("TENANT_ID")
    client_id = os.getenv("CLIENT_ID")
    scopes = os.getenv("GRAPH_SCOPES", "Sites.Read.All offline_access").split()

    hostname = os.getenv("SHAREPOINT_HOSTNAME")
    site_path = os.getenv("SHAREPOINT_SITE_PATH")

    employees_title = os.getenv("EMPLOYEES_LIST_TITLE", "Employee Database")
    teams_title = os.getenv("TEAMS_LIST_TITLE", "Team Info")
    reviews_title = os.getenv("REVIEWS_LIST_TITLE", "Performance Reviews")

    gc = GraphClient(tenant, client_id, scopes)
    print("Authenticating with device code...")
    gc.get_token_device_code()

    print("Fetching SharePoint lists...")
    employees_f, teams_f, reviews_f = fetch_lists(gc, hostname, site_path, (employees_title, teams_title, reviews_title))
    print(f"Employees: {len(employees_f)}  Teams: {len(teams_f)}  Reviews: {len(reviews_f)}")

    cx = connect_db()
    load_from_sharepoint(cx, employees_f, teams_f, reviews_f)

    while True:
        try:
            q = input("\nAsk a question (empty to quit): ").strip()
            if not q:
                break
            sql = ask_sql(q)
            print("\n[SQL]\n", sql)
            rows = [dict(r) for r in cx.execute(sql).fetchall()]
            print("\n[ROWS]\n", json.dumps(rows, indent=2, default=str))
            answer = synthesize_answer(q, rows)
            print("\n[ANSWER]\n", answer)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    main()
