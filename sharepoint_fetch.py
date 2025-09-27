from typing import Dict, List, Tuple
from urllib.parse import quote
from graph_client import GraphClient

GRAPH_ROOT = "https://graph.microsoft.com/v1.0"

def resolve_site_id(gc: GraphClient, hostname: str, site_path: str) -> str:
    # GET /sites/{hostname}:/sites/{site-path}
    url = f"{GRAPH_ROOT}/sites/{hostname}:{site_path}"
    data = gc.get(url)
    return data["id"]

def get_list_id(gc: GraphClient, site_id: str, list_title: str) -> str:
    # GET /sites/{site-id}/lists?$filter=displayName eq 'Title'
    url = f"{GRAPH_ROOT}/sites/{site_id}/lists"
    data = gc.get(url, params={"$filter": f"displayName eq '{list_title}'"})
    items = data.get("value", [])
    if not items:
        raise RuntimeError(f"List with title '{list_title}' not found")
    return items[0]["id"]

def get_all_list_items(gc: GraphClient, site_id: str, list_id: str) -> List[dict]:
    # GET /sites/{site-id}/lists/{list-id}/items?expand=fields&top=999
    url = f"{GRAPH_ROOT}/sites/{site_id}/lists/{list_id}/items"
    params = {"$expand": "fields", "$top": 999}
    results: List[dict] = []
    while True:
        data = gc.get(url, params=params)
        results.extend(data.get("value", []))
        nxt = data.get("@odata.nextLink")
        if not nxt:
            break
        # When nextLink is present, Graph has full URL; override url/params
        url, params = nxt, None
    return results

def fetch_lists(gc: GraphClient, hostname: str, site_path: str, titles: Tuple[str, str, str]):
    site_id = resolve_site_id(gc, hostname, site_path)
    e_id = get_list_id(gc, site_id, titles[0])
    t_id = get_list_id(gc, site_id, titles[1])
    r_id = get_list_id(gc, site_id, titles[2])

    employees = get_all_list_items(gc, site_id, e_id)
    teams = get_all_list_items(gc, site_id, t_id)
    reviews = get_all_list_items(gc, site_id, r_id)

    # We only care about the 'fields' object for each item
    employees_f = [x.get("fields", {}) for x in employees]
    teams_f = [x.get("fields", {}) for x in teams]
    reviews_f = [x.get("fields", {}) for x in reviews]
    return employees_f, teams_f, reviews_f
