
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from model.database import create_tables

from controller.user_controller import (
    router as user_router
)

from controller.bank_controller import (
    router as bank_router
)

from controller.account_controller import (
    router as account_router
)

from controller.transfer_controller import (
    router as transfer_router
)

from controller.car_controller import (
    router as car_router
)

from controller.home_controller import (
    router as home_router
)

from controller.logs_controller import (
    router as logs_router
)

from controller.admin_controller import (
    router as admin_router
)


create_tables()


app = FastAPI(
    title="Havaleh API",
    description="Asset and Account Management System",
    version="1.0.0"
)


app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


app.include_router(user_router)
app.include_router(bank_router)
app.include_router(account_router)
app.include_router(transfer_router)
app.include_router(car_router)
app.include_router(home_router)
app.include_router(logs_router)
app.include_router(admin_router)


@app.get("/")
def root():
    return {
        "message": "Havaleh API is running"
    }
