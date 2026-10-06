from fastapi import Depends, FastAPI, Request
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer

from api.v1.routers import router as v1_router
from core.exceptions import AppError

# cdn.jsdelivr.net (padrão do FastAPI) não abre nesta rede -> Swagger fica em
# branco. Servimos os assets pelo cdnjs.
SWAGGER_JS = "https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.17.14/swagger-ui-bundle.js"
SWAGGER_CSS = "https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.17.14/swagger-ui.css"

# auto_error=False: o esquema serve só para o botão "Authorize" do Swagger.
# Com auto_error=True ele devolveria 401 em TODAS as rotas de /api/v1 —
# inclusive /users/register e /users/login, que precisam ser públicas.
# Quando existir a dependência que valida o token de fato, é ela que entra
# no include_router dos grupos protegidos (ver ARCHITECTURE.md).
security_scheme = HTTPBearer(bearerFormat="JWT", auto_error=False)

app = FastAPI(title="Ecommerce API", docs_url=None)

app.include_router(v1_router, prefix="/api/v1", dependencies=[Depends(security_scheme)])


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Traduz qualquer AppError para resposta HTTP. Único ponto de tradução."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers,
    )


@app.get("/docs", include_in_schema=False)
def swagger_ui():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        swagger_js_url=SWAGGER_JS,
        swagger_css_url=SWAGGER_CSS,
    )
