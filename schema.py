# Defines the normalized relational schema and how we map SharePoint fields to columns.

from typing import Dict, Any

# Target SQL tables
DDL = {
    "Teams": """
    CREATE TABLE IF NOT EXISTS Teams(
        TeamID INTEGER PRIMARY KEY,
        TeamTitle TEXT,
        SupervisorEmail TEXT
    );
    """,
    "Employees": """
    CREATE TABLE IF NOT EXISTS Employees(
        NetID TEXT PRIMARY KEY,
        FirstName TEXT,
        LastName TEXT,
        TeamID INTEGER,
        HireDate TEXT,
        Status TEXT,
        FOREIGN KEY(TeamID) REFERENCES Teams(TeamID)
    );
    """,
    "PerformanceReviews": """
    CREATE TABLE IF NOT EXISTS PerformanceReviews(
        ReviewID INTEGER PRIMARY KEY,
        NetID TEXT,
        TeamID INTEGER,
        ReviewDate TEXT,
        ScoreTotal REAL,
        RaiseEntered INTEGER,
        StayingNextSemester INTEGER,
        Feedback TEXT,
        FOREIGN KEY(NetID) REFERENCES Employees(NetID),
        FOREIGN KEY(TeamID) REFERENCES Teams(TeamID)
    );
    """
}

# Example SharePoint field mappings (adjust per your lists)
# Map raw Graph 'fields' dict -> row dict for the target table
MAPPERS = {
    "Teams": lambda f: {
        # Prefer a numeric ID field if you have one; fallback to SharePoint item id
        "TeamID": f.get("TeamID") or f.get("Id") or f.get("ID"),
        "TeamTitle": f.get("Title") or f.get("TeamTitle"),
        "SupervisorEmail": f.get("SupervisorEmail") or f.get("Supervisor Email")
    },
    "Employees": lambda f: {
        "NetID": f.get("NetID") or f.get("Title"),
        "FirstName": f.get("FirstName") or f.get("First Name"),
        "LastName": f.get("LastName") or f.get("Last Name"),
        "TeamID": f.get("TeamID") or f.get("PrimaryTeamId") or f.get("TeamLookupId"),
        "HireDate": f.get("HireDate") or f.get("Created"),
        "Status": f.get("Status") or f.get("EmploymentStatus")
    },
    "PerformanceReviews": lambda f: {
        "ReviewID": f.get("ReviewID") or f.get("Id") or f.get("ID"),
        "NetID": f.get("NetID"),
        "TeamID": f.get("TeamID") or f.get("TeamLookupId"),
        "ReviewDate": f.get("ReviewDate") or f.get("Created"),
        "ScoreTotal": f.get("ScoreTotal"),
        "RaiseEntered": f.get("RaiseEntered"),
        "StayingNextSemester": f.get("StayingNextSemester"),
        "Feedback": f.get("Feedback")
    }
}
