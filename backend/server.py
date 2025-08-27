from fastapi import FastAPI, APIRouter, HTTPException, Depends, File, UploadFile, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import Response
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
import bcrypt
import json
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.colors import black, blue, grey
from reportlab.lib import colors

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Create the main app without a prefix
app = FastAPI(title="Street Food Vendor Platform", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class UserBase(BaseModel):
    email: EmailStr
    name: str
    phone: str
    address: str
    user_type: str  # 'vendor' or 'supplier'

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    phone: str
    address: str
    user_type: str
    created_at: datetime
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    supplier_id: str
    name: str
    description: str
    price: float
    unit: str  # kg, pieces, etc.
    category: str
    min_order_quantity: int
    stock_quantity: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    unit: str
    category: str
    min_order_quantity: int
    stock_quantity: int

class OrderItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    price: float
    unit: str
    total: float

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    vendor_id: str
    supplier_id: str
    items: List[OrderItem]
    subtotal: float
    tax: float
    total: float
    status: str = "pending"  # pending, confirmed, delivered, cancelled
    delivery_address: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    delivery_date: Optional[datetime] = None

class OrderCreate(BaseModel):
    supplier_id: str
    items: List[OrderItem]
    delivery_address: str
    delivery_date: Optional[datetime] = None

class SupplierInfo(BaseModel):
    name: str
    address: str
    phone: str
    email: str
    gst_number: Optional[str] = None

class VendorInfo(BaseModel):
    name: str
    address: str
    phone: str
    email: str
    business_name: Optional[str] = None

# Utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"id": user_id})
    if user is None:
        raise credentials_exception
    return User(**user)

# PDF Generation Functions
def generate_receipt_pdf(order: Order, vendor_info: VendorInfo, supplier_info: SupplierInfo):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Container for 'Flowable' objects
    story = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Header
    header_style = styles['Heading1']
    header_style.alignment = TA_CENTER
    story.append(Paragraph("TAX INVOICE", header_style))
    story.append(Spacer(1, 12))
    
    # Invoice details
    invoice_data = [
        ['Invoice No:', order.id[:8].upper()],
        ['Date:', order.created_at.strftime('%d/%m/%Y')],
        ['Status:', order.status.upper()]
    ]
    
    invoice_table = Table(invoice_data, colWidths=[2*inch, 2*inch])
    invoice_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(invoice_table)
    story.append(Spacer(1, 12))
    
    # Supplier and Vendor info
    info_data = [
        ['SUPPLIER DETAILS', 'VENDOR DETAILS'],
        [supplier_info.name, vendor_info.name],
        [supplier_info.address, vendor_info.address],
        [f'Phone: {supplier_info.phone}', f'Phone: {vendor_info.phone}'],
        [f'Email: {supplier_info.email}', f'Email: {vendor_info.email}'],
        [f'GST: {supplier_info.gst_number or "N/A"}', f'Business: {vendor_info.business_name or "N/A"}']
    ]
    
    info_table = Table(info_data, colWidths=[3*inch, 3*inch])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 12))
    
    # Items table
    items_data = [['S.No', 'Product Name', 'Quantity', 'Unit', 'Rate', 'Amount']]
    
    for i, item in enumerate(order.items, 1):
        items_data.append([
            str(i),
            item.product_name,
            str(item.quantity),
            item.unit,
            f'₹{item.price:.2f}',
            f'₹{item.total:.2f}'
        ])
    
    # Add subtotal, tax, and total
    items_data.append(['', '', '', '', 'Subtotal:', f'₹{order.subtotal:.2f}'])
    items_data.append(['', '', '', '', 'Tax (18%):', f'₹{order.tax:.2f}'])
    items_data.append(['', '', '', '', 'TOTAL:', f'₹{order.total:.2f}'])
    
    items_table = Table(items_data, colWidths=[0.5*inch, 2.5*inch, 1*inch, 1*inch, 1*inch, 1*inch])
    items_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -2), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
        ('ALIGN', (4, -3), (-1, -1), 'RIGHT'),
        ('FONTNAME', (4, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (4, -1), (-1, -1), colors.lightgrey),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 12))
    
    # Footer
    footer_text = "Thank you for your business!"
    footer_style = styles['Normal']
    footer_style.alignment = TA_CENTER
    story.append(Paragraph(footer_text, footer_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

# Authentication routes
@api_router.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    # Hash password
    hashed_password = get_password_hash(user.password)
    print(f"[DEBUG] Registering user: {user.email}, hashed_password: {hashed_password}")
    # Create user
    user_dict = user.dict()
    user_dict.pop('password')
    user_obj = User(**user_dict)
    user_doc = user_obj.dict()
    user_doc['password'] = hashed_password
    print(f"[DEBUG] User doc to insert: {user_doc}")
    await db.users.insert_one(user_doc)
    return UserResponse(**user_obj.dict())

@api_router.post("/login", response_model=Token)
async def login(user: UserLogin):
    # Find user
    db_user = await db.users.find_one({"email": user.email})
    print(f"[DEBUG] Login attempt for: {user.email}")
    if not db_user:
        print("[DEBUG] No user found with that email.")
    else:
        print(f"[DEBUG] Found user: {db_user}")
        print(f"[DEBUG] Password provided: {user.password}")
        print(f"[DEBUG] Password in DB: {db_user['password']}")
        print(f"[DEBUG] Password match: {verify_password(user.password, db_user['password'])}")
    if not db_user or not verify_password(user.password, db_user['password']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user['id']}, expires_delta=access_token_expires
    )
    user_response = UserResponse(**{k: v for k, v in db_user.items() if k != 'password'})
    return Token(access_token=access_token, token_type="bearer", user=user_response)

@api_router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse(**current_user.dict())

# Product routes
@api_router.post("/products", response_model=Product)
async def create_product(product: ProductCreate, current_user: User = Depends(get_current_user)):
    if current_user.user_type != "supplier":
        raise HTTPException(status_code=403, detail="Only suppliers can create products")
    
    product_dict = product.dict()
    product_dict['supplier_id'] = current_user.id
    product_obj = Product(**product_dict)
    
    await db.products.insert_one(product_obj.dict())
    return product_obj

@api_router.get("/products", response_model=List[Product])
async def get_products(category: Optional[str] = None):
    query = {"is_active": True}
    if category:
        query["category"] = category
    products = await db.products.find(query).to_list(1000)
    return [Product(**product) for product in products]

@api_router.get("/categories")
async def get_categories():
    categories = await db.products.distinct("category", {"is_active": True})
    return sorted(categories)

@api_router.get("/suppliers", response_model=List[UserResponse])
async def get_suppliers():
    suppliers = await db.users.find({"user_type": "supplier", "is_active": True}).to_list(1000)
    return [UserResponse(**{k: v for k, v in supplier.items() if k != 'password'}) for supplier in suppliers]

@api_router.get("/products/category/{category_name}", response_model=List[Product])
async def get_products_by_category(category_name: str, current_user: User = Depends(get_current_user)):
    """Get products by specific category"""
    if current_user.user_type != "vendor":
        raise HTTPException(status_code=403, detail="Only vendors can browse products by category")
    
    products = await db.products.find({"category": category_name, "is_active": True}).to_list(1000)
    return [Product(**product) for product in products]

# Analytics routes
@api_router.get("/analytics/vendor")
async def get_vendor_analytics(current_user: User = Depends(get_current_user)):
    """Get vendor analytics data"""
    if current_user.user_type != "vendor":
        raise HTTPException(status_code=403, detail="Only vendors can access vendor analytics")
    
    # Get orders for the last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    orders = await db.orders.find({
        "vendor_id": current_user.id,
        "created_at": {"$gte": thirty_days_ago}
    }).to_list(1000)
    
    # Daily analytics
    daily_stats = {}
    weekly_stats = {}
    monthly_stats = {}
    
    for order in orders:
        order_date = order['created_at'].date()
        week_key = order_date.strftime('%Y-W%U')
        month_key = order_date.strftime('%Y-%m')
        
        # Daily stats
        if str(order_date) not in daily_stats:
            daily_stats[str(order_date)] = {"orders": 0, "total": 0}
        daily_stats[str(order_date)]["orders"] += 1
        daily_stats[str(order_date)]["total"] += order['total']
        
        # Weekly stats
        if week_key not in weekly_stats:
            weekly_stats[week_key] = {"orders": 0, "total": 0}
        weekly_stats[week_key]["orders"] += 1
        weekly_stats[week_key]["total"] += order['total']
        
        # Monthly stats
        if month_key not in monthly_stats:
            monthly_stats[month_key] = {"orders": 0, "total": 0}
        monthly_stats[month_key]["orders"] += 1
        monthly_stats[month_key]["total"] += order['total']
    
    return {
        "daily": daily_stats,
        "weekly": weekly_stats,
        "monthly": monthly_stats,
        "total_orders": len(orders),
        "total_spent": sum(order['total'] for order in orders)
    }

