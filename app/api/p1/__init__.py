from fastapi import APIRouter, Depends

# from app.api.p1.user_note import user_note1
from app.api.p1.tax import gst62, agency
from app.api.p1.invoice import r_inv, r_payment, r_payment_allocation, r_payment_workflow
from app.api.p1.partner import r_partners
from app.api.p1.product import category, product
# from app.api.p1.user import users
from app.api.p1.journal import r_journal
from app.api.p1.global_set import global_type, global_coa, global_transaction
from app.utils.u_auth_py import authent
from app.api.p1.expense import bill, vendor_credit, expense, bill_payment, credit_card_credit

p1rou = APIRouter()

# p1rou.include_router(user_note1.router, prefix="/user_note", tags=["p1_UserNote"], dependencies=[Depends(authent)])
p1rou.include_router(r_payment.router, tags=["p1_Payment"], dependencies=[Depends(authent)])   
p1rou.include_router(r_payment_allocation.router, prefix="/payment_allocation", tags=["p1_Payment_Allocation"], dependencies=[Depends(authent)])
p1rou.include_router(r_payment_workflow.router, prefix="/payment_workflow", tags=["p1_Payment_Workflow"], dependencies=[Depends(authent)])   

p1rou.include_router(r_inv.router, tags=["P1_Revenue"], dependencies=[Depends(authent)])   
p1rou.include_router(r_partners.router, prefix="/partner", tags=["p1_Partner"], dependencies=[Depends(authent)])   

p1rou.include_router(gst62.router, prefix="/gst62", tags=["p1_GST62"], dependencies=[Depends(authent)])
p1rou.include_router(agency.router, prefix="/agency", tags=["p1_Agency"], dependencies=[Depends(authent)])
p1rou.include_router(global_type.router, prefix="/global_type", tags=["p1_Global"], dependencies=[Depends(authent)])
p1rou.include_router(global_coa.router, prefix="/global_coa", tags=["p1_Global"], dependencies=[Depends(authent)])
p1rou.include_router(global_transaction.router, prefix="/global_transaction", tags=["p1_Global"], dependencies=[Depends(authent)])

# p1rou.include_router(users.router, prefix="/user", tags=["p1_User"], dependencies=[Depends(authent)])
p1rou.include_router(r_journal.router, prefix="/journal", tags=["p1_Journal"], dependencies=[Depends(authent)])
p1rou.include_router(category.router, prefix="/category", tags=["p1_Product"], dependencies=[Depends(authent)])
p1rou.include_router(product.router, prefix="/product", tags=["p1_Product"], dependencies=[Depends(authent)])

p1rou.include_router(bill.router, prefix="/bill", tags=["p1_Expense"], dependencies=[Depends(authent)])
p1rou.include_router(bill_payment.router, prefix="/bill_payment", tags=["p1_Expense"], dependencies=[Depends(authent)])
p1rou.include_router(vendor_credit.router, prefix="/vendor_credit", tags=["p1_Expense"], dependencies=[Depends(authent)])
p1rou.include_router(credit_card_credit.router, prefix="/credit_card_credit", tags=["p1_Expense"], dependencies=[Depends(authent)])
p1rou.include_router(expense.router, prefix="/expense", tags=["p1_Expense"], dependencies=[Depends(authent)])
