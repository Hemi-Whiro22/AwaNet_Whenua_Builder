from fastapi import APIRouter
from fastapi import Body
from te_po.services.reo_service import translate_reo, explain_reo, pronounce_reo
from te_po.models.reo_models import ReoRequest

router = APIRouter(prefix="/reo", tags=["Reo"])


@router.post("/translate")
async def reo_translate(payload: ReoRequest = Body(...)):
    return translate_reo(payload.text)


@router.post("/explain")
async def reo_explain(payload: ReoRequest = Body(...)):
    return explain_reo(payload.text)


@router.post("/pronounce")
async def reo_pronounce(payload: ReoRequest = Body(...)):
    return pronounce_reo(payload.text)
