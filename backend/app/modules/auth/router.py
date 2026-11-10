from fastapi import APIRouter

auth_router = APIRouter(prefix="/auth")



@auth_router.get("/owner/")
async def get_owner():
    pass


@auth_router.post("/login/")
async def login():
    pass


@auth_router.post("/register/")
async def register():
    pass