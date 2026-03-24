from fastapi import FastAPI
from app.api.endpoints import product_analysis

app = FastAPI(title="电商商品数据分析Agent", version="1.0")

app.include_router(product_analysis.router)

@app.get("/")
def root():
    return {"message": "电商商品数据分析Agent API"}