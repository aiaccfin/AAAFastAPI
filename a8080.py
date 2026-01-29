import uvicorn

from app import main_rls
from app.config import settings

api = main_rls.create_app(settings)

if __name__ == "__main__":
    uvicorn.run("a8080:api", host="0.0.0.0", port=8080, reload=True)
