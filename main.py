from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from routers.user_router.user import router as user_router
from routers.overview_router.overview import router as overview_router
from routers.note_router.note import router as note_router

app = FastAPI()

app.include_router(user_router)
app.include_router(overview_router)
app.include_router(note_router)


app.mount("/statics", StaticFiles(directory="statics"))

# Static Pages

@app.get("/", include_in_schema=False)
async def index(request: Request):
    return FileResponse("./statics/homepage/index.html", media_type="text/html")



@app.get("/login_regist", include_in_schema=False)
async def login_regist_page(request: Request):
    return FileResponse("./statics/login_registpage/login_regist.html")



@app.get("/overview", include_in_schema=False)
async def overview_page(request: Request):
    return FileResponse("./statics/overviewpage/overview.html")



@app.get("/note/{note_id}", include_in_schema=False)
async def note_page(request: Request):
    return FileResponse("./statics/notepage/note.html")

