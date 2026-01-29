from fastapi import APIRouter, Depends

from app.api.ocr import r_ocr, r_ocr_img, r_ocr_txt, r_tesserat
from app.utils.u_auth_py import authent

ocrRouter = APIRouter()

ocrRouter.include_router(r_ocr.router, prefix="/ocr",  tags=["OCR"], dependencies=[Depends(authent)])
ocrRouter.include_router(r_ocr_img.router,   prefix="/img",  tags=["OCR_IMG"], dependencies=[Depends(authent)])
ocrRouter.include_router(r_ocr_txt.router, prefix="/txt",  tags=["OCR_Text"], dependencies=[Depends(authent)])
ocrRouter.include_router(r_tesserat.router, prefix="/tesserat",  tags=["Tesserat"], dependencies=[Depends(authent)])


# from fastapi import APIRouter, Depends

# from app.utils.u_auth_py import authent
# from app.api.ocr import r_ocr

# router = APIRouter()

# router.include_router(r_ocr.router,  tags=["OCR: OCR"] , dependencies=[Depends(authent)])

# # router.include_router(r_ocr_txt.router,  prefix="/ocr_txt", tags=["OCR: Text"] , dependencies=[Depends(authent)])
# # router.include_router(r_ocr_img.router,  prefix="/ocr_img", tags=["OCR: Image"], dependencies=[Depends(authent)])

# @router.get("/")
# def root(): return {"r_ocr": "OCR Setup"}
