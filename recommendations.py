import json
from urllib.parse import quote_plus
from app.config import settings
from app.database import get_db
from app.services.gemini_utils import build_prompt, generate_with_gemini

URLS = {
 "amazon":"https://www.amazon.in/s?k={q}", "flipkart":"https://www.flipkart.com/search?q={q}",
 "ikea":"https://www.ikea.com/in/en/search/?q={q}", "swiggy":"https://www.swiggy.com/search?query={q}",
 "zomato":"https://www.zomato.com/", "oyo":"https://www.oyorooms.com/",
 "bookmyshow":"https://in.bookmyshow.com/explore/", "bluestone":"https://www.bluestone.com/search.html?search={q}",
 "tanishq":"https://www.tanishq.co.in/", "caratlane":"https://www.caratlane.com/"
}

def fallback(planner, payload):
    budget=float(payload["total_budget"])
    if planner=="home":
        specs=[("Lighting",.15,"LED ceiling light",["Amazon","IKEA"]),("Fans",.20,"Energy-efficient ceiling fan",["Amazon","Flipkart"]),("Furniture & decor",.65,"Room furniture and decor",["IKEA","Amazon"])]
    elif planner=="party":
        specs=[("Venue",.30,"Small event venue",["OYO"]),("Catering",.45,"Food package per guest",["Swiggy","Zomato"]),("Decoration & entertainment",.25,"Basic decor and activities",["Amazon","BookMyShow"])]
    else:
        specs=[("Jewelry",.85,"Occasion-appropriate jewelry set",["Amazon","Flipkart","Bluestone"]),("Styling",.15,"Matching accessories",["Amazon","Flipkart"])]
    groups=[]
    for category,pct,name,platforms in specs:
        allocation=round(budget*pct,2)
        groups.append({"category":category,"allocation":allocation,"items":[{"name":name,
          "description":"Demo estimate; compare current options before purchasing.",
          "estimated_price":allocation,"quantity":1,"search_terms":name,"platforms":platforms}]})
    return {"total_budget":budget,"budget_breakdown":groups,
            "remaining_budget":round(budget-sum(g["allocation"] for g in groups),2),
            "additional_suggestions":["Demo estimates only. Confirm prices, availability, delivery charges and taxes with the seller."]}

def attach_links(result):
    for group in result.get("budget_breakdown",[]):
        for item in group.get("items",[]):
            q=quote_plus(item.get("search_terms") or item.get("name") or group.get("category",""))
            links={}
            for platform in item.get("platforms",[]):
                key=platform.lower().replace(" ","")
                if key in URLS: links[platform]=URLS[key].format(q=q)
            item["shopping_links"]=links
    return result

def recommend(planner,payload,image_bytes=None,mime_type="image/jpeg"):
    mode="demo"
    if settings.gemini_api_key and not settings.use_mock_ai:
        try:
            result=generate_with_gemini(build_prompt(planner,payload,bool(image_bytes)),image_bytes,mime_type)
            mode="gemini"
        except Exception as exc:
            result=fallback(planner,payload)
            result["additional_suggestions"].insert(0,"Gemini unavailable; showing demo estimates: "+str(exc)[:150])
            mode="fallback"
    else:
        result=fallback(planner,payload)
    budget=float(payload["total_budget"])
    result["planner"]=planner
    result["total_budget"]=budget
    groups=result.get("budget_breakdown",[])
    allocated=sum(max(0,float(g.get("allocation",0) or 0)) for g in groups)
    if allocated>budget and allocated:
        factor=budget/allocated
        for g in groups: g["allocation"]=round(max(0,float(g.get("allocation",0) or 0))*factor,2)
    result["remaining_budget"]=max(0,round(budget-sum(float(g.get("allocation",0) or 0) for g in groups),2))
    result["ai_mode"]=mode
    return attach_links(result)

def save_history(user_id,planner,payload,result):
    with get_db() as db:
        db.execute("INSERT INTO history(user_id,planner,request_json,result_json) VALUES(?,?,?,?)",
                   (user_id,planner,json.dumps(payload),json.dumps(result)))

def get_history(user_id):
    with get_db() as db:
        rows=db.execute("SELECT id,planner,request_json,result_json,created_at FROM history WHERE user_id=? ORDER BY id DESC LIMIT 50",(user_id,)).fetchall()
    return [{"id":r["id"],"planner":r["planner"],"request":json.loads(r["request_json"]),
             "result":json.loads(r["result_json"]),"created_at":r["created_at"]} for r in rows]
