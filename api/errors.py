from fastapi import HTTPException

class ItemNotFoundException(Exception):
    pass

def handle_item_not_found_exception(e: ItemNotFoundException):
    return HTTPException(status_code=404, detail=str(e))

def handle_generic_exception(e: Exception):
    return HTTPException(status_code=500, detail="Internal Server Error")