from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def route_check():
    return {"message": "Orders route"}

# rota criar order
# rota atualizar order (webhook? )