@api_router.get("/analytics/supplier")
async def get_supplier_analytics(current_user: User = Depends(get_current_user)):
    """Get supplier analytics data"""
    if current_user.user_type != "supplier":
        raise HTTPException(status_code=403, detail="Only suppliers can access supplier analytics")
    
    # Get orders for the last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    orders = await db.orders.find({
        "supplier_id": current_user.id,
        "created_at": {"$gte": thirty_days_ago}
    }).to_list(1000)
    
    # Daily analytics
    daily_stats = {}
    weekly_stats = {}
    monthly_stats = {}
    
    for order in orders:
        order_date = order['created_at'].date()
        week_key = order_date.strftime('%Y-W%U')
        month_key = order_date.strftime('%Y-%m')
        
        # Daily stats
        if str(order_date) not in daily_stats:
            daily_stats[str(order_date)] = {"orders": 0, "revenue": 0}
        daily_stats[str(order_date)]["orders"] += 1
        daily_stats[str(order_date)]["revenue"] += order['total']
        
        # Weekly stats
        if week_key not in weekly_stats:
            weekly_stats[week_key] = {"orders": 0, "revenue": 0}
        weekly_stats[week_key]["orders"] += 1
        weekly_stats[week_key]["revenue"] += order['total']
        
        # Monthly stats
        if month_key not in monthly_stats:
            monthly_stats[month_key] = {"orders": 0, "revenue": 0}
        monthly_stats[month_key]["orders"] += 1
        monthly_stats[month_key]["revenue"] += order['total']
    
    return {
        "daily": daily_stats,
        "weekly": weekly_stats,
        "monthly": monthly_stats,
        "total_orders": len(orders),
        "total_revenue": sum(order['total'] for order in orders)
    }

