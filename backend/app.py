from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api.endpoints import router as api_router

app = FastAPI(title="Equity Mirror API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Equity Mirror Backend"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)