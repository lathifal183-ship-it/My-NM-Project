import os, uuid
os.environ["DATABASE_PATH"]="test_pocketsmart.db"
os.environ["USE_MOCK_AI"]="true"
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db
client=TestClient(app)

def setup_function():
    init_db()

def test_health():
    r=client.get("/health")
    assert r.status_code==200 and r.json()["status"]=="ok"

def test_register_login_session():
    name="test_"+uuid.uuid4().hex[:8]
    r=client.post("/register",data={"username":name,"email":name+"@example.com","password":"testpassword123"},follow_redirects=False)
    assert r.status_code==303
    assert client.get("/api/session-info").status_code==200
    client.post("/logout")
    r=client.post("/login",data={"username":name,"password":"testpassword123"},follow_redirects=False)
    assert r.status_code==303

def test_home_requires_login():
    client.cookies.clear()
    r=client.post("/api/generate-home",json={"total_budget":20000,"room_types":["Bedroom"]})
    assert r.status_code==401

def test_home_demo():
    name="demo_"+uuid.uuid4().hex[:8]
    client.post("/register",data={"username":name,"email":name+"@example.com","password":"testpassword123"})
    r=client.post("/api/generate-home",json={"total_budget":20000,"room_types":["Bedroom"],"num_lights":2,"num_fans":1,"num_furniture":1,"num_dining_tables":0,"style":"Modern","additional_requirements":""})
    assert r.status_code==200
    d=r.json()
    assert d["planner"]=="home" and d["total_budget"]==20000 and d["ai_mode"]=="demo"
    assert d["budget_breakdown"]