@api_router.post("/seed-data")
async def seed_sample_data(current_user: User = Depends(get_current_user)):
    """Seed sample data for testing"""
    if current_user.user_type != "supplier":
        raise HTTPException(status_code=403, detail="Only suppliers can seed data")
    
    sample_products = [
        # Fruits
        {"name": "Fresh Apples", "description": "Premium quality red apples", "price": 120.0, "unit": "kg", "category": "Fruits", "min_order_quantity": 5, "stock_quantity": 100},
        {"name": "Bananas", "description": "Fresh yellow bananas", "price": 60.0, "unit": "kg", "category": "Fruits", "min_order_quantity": 10, "stock_quantity": 150},
        {"name": "Fresh Oranges", "description": "Juicy oranges", "price": 80.0, "unit": "kg", "category": "Fruits", "min_order_quantity": 5, "stock_quantity": 80},
        {"name": "Mangoes", "description": "Sweet alphonso mangoes", "price": 200.0, "unit": "kg", "category": "Fruits", "min_order_quantity": 3, "stock_quantity": 50},
        {"name": "Grapes", "description": "Fresh green grapes", "price": 150.0, "unit": "kg", "category": "Fruits", "min_order_quantity": 2, "stock_quantity": 40},
        
        # Vegetables
        {"name": "Fresh Tomatoes", "description": "Premium quality fresh tomatoes", "price": 45.0, "unit": "kg", "category": "Vegetables", "min_order_quantity": 5, "stock_quantity": 200},
        {"name": "Onions", "description": "Fresh red onions", "price": 35.0, "unit": "kg", "category": "Vegetables", "min_order_quantity": 10, "stock_quantity": 300},
        {"name": "Potatoes", "description": "Fresh potatoes", "price": 25.0, "unit": "kg", "category": "Vegetables", "min_order_quantity": 10, "stock_quantity": 500},
        {"name": "Bell Peppers", "description": "Colorful bell peppers", "price": 80.0, "unit": "kg", "category": "Vegetables", "min_order_quantity": 3, "stock_quantity": 60},
        {"name": "Carrots", "description": "Fresh carrots", "price": 55.0, "unit": "kg", "category": "Vegetables", "min_order_quantity": 5, "stock_quantity": 120},
        
        # Spices
        {"name": "Turmeric Powder", "description": "Pure turmeric powder", "price": 200.0, "unit": "kg", "category": "Spices", "min_order_quantity": 1, "stock_quantity": 30},
        {"name": "Red Chili Powder", "description": "Spicy red chili powder", "price": 300.0, "unit": "kg", "category": "Spices", "min_order_quantity": 1, "stock_quantity": 25},
        {"name": "Cumin Seeds", "description": "Whole cumin seeds", "price": 400.0, "unit": "kg", "category": "Spices", "min_order_quantity": 1, "stock_quantity": 20},
        {"name": "Coriander Seeds", "description": "Fresh coriander seeds", "price": 180.0, "unit": "kg", "category": "Spices", "min_order_quantity": 1, "stock_quantity": 35},
        {"name": "Garam Masala", "description": "Authentic garam masala blend", "price": 500.0, "unit": "kg", "category": "Spices", "min_order_quantity": 1, "stock_quantity": 15},
        
        # Dairy
        {"name": "Fresh Milk", "description": "Pure cow milk", "price": 55.0, "unit": "liters", "category": "Dairy", "min_order_quantity": 10, "stock_quantity": 100},
        {"name": "Paneer", "description": "Fresh cottage cheese", "price": 250.0, "unit": "kg", "category": "Dairy", "min_order_quantity": 2, "stock_quantity": 40},
        {"name": "Butter", "description": "Fresh butter", "price": 300.0, "unit": "kg", "category": "Dairy", "min_order_quantity": 1, "stock_quantity": 25},
        {"name": "Yogurt", "description": "Fresh yogurt", "price": 80.0, "unit": "kg", "category": "Dairy", "min_order_quantity": 5, "stock_quantity": 60},
        
        # Grains
        {"name": "Basmati Rice", "description": "Premium basmati rice", "price": 120.0, "unit": "kg", "category": "Grains", "min_order_quantity": 10, "stock_quantity": 200},
        {"name": "Wheat Flour", "description": "Fresh wheat flour", "price": 45.0, "unit": "kg", "category": "Grains", "min_order_quantity": 20, "stock_quantity": 500},
        {"name": "Lentils (Dal)", "description": "Mixed lentils", "price": 90.0, "unit": "kg", "category": "Grains", "min_order_quantity": 5, "stock_quantity": 150},
        {"name": "Quinoa", "description": "Organic quinoa", "price": 400.0, "unit": "kg", "category": "Grains", "min_order_quantity": 2, "stock_quantity": 30},
        
        # Beverages
        {"name": "Coconut Water", "description": "Fresh coconut water", "price": 40.0, "unit": "liters", "category": "Beverages", "min_order_quantity": 10, "stock_quantity": 80},
        {"name": "Fresh Juice", "description": "Mixed fruit juice", "price": 60.0, "unit": "liters", "category": "Beverages", "min_order_quantity": 5, "stock_quantity": 50},
        {"name": "Lassi", "description": "Traditional yogurt drink", "price": 50.0, "unit": "liters", "category": "Beverages", "min_order_quantity": 5, "stock_quantity": 40},
        
        # Bakery
        {"name": "Bread", "description": "Fresh bread loaves", "price": 35.0, "unit": "pieces", "category": "Bakery", "min_order_quantity": 10, "stock_quantity": 100},
        {"name": "Buns", "description": "Fresh burger buns", "price": 5.0, "unit": "pieces", "category": "Bakery", "min_order_quantity": 50, "stock_quantity": 200},
        {"name": "Cookies", "description": "Assorted cookies", "price": 200.0, "unit": "kg", "category": "Bakery", "min_order_quantity": 2, "stock_quantity": 30},
        
        # Oils & Condiments
        {"name": "Sunflower Oil", "description": "Pure sunflower oil", "price": 150.0, "unit": "liters", "category": "Oils & Condiments", "min_order_quantity": 5, "stock_quantity": 60},
        {"name": "Mustard Oil", "description": "Pure mustard oil", "price": 180.0, "unit": "liters", "category": "Oils & Condiments", "min_order_quantity": 3, "stock_quantity": 40},
        {"name": "Vinegar", "description": "Apple cider vinegar", "price": 120.0, "unit": "liters", "category": "Oils & Condiments", "min_order_quantity": 2, "stock_quantity": 25},
        
        # Frozen Items
        {"name": "Frozen Vegetables", "description": "Mixed frozen vegetables", "price": 100.0, "unit": "kg", "category": "Frozen Items", "min_order_quantity": 5, "stock_quantity": 80},
        {"name": "Frozen Fruits", "description": "Mixed frozen fruits", "price": 150.0, "unit": "kg", "category": "Frozen Items", "min_order_quantity": 3, "stock_quantity": 40},
        
        # Disposables
        {"name": "Paper Plates", "description": "Disposable paper plates", "price": 2.0, "unit": "pieces", "category": "Disposables", "min_order_quantity": 100, "stock_quantity": 1000},
        {"name": "Plastic Cups", "description": "Disposable plastic cups", "price": 1.5, "unit": "pieces", "category": "Disposables", "min_order_quantity": 100, "stock_quantity": 1500},
        {"name": "Food Containers", "description": "Takeaway food containers", "price": 8.0, "unit": "pieces", "category": "Disposables", "min_order_quantity": 50, "stock_quantity": 500},
    ]
    
    # Insert sample products
    for product_data in sample_products:
        product_data['supplier_id'] = current_user.id
        product_obj = Product(**product_data)
        await db.products.insert_one(product_obj.dict())
    
    return {"message": f"Successfully seeded {len(sample_products)} sample products"}

