from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os
from datetime import datetime
from pathlib import Path

app = FastAPI(title="Product Stock API", version="1.0.0")

# Configure CORS for Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class StockItem(BaseModel):
    license: str

class Product(BaseModel):
    id: int
    name: str
    image: str
    imagehover: Optional[str] = None
    description: str
    price: float
    delivery_method: str
    stock: List[StockItem]

# File paths - use absolute paths for Vercel
BASE_DIR = Path(__file__).parent
STOCK_FILE = BASE_DIR / "data" / "stock.json"
BACKUP_DIR = BASE_DIR / "data" / "backups"

# Ensure data directory exists
STOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

def load_stock_data():
    """Load stock data from JSON file"""
    try:
        if STOCK_FILE.exists():
            with open(STOCK_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Create default structure if file doesn't exist
            default_data = {
                "BloodStrike": [
                    {
                        "id": 1,
                        "name": "Blood Strike Account",
                        "image": "https://pic.bittopup.com/apiUpload/2ccf31c25175abf452e9766912a42c73.jpg",
                        "imagehover": "https://imgop.itemku.com/?url=https%3A%2F%2Fd1x91p7vw3vuq8.cloudfront.net%2Fitemku-upload%2F2025715%2Fbu7sesjsnbxx2ftm9kc8q_thumbnail.jpg&w=1033&q=10",
                        "description": "Best Account BloodStrike",
                        "price": 10.0,
                        "delivery_method": "instant",
                        "stock": [
                            {"license": "email@example.com:password123"},
                            {"license": "email2@example.com:password456"}
                        ]
                    }
                ],
                "Window Protection 11": [
                    {
                        "id": 2,
                        "name": "Window Protection",
                        "image": "https://pic.bittopup.com/apiUpload/2ccf31c25175abf452e9766912a42c73.jpg",
                        "imagehover": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ4NOVVkcMqtvEutXTu_StAuIwGGvO9DevFkg&s",
                        "description": "Best Window Protection",
                        "price": 30.0,
                        "delivery_method": "Waiting",
                        "stock": [
                            {"license": "email@example.com:password123"},
                            {"license": "email2@example.com:password456"},
                            {"license": "email2@example.com:password456"},
                            {"license": "email2@example.com:password456"}
                        ]
                    }
                ]
            }
            save_stock_data(default_data)
            return default_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading stock data: {str(e)}")

def save_stock_data(data: Dict[str, Any]):
    """Save stock data to JSON file with backup"""
    try:
        # Create backup
        if STOCK_FILE.exists():
            backup_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = BACKUP_DIR / f"stock_backup_{backup_time}.json"
            with open(STOCK_FILE, 'r') as original, open(backup_file, 'w') as backup:
                backup.write(original.read())
        
        # Save new data
        with open(STOCK_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving stock data: {str(e)}")

@app.get("/")
async def root():
    return {
        "message": "Product Stock API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "GET /api/products": "Get all products",
            "GET /api/products/{product_id}": "Get specific product",
            "GET /api/categories": "Get all categories",
            "GET /api/categories/{category_name}": "Get products by category",
            "GET /api/stock/{product_id}": "Get stock count for product",
            "POST /api/stock/consume/{product_id}": "Consume one stock item",
            "GET /api/dashboard": "Get dashboard statistics",
            "GET /api/health": "Health check endpoint"
        }
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        load_stock_data()
        return {
            "status": "healthy", 
            "timestamp": datetime.now().isoformat(),
            "service": "Product Stock API"
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/api/products", response_model=List[Product])
async def get_all_products():
    """Get all products from all categories"""
    try:
        stock_data = load_stock_data()
        all_products = []
        
        for category, products in stock_data.items():
            all_products.extend(products)
        
        return all_products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/{product_id}", response_model=Product)
async def get_product(product_id: int):
    """Get specific product by ID"""
    try:
        stock_data = load_stock_data()
        
        for category, products in stock_data.items():
            for product in products:
                if product["id"] == product_id:
                    return product
        
        raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/categories")
async def get_categories():
    """Get all categories"""
    try:
        stock_data = load_stock_data()
        categories = []
        
        for category_name, products in stock_data.items():
            categories.append({
                "name": category_name,
                "product_count": len(products)
            })
        
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/categories/{category_name}")
async def get_products_by_category(category_name: str):
    """Get products by category name"""
    try:
        stock_data = load_stock_data()
        
        if category_name not in stock_data:
            raise HTTPException(
                status_code=404, 
                detail=f"Category '{category_name}' not found"
            )
        
        return {
            "category": category_name,
            "products": stock_data[category_name]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stock/{product_id}")
async def get_product_stock(product_id: int):
    """Get stock count and availability for a product"""
    try:
        stock_data = load_stock_data()
        
        for category, products in stock_data.items():
            for product in products:
                if product["id"] == product_id:
                    return {
                        "product_id": product_id,
                        "product_name": product["name"],
                        "category": category,
                        "stock_count": len(product["stock"]),
                        "available": len(product["stock"]) > 0,
                        "delivery_method": product["delivery_method"]
                    }
        
        raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/stock/consume/{product_id}")
async def consume_stock_item(product_id: int):
    """Consume one stock item from a product (for purchases)"""
    try:
        stock_data = load_stock_data()
        found = False
        consumed_license = None
        
        for category, products in stock_data.items():
            for product in products:
                if product["id"] == product_id:
                    found = True
                    if product["stock"]:
                        # Remove one license from stock
                        consumed_license = product["stock"].pop(0)
                        
                        # Save updated data
                        save_stock_data(stock_data)
                        
                        return {
                            "success": True,
                            "product_id": product_id,
                            "product_name": product["name"],
                            "category": category,
                            "consumed_license": consumed_license,
                            "remaining_stock": len(product["stock"]),
                            "message": "Stock item consumed successfully"
                        }
                    else:
                        raise HTTPException(
                            status_code=400, 
                            detail=f"Product {product['name']} is out of stock"
                        )
        
        if not found:
            raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard")
async def get_dashboard_stats():
    """Get dashboard statistics for all products"""
    try:
        stock_data = load_stock_data()
        total_products = 0
        total_stock = 0
        low_stock_products = []
        
        for category, products in stock_data.items():
            total_products += len(products)
            for product in products:
                stock_count = len(product["stock"])
                total_stock += stock_count
                
                if stock_count <= 3:  # Low stock threshold
                    low_stock_products.append({
                        "id": product["id"],
                        "name": product["name"],
                        "category": category,
                        "stock_count": stock_count,
                        "price": product["price"]
                    })
        
        return {
            "total_categories": len(stock_data),
            "total_products": total_products,
            "total_stock_items": total_stock,
            "low_stock_products": low_stock_products,
            "low_stock_count": len(low_stock_products),
            "updated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# For Vercel, we need to expose the app object
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
