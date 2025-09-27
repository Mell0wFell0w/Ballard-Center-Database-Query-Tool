import sqlite3
from typing import Iterable, Dict, Any
from schema import DDL, MAPPERS

def ensure_schema(cx: sqlite3.Connection):
    cur = cx.cursor()
    for ddl in DDL.values():
        cur.execute(ddl)
    cx.commit()

def insert_rows(cx: sqlite3.Connection, table: str, rows: Iterable[Dict[str, Any]]):
    if not rows:
        return
    cols = list(rows[0].keys())
    placeholders = ",".join(["?"] * len(cols))
    sql = f"INSERT OR REPLACE INTO {table} ({','.join(cols)}) VALUES ({placeholders})"
    data = [tuple(r.get(c) for c in cols) for r in rows]
    cx.executemany(sql, data)
    cx.commit()

def load_from_sharepoint(cx: sqlite3.Connection, employees_f, teams_f, reviews_f):
    ensure_schema(cx)

    # Map raw fields to target tables
    teams_rows = [MAPPERS["Teams"](f) for f in teams_f]
    employees_rows = [MAPPERS["Employees"](f) for f in employees_f]
    reviews_rows = [MAPPERS["PerformanceReviews"](f) for f in reviews_f]

    # Basic cleanup: drop rows missing primary keys
    teams_rows = [r for r in teams_rows if r.get("TeamID") is not None]
    employees_rows = [r for r in employees_rows if r.get("NetID")]
    reviews_rows = [r for r in reviews_rows if r.get("ReviewID")]

    insert_rows(cx, "Teams", teams_rows)
    insert_rows(cx, "Employees", employees_rows)
    insert_rows(cx, "PerformanceReviews", reviews_rows)