# Make /suppliers public (remove auth requirement)
@api_router.get("/suppliers", response_model=List[UserResponse])
async def get_suppliers():
    suppliers = await db.users.find({"user_type": "supplier", "is_active": True}).to_list(1000)
    return [UserResponse(**{k: v for k, v in supplier.items() if k != 'password'}) for supplier in suppliers]

# Make /products public (remove auth requirement)
@api_router.get("/products", response_model=List[Product])
async def get_products(category: Optional[str] = None):
    query = {"is_active": True}
    if category:
        query["category"] = category
    products = await db.products.find(query).to_list(1000)
    return [Product(**product) for product in products]

# Make /categories public (remove auth requirement)
@api_router.get("/categories")
async def get_categories():
    categories = await db.products.distinct("category", {"is_active": True})
    return sorted(categories)

# Order routes
@api_router.post("/orders", response_model=Order)
async def create_order(order: OrderCreate, current_user: User = Depends(get_current_user)):
    if current_user.user_type != "vendor":
        raise HTTPException(status_code=403, detail="Only vendors can create orders")
    
    # Calculate totals
    subtotal = sum(item.total for item in order.items)
    tax = subtotal * 0.18  # 18% tax
    total = subtotal + tax
    
    order_dict = order.dict()
    order_dict['vendor_id'] = current_user.id
    order_dict['subtotal'] = subtotal
    order_dict['tax'] = tax
    order_dict['total'] = total
    
    order_obj = Order(**order_dict)
    
    await db.orders.insert_one(order_obj.dict())
    return order_obj

