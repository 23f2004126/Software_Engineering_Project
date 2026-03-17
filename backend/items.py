from fastapi import APIROUTER
router = APIRouter()
@app.get("/items")
def get_items():
  return [{"id": 1, "name": "sample item"}]
