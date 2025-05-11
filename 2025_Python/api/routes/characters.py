from fastapi import APIRouter
import state

router = APIRouter()


@router.get("/characters")
async def get_characters():
    return state.characters