@api_router.get("/orders", response_model=List[Order])
async def get_orders(current_user: User = Depends(get_current_user)):
    if current_user.user_type == "vendor":
        orders = await db.orders.find({"vendor_id": current_user.id}).to_list(1000)
    else:
        orders = await db.orders.find({"supplier_id": current_user.id}).to_list(1000)
    
    return [Order(**order) for order in orders]

@api_router.get("/orders/{order_id}/receipt")
async def download_receipt(order_id: str, current_user: User = Depends(get_current_user)):
    # Get order
    order = await db.orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check permissions
    if current_user.user_type == "vendor" and order['vendor_id'] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    elif current_user.user_type == "supplier" and order['supplier_id'] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get vendor and supplier info
    vendor = await db.users.find_one({"id": order['vendor_id']})
    supplier = await db.users.find_one({"id": order['supplier_id']})
    
    if not vendor or not supplier:
        raise HTTPException(status_code=404, detail="User information not found")
    
    vendor_info = VendorInfo(
        name=vendor['name'],
        address=vendor['address'],
        phone=vendor['phone'],
        email=vendor['email'],
        business_name=vendor.get('business_name')
    )
    
    supplier_info = SupplierInfo(
        name=supplier['name'],
        address=supplier['address'],
        phone=supplier['phone'],
        email=supplier['email'],
        gst_number=supplier.get('gst_number')
    )
    
    # Generate PDF
    order_obj = Order(**order)
    pdf_buffer = generate_receipt_pdf(order_obj, vendor_info, supplier_info)
    
    return Response(
        content=pdf_buffer.read(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=receipt_{order_id[:8]}.pdf"}
    )

# Include the router in the main app
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

# --- Add this block to allow running with `python server.py` ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)