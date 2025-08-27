import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { ShoppingCart, TrendingUp, Package, DollarSign, Calendar, Filter, Search } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Set up axios defaults
axios.defaults.baseURL = API;

// Color palette for charts
const COLORS = ['#f97316', '#ea580c', '#dc2626', '#7c3aed', '#059669', '#0ea5e9', '#8b5cf6', '#f59e0b'];

const App = () => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [currentView, setCurrentView] = useState('landing');
  const [loading, setLoading] = useState(false);

  // Set up axios interceptor for authentication
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchUserInfo();
    }
  }, [token]);

  const fetchUserInfo = async () => {
    try {
      const response = await axios.get('/me');
      setUser(response.data);
      setCurrentView(response.data.user_type === 'vendor' ? 'vendor-dashboard' : 'supplier-dashboard');
    } catch (error) {
      console.error('Failed to fetch user info:', error);
      logout();
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    setCurrentView('landing');
  };

  const LandingPage = () => (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-red-50">
      <div className="container mx-auto px-4 py-8">
        <nav className="flex justify-between items-center mb-16">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center">
              <span className="text-white font-bold">SF</span>
            </div>
            <h1 className="text-2xl font-bold text-gray-800">StreetFood Connect</h1>
          </div>
          <div className="space-x-4">
            <button
              onClick={() => setCurrentView('login')}
              className="px-6 py-2 border border-orange-500 text-orange-500 rounded-lg hover:bg-orange-50 transition-colors"
            >
              Login
            </button>
            <button
              onClick={() => setCurrentView('register')}
              className="px-6 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors"
            >
              Register
            </button>
          </div>
        </nav>

        <div className="text-center mb-16">
          <h2 className="text-5xl font-bold text-gray-800 mb-6">
            Connect Street Food Vendors with <span className="text-orange-500">Trusted Suppliers</span>
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Build your food business with verified suppliers, get quality ingredients at competitive prices, 
            and manage your supply chain efficiently with instant invoice generation.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto mb-16">
          <div className="bg-white rounded-xl shadow-lg p-8 border border-orange-100">
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mb-4">
              <ShoppingCart className="w-6 h-6 text-orange-500" />
            </div>
            <h3 className="text-xl font-semibold text-gray-800 mb-3">For Vendors</h3>
            <ul className="text-gray-600 space-y-2 mb-6">
              <li>• Browse by categories (Fruits, Vegetables, Spices, etc.)</li>
              <li>• Compare prices and quality</li>
              <li>• Place orders and track deliveries</li>
              <li>• Generate professional invoices</li>
              <li>• View analytics and spending trends</li>
            </ul>
            <button
              onClick={() => setCurrentView('register-vendor')}
              className="w-full bg-orange-500 text-white py-3 rounded-lg hover:bg-orange-600 transition-colors"
            >
              Join as Vendor
            </button>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-8 border border-orange-100">
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mb-4">
              <Package className="w-6 h-6 text-orange-500" />
            </div>
            <h3 className="text-xl font-semibold text-gray-800 mb-3">For Suppliers</h3>
            <ul className="text-gray-600 space-y-2 mb-6">
              <li>• Reach thousands of vendors</li>
              <li>• Manage inventory by categories</li>
              <li>• Process orders seamlessly</li>
              <li>• View revenue analytics & trends</li>
              <li>• Grow your business network</li>
            </ul>
            <button
              onClick={() => setCurrentView('register-supplier')}
              className="w-full bg-orange-500 text-white py-3 rounded-lg hover:bg-orange-600 transition-colors"
            >
              Join as Supplier
            </button>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-8 max-w-2xl mx-auto">
          <h3 className="text-2xl font-semibold text-gray-800 mb-4 text-center">
            🧾 Professional Invoice Generation & Analytics
          </h3>
          <p className="text-gray-600 text-center mb-4">
            Generate GST-compliant invoices instantly and track your business performance with detailed analytics.
          </p>
          <div className="bg-orange-50 rounded-lg p-4">
            <p className="text-sm text-orange-700 font-medium">
              ✓ GST Number & Tax Calculations  ✓ Category-wise Browsing  ✓ Business Analytics  ✓ Downloadable PDF Format
            </p>
          </div>
        </div>
      </div>
    </div>
  );

  const AuthForm = ({ isLogin, userType }) => {
    const [formData, setFormData] = useState({
      email: '',
      password: '',
      name: '',
      phone: '',
      address: '',
      user_type: userType || 'vendor'
    });

    const handleSubmit = async (e) => {
      e.preventDefault();
      setLoading(true);
      try {
        const endpoint = isLogin ? '/login' : '/register';
        const response = await axios.post(endpoint, formData);
        
        if (isLogin) {
          setToken(response.data.access_token);
          localStorage.setItem('token', response.data.access_token);
          setUser(response.data.user);
        } else {
          setCurrentView('login');
        }
      } catch (error) {
        alert(error.response?.data?.detail || 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 to-red-50 flex items-center justify-center px-4">
        <div className="bg-white rounded-xl shadow-lg p-8 w-full max-w-md">
          <div className="text-center mb-6">
            <h2 className="text-2xl font-bold text-gray-800">
              {isLogin ? 'Welcome Back' : 'Create Account'}
            </h2>
            <p className="text-gray-600 mt-2">
              {isLogin ? 'Sign in to your account' : `Join as ${userType}`}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {!isLogin && (
              <>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700">Full Name</label>
                <input
                  id="name"
                  type="text"
                  name="name"
                  autoComplete="name"
                  placeholder="Full Name"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                  required
                />
                <label htmlFor="phone" className="block text-sm font-medium text-gray-700">Phone Number</label>
                <input
                  id="phone"
                  type="tel"
                  name="phone"
                  autoComplete="tel"
                  placeholder="Phone Number"
                  value={formData.phone}
                  onChange={(e) => setFormData({...formData, phone: e.target.value})}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                  required
                />
                <label htmlFor="address" className="block text-sm font-medium text-gray-700">Address</label>
                <textarea
                  id="address"
                  name="address"
                  autoComplete="street-address"
                  placeholder="Address"
                  value={formData.address}
                  onChange={(e) => setFormData({...formData, address: e.target.value})}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 h-20"
                  required
                />
              </>
            )}
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">Email Address</label>
            <input
              id="email"
              type="email"
              name="email"
              autoComplete="email"
              placeholder="Email Address"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
              required
            />
            <label htmlFor="password" className="block text-sm font-medium text-gray-700">Password</label>
            <input
              id="password"
              type="password"
              name="password"
              autoComplete="new-password"
              placeholder="Password"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
              required
            />
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-orange-500 text-white py-3 rounded-lg hover:bg-orange-600 transition-colors disabled:opacity-50"
            >
              {loading ? 'Processing...' : (isLogin ? 'Sign In' : 'Create Account')}
            </button>
          </form>

          <div className="mt-6 text-center">
            <button
              onClick={() => setCurrentView('landing')}
              className="text-orange-500 hover:text-orange-600 transition-colors"
            >
              ← Back to Home
            </button>
          </div>
        </div>
      </div>
    );
  };

  const VendorDashboard = () => {
    const [products, setProducts] = useState([]);
    const [orders, setOrders] = useState([]);
    const [suppliers, setSuppliers] = useState([]);
    const [categories, setCategories] = useState([]);
    const [analytics, setAnalytics] = useState(null);
    const [activeTab, setActiveTab] = useState('browse');
    const [selectedCategory, setSelectedCategory] = useState('all');
    const [searchTerm, setSearchTerm] = useState('');
    const [cart, setCart] = useState([]);
    const [selectedSupplier, setSelectedSupplier] = useState(null);

    useEffect(() => {
      fetchProducts();
      fetchOrders();
      fetchSuppliers();
      fetchCategories();
      fetchAnalytics();
    }, []);

    const fetchProducts = async (category = null) => {
      try {
        const endpoint = category ? `/products?category=${category}` : '/products';
        const response = await axios.get(endpoint);
        setProducts(response.data);
      } catch (error) {
        console.error('Failed to fetch products:', error);
      }
    };

    const fetchOrders = async () => {
      try {
        const response = await axios.get('/orders');
        setOrders(response.data);
      } catch (error) {
        console.error('Failed to fetch orders:', error);
      }
    };

    const fetchSuppliers = async () => {
      try {
        const response = await axios.get('/suppliers');
        setSuppliers(response.data);
      } catch (error) {
        console.error('Failed to fetch suppliers:', error);
      }
    };

    const fetchCategories = async () => {
      try {
        const response = await axios.get('/categories');
        setCategories(response.data);
      } catch (error) {
        console.error('Failed to fetch categories:', error);
      }
    };

    const fetchAnalytics = async () => {
      try {
        const response = await axios.get('/analytics/vendor');
        setAnalytics(response.data);
      } catch (error) {
        console.error('Failed to fetch analytics:', error);
      }
    };

    const handleCategoryChange = (category) => {
      setSelectedCategory(category);
      if (category === 'all') {
        fetchProducts();
      } else {
        fetchProducts(category);
      }
    };

    const addToCart = (product) => {
      const existingItem = cart.find(item => item.product_id === product.id);
      if (existingItem) {
        setCart(cart.map(item =>
          item.product_id === product.id
            ? { ...item, quantity: item.quantity + 1, total: (item.quantity + 1) * item.price }
            : item
        ));
      } else {
        setCart([...cart, {
          product_id: product.id,
          product_name: product.name,
          quantity: 1,
          price: product.price,
          unit: product.unit,
          total: product.price
        }]);
      }
    };

    const removeFromCart = (productId) => {
      setCart(cart.filter(item => item.product_id !== productId));
    };

    const updateCartQuantity = (productId, quantity) => {
      if (quantity <= 0) {
        removeFromCart(productId);
        return;
      }
      setCart(cart.map(item =>
        item.product_id === productId
          ? { ...item, quantity, total: quantity * item.price }
          : item
      ));
    };

    const placeOrder = async () => {
      if (!selectedSupplier || cart.length === 0) {
        alert('Please select a supplier and add items to cart');
        return;
      }

      try {
        const orderData = {
          supplier_id: selectedSupplier,
          items: cart,
          delivery_address: user.address
        };

        await axios.post('/orders', orderData);
        setCart([]);
        setSelectedSupplier(null);
        fetchOrders();
        fetchAnalytics();
        alert('Order placed successfully!');
      } catch (error) {
        alert('Failed to place order: ' + (error.response?.data?.detail || 'Unknown error'));
      }
    };

    const downloadReceipt = async (orderId) => {
      try {
        const response = await axios.get(`/orders/${orderId}/receipt`, {
          responseType: 'blob'
        });
        
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `receipt_${orderId.substring(0, 8)}.pdf`);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
      } catch (error) {
        alert('Failed to download receipt');
      }
    };

    const filteredProducts = products.filter(product =>
      product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      product.description.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const prepareChartData = (data, type) => {
      if (!data) return [];
      return Object.entries(data).map(([key, value]) => ({
        date: key,
        [type === 'vendor' ? 'spending' : 'revenue']: value.total || value.revenue || 0,
        orders: value.orders
      }));
    };

    const CategoryIcon = ({ category }) => {
      const iconMap = {
        'Fruits': '🍎',
        'Vegetables': '🥕',
        'Spices': '🌶️',
        'Dairy': '🥛',
        'Grains': '🌾',
        'Beverages': '🥤',
        'Bakery': '🍞',
        'Oils & Condiments': '🫒',
        'Frozen Items': '🧊',
        'Disposables': '🥤'
      };
      return <span className="text-2xl">{iconMap[category] || '📦'}</span>;
    };

    return (
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center">
                  <span className="text-white font-bold">SF</span>
                </div>
                <h1 className="text-xl font-bold text-gray-800">Vendor Dashboard</h1>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-gray-600">Welcome, {user?.name}</span>
                <button
                  onClick={logout}
                  className="px-4 py-2 text-red-600 hover:text-red-700 transition-colors"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </nav>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-white rounded-lg shadow-sm">
            <div className="border-b">
              <nav className="flex">
                <button
                  onClick={() => setActiveTab('browse')}
                  className={`px-6 py-3 font-medium ${activeTab === 'browse' ? 'text-orange-600 border-b-2 border-orange-600' : 'text-gray-600'}`}
                >
                  Browse Products
                </button>
                <button
                  onClick={() => setActiveTab('cart')}
                  className={`px-6 py-3 font-medium ${activeTab === 'cart' ? 'text-orange-600 border-b-2 border-orange-600' : 'text-gray-600'}`}
                >
                  Cart ({cart.length})
                </button>
                <button
                  onClick={() => setActiveTab('orders')}
                  className={`px-6 py-3 font-medium ${activeTab === 'orders' ? 'text-orange-600 border-b-2 border-orange-600' : 'text-gray-600'}`}
                >
                  My Orders
                </button>
                <button
                  onClick={() => setActiveTab('analytics')}
                  className={`px-6 py-3 font-medium ${activeTab === 'analytics' ? 'text-orange-600 border-b-2 border-orange-600' : 'text-gray-600'}`}
                >
                  Analytics
                </button>
              </nav>
            </div>

            <div className="p-6">
              {activeTab === 'browse' && (
                <div>
                  <div className="mb-6">
                    <div className="flex flex-col sm:flex-row gap-4 mb-4">
                      <div className="relative flex-1">
                        <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                        <input
                          type="text"
                          name="searchProducts"
                          placeholder="Search products..."
                          value={searchTerm}
                          onChange={(e) => setSearchTerm(e.target.value)}
                          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                        />
                      </div>
                      <select
                        name="category"
                        value={selectedCategory}
                        onChange={(e) => handleCategoryChange(e.target.value)}
                        className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                      >
                        <option value="all">All Categories</option>
                        {categories.map(category => (
                          <option key={category} value={category}>
                            {category}
                          </option>
                        ))}
                      </select>
                    </div>

                    {/* Category Pills */}
                    <div className="flex flex-wrap gap-2 mb-4">
                      <button
                        onClick={() => handleCategoryChange('all')}
                        className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                          selectedCategory === 'all' 
                            ? 'bg-orange-500 text-white' 
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        All Categories
                      </button>
                      {categories.map(category => (
                        <button
                          key={category}
                          onClick={() => handleCategoryChange(category)}
                          className={`px-4 py-2 rounded-full text-sm font-medium transition-colors flex items-center gap-2 ${
                            selectedCategory === category 
                              ? 'bg-orange-500 text-white' 
                              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          }`}
                        >
                          <CategoryIcon category={category} />
                          {category}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {filteredProducts.map(product => (
                      <div key={product.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                        <div className="flex items-center gap-2 mb-2">
                          <CategoryIcon category={product.category} />
                          <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                            {product.category}
                          </span>
                        </div>
                        <h3 className="font-medium text-gray-800">{product.name}</h3>
                        <p className="text-sm text-gray-600 mt-1">{product.description}</p>
                        <div className="mt-2 flex justify-between items-center">
                          <span className="text-lg font-semibold text-orange-600">
                            ₹{product.price}/{product.unit}
                          </span>
                          <span className="text-sm text-gray-500">
                            Min: {product.min_order_quantity} {product.unit}
                          </span>
                        </div>
                        <div className="mt-3 flex justify-between items-center">
                          <span className="text-sm text-gray-500">
                            Stock: {product.stock_quantity}
                          </span>
                          <button
                            onClick={() => addToCart(product)}
                            className="px-3 py-1 bg-orange-500 text-white rounded hover:bg-orange-600 transition-colors"
                          >
                            Add to Cart
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'cart' && (
                <div>
                  <h2 className="text-lg font-semibold mb-4">Shopping Cart</h2>
                  {cart.length === 0 ? (
                    <p className="text-gray-500">Your cart is empty</p>
                  ) : (
                    <div>
                      <div className="mb-4">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Select Supplier
                        </label>
                        <select
                          value={selectedSupplier || ''}
                          onChange={(e) => setSelectedSupplier(e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
                        >
                          <option value="">Choose a supplier...</option>
                          {suppliers.map(supplier => (
                            <option key={supplier.id} value={supplier.id}>
                              {supplier.name} - {supplier.address}
                            </option>
                          ))}
                        </select>
                      </div>

                      <div className="space-y-3">
                        {cart.map(item => (
                          <div key={item.product_id} className="flex items-center justify-between p-3 border rounded">
                            <div>
                              <h4 className="font-medium">{item.product_name}</h4>
                              <p className="text-sm text-gray-600">₹{item.price}/{item.unit}</p>
                            </div>
                            <div className="flex items-center space-x-2">
                              <button
                                onClick={() => updateCartQuantity(item.product_id, item.quantity - 1)}
                                className="px-2 py-1 bg-gray-200 rounded hover:bg-gray-300"
                              >
                                -
                              </button>
                              <span className="px-3 py-1 bg-gray-100 rounded">{item.quantity}</span>
                              <button
                                onClick={() => updateCartQuantity(item.product_id, item.quantity + 1)}
                                className="px-2 py-1 bg-gray-200 rounded hover:bg-gray-300"
                              >
                                +
                              </button>
                              <span className="ml-4 font-medium">₹{item.total.toFixed(2)}</span>
                              <button
                                onClick={() => removeFromCart(item.product_id)}
                                className="ml-2 px-2 py-1 bg-red-500 text-white rounded hover:bg-red-600"
                              >
                                Remove
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>

                      <div className="mt-4 pt-4 border-t">
                        <div className="text-right">
                          <p className="text-lg font-semibold">
                            Total: ₹{cart.reduce((sum, item) => sum + item.total, 0).toFixed(2)}
                          </p>
                        </div>
                        <div className="mt-4 text-right">
                          <button
                            onClick={placeOrder}
                            className="px-6 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors"
                          >
                            Place Order
                          </button>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'orders' && (
                <div>
                  <h2 className="text-lg font-semibold mb-4">My Orders</h2>
                  {orders.length === 0 ? (
                    <p className="text-gray-500">No orders yet</p>
                  ) : (
                    <div className="space-y-4">
                      {orders.map(order => (
                        <div key={order.id} className="border rounded-lg p-4">
                          <div className="flex justify-between items-start mb-3">
                            <div>
                              <h3 className="font-medium">Order #{order.id.substring(0, 8)}</h3>
                              <p className="text-sm text-gray-600">
                                {new Date(order.created_at).toLocaleDateString()}
                              </p>
                            </div>
                            <div className="text-right">
                              <span className={`px-2 py-1 rounded text-xs ${
                                order.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                                order.status === 'confirmed' ? 'bg-blue-100 text-blue-800' :
                                order.status === 'delivered' ? 'bg-green-100 text-green-800' :
                                'bg-gray-100 text-gray-800'
                              }`}>
                                {order.status.toUpperCase()}
                              </span>
                            </div>
                          </div>
                          
                          <div className="space-y-2">
                            {order.items.map((item, index) => (
                              <div key={index} className="flex justify-between text-sm">
                                <span>{item.product_name} x {item.quantity}</span>
                                <span>₹{item.total.toFixed(2)}</span>
                              </div>
                            ))}
                          </div>
                          
                          <div className="mt-3 pt-3 border-t flex justify-between items-center">
                            <div>
                              <p className="text-sm"><strong>Subtotal:</strong> ₹{order.subtotal.toFixed(2)}</p>
                              <p className="text-sm"><strong>Tax:</strong> ₹{order.tax.toFixed(2)}</p>
                              <p className="font-medium"><strong>Total:</strong> ₹{order.total.toFixed(2)}</p>
                            </div>
                            <button
                              onClick={() => downloadReceipt(order.id)}
                              className="px-4 py-2 bg-orange-500 text-white rounded hover:bg-orange-600 transition-colors"
                            >
                              Download Receipt
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'analytics' && (
                <div>
                  <h2 className="text-lg font-semibold mb-6">Vendor Analytics</h2>
                  {analytics ? (
                    <div className="space-y-6">
                      {/* Summary Cards */}
                      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <div className="bg-orange-50 rounded-lg p-4">
                          <div className="flex items-center">
                            <DollarSign className="h-8 w-8 text-orange-600" />
                            <div className="ml-4">
                              <p className="text-sm font-medium text-orange-600">Total Spent</p>
                              <p className="text-2xl font-bold text-orange-900">₹{analytics.total_spent.toFixed(2)}</p>
                            </div>
                          </div>
                        </div>
                        <div className="bg-blue-50 rounded-lg p-4">
                          <div className="flex items-center">
                            <ShoppingCart className="h-8 w-8 text-blue-600" />
                            <div className="ml-4">
                              <p className="text-sm font-medium text-blue-600">Total Orders</p>
                              <p className="text-2xl font-bold text-blue-900">{analytics.total_orders}</p>
                            </div>
                          </div>
                        </div>
                        <div className="bg-green-50 rounded-lg p-4">
                          <div className="flex items-center">
                            <TrendingUp className="h-8 w-8 text-green-600" />
                            <div className="ml-4">
                              <p className="text-sm font-medium text-green-600">Avg Order Value</p>
                              <p className="text-2xl font-bold text-green-900">
                                ₹{analytics.total_orders > 0 ? (analytics.total_spent / analytics.total_orders).toFixed(2) : 0}
                              </p>
                            </div>
                          </div>
                        </div>
                        <div className="bg-purple-50 rounded-lg p-4">
                          <div className="flex items-center">
                            <Calendar className="h-8 w-8 text-purple-600" />
                            <div className="ml-4">
                              <p className="text-sm font-medium text-purple-600">This Month</p>
                              <p className="text-2xl font-bold text-purple-900">
                                {Object.keys(analytics.monthly).length} months
                              </p>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Daily Spending Chart */}
                      <div className="bg-white rounded-lg border p-6">
                        <h3 className="text-lg font-semibold mb-4">Daily Spending Trend</h3>
                        <ResponsiveContainer width="100%" height={300}>
                          <LineChart data={prepareChartData(analytics.daily, 'vendor')}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="date" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Line type="monotone" dataKey="spending" stroke="#f97316" strokeWidth={2} />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>

                      {/* Weekly Analytics */}
                      <div className="bg-white rounded-lg border p-6">
                        <h3 className="text-lg font-semibold mb-4">Weekly Order Analysis</h3>
                        <ResponsiveContainer width="100%" height={300}>
                          <BarChart data={prepareChartData(analytics.weekly, 'vendor')}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="date" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Bar dataKey="orders" fill="#f97316" />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>

                      {/* Monthly Spending */}
                      <div className="bg-white rounded-lg border p-6">
                        <h3 className="text-lg font-semibold mb-4">Monthly Spending Overview</h3>
                        <ResponsiveContainer width="100%" height={300}>
                          <LineChart data={prepareChartData(analytics.monthly, 'vendor')}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="date" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Line type="monotone" dataKey="spending" stroke="#ea580c" strokeWidth={3} />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  ) : (
                    <p className="text-gray-500">Loading analytics...</p>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };

  const SupplierDashboard = () => {
    const [products, setProducts] = useState([]);
    const [orders, setOrders] = useState([]);
    const [analytics, setAnalytics] = useState(null);
    const [activeTab, setActiveTab] = useState('products');
    const [showAddProduct, setShowAddProduct] = useState(false);
    const [newProduct, setNewProduct] = useState({
      name: '',
      description: '',
      price: '',
      unit: 'kg',
      category: '',
      min_order_quantity: '',
      stock_quantity: ''
    });

    useEffect(() => {
      fetchProducts();
      fetchOrders();
      fetchAnalytics();
    }, []);

    const fetchProducts = async () => {
      try {
        const response = await axios.get('/products');
        setProducts(response.data);
      } catch (error) {
        console.error('Failed to fetch products:', error);
      }
    };

    const fetchOrders = async () => {
      try {
        const response = await axios.get('/orders');
        setOrders(response.data);
      } catch (error) {
        console.error('Failed to fetch orders:', error);
      }
    };

    const fetchAnalytics = async () => {
      try {
        const response = await axios.get('/analytics/supplier');
        setAnalytics(response.data);
      } catch (error) {
        console.error('Failed to fetch analytics:', error);
      }
    };

    const addProduct = async (e) => {
      e.preventDefault();
      try {
        await axios.post('/products', {
          ...newProduct,
          price: parseFloat(newProduct.price),
          min_order_quantity: parseInt(newProduct.min_order_quantity),
          stock_quantity: parseInt(newProduct.stock_quantity)
        });
        setNewProduct({
          name: '',
          description: '',
          price: '',
          unit: 'kg',
          category: '',
          min_order_quantity: '',
          stock_quantity: ''
        });
        setShowAddProduct(false);
        fetchProducts();
      } catch (error) {
        alert('Failed to add product: ' + (error.response?.data?.detail || 'Unknown error'));
      }
    };

    const seedSampleData = async () => {
      try {
        await axios.post('/seed-data');
        alert('Sample data seeded successfully!');
        fetchProducts();
      } catch (error) {
        alert('Failed to seed data: ' + (error.response?.data?.detail || 'Unknown error'));
      }
    };

    const downloadReceipt = async (orderId) => {
      try {
        const response = await axios.get(`/orders/${orderId}/receipt`, {
          responseType: 'blob'
        });
        
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `receipt_${orderId.substring(0, 8)}.pdf`);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
      } catch (error) {
        alert('Failed to download receipt');
      }
    };

    const prepareChartData = (data, type) => {
      if (!data) return [];
      return Object.entries(data).map(([key, value]) => ({
        date: key,
        revenue: value.revenue || 0,
        orders: value.orders
      }));
    };

    const categories = [
      'Fruits', 'Vegetables', 'Spices', 'Dairy', 'Grains', 'Beverages', 
      'Bakery', 'Oils & Condiments', 'Frozen Items', 'Disposables'
    ];

    return (
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center">
                  <span className="text-white font-bold">SF</span>
                </div>
                <h1 className="text-xl font-bold text-gray-800">Supplier Dashboard</h1>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-gray-600">Welcome, {user?.name}</span>
                <button
                  onClick={logout}
                  className="px-4 py-2 text-red-600 hover:text-red-700 transition-colors"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </nav>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-white rounded-lg shadow-sm">
            <div className="border-b">
              <nav className="flex">
                <button
                  onClick={() => setActiveTab('products')}
                  className={`px-6 py-3 font-medium ${activeTab === 'products' ? 'text-orange-600 border-b-2 border-orange-600' : 'text-gray-600'}`}
                >
                  My Products
                </button>
                <button
                  onClick={() => setActiveTab('orders')}
                  className={`px-6 py-3 font-medium ${activeTab === 'orders' ? 'text-orange-600 border-b-2 border-orange-600' : 'text-gray-600'}`}
                >
                  Orders
                </button>
                <button
                  onClick={() => setActiveTab('analytics')}
                  className={`px-6 py-3 font-medium ${activeTab === 'analytics' ? 'text-orange-600 border-b-2 border-orange-600' : 'text-gray-600'}`}
                >
                  Analytics
                </button>
              </nav>
            </div>

            <div className="p-6">
              {activeTab === 'products' && (
                <div>
                  <div className="flex justify-between items-center mb-4">
                    <h2 className="text-lg font-semibold">My Products</h2>
                    <div className="space-x-2">
                      <button
                        onClick={seedSampleData}
                        className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 transition-colors"
                      >
                        Seed Sample Data
                      </button>
                      <button
                        onClick={() => setShowAddProduct(true)}
                        className="px-4 py-2 bg-orange-500 text-white rounded hover:bg-orange-600 transition-colors"
                      >
                        Add Product
                      </button>
                    </div>
                  </div>

                  {showAddProduct && (
                    <div className="mb-6 p-4 border rounded-lg bg-gray-50">
                      <h3 className="font-medium mb-4">Add New Product</h3>
                      <form onSubmit={addProduct} className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <input
                          type="text"
                          name="productName"
                          placeholder="Product Name"
                          value={newProduct.name}
                          onChange={(e) => setNewProduct({...newProduct, name: e.target.value})}
                          className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-orange-500"
                          required
                        />
                        <select
                          name="productCategory"
                          value={newProduct.category}
                          onChange={(e) => setNewProduct({...newProduct, category: e.target.value})}
                          className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-orange-500"
                          required
                        >
                          <option value="">Select Category</option>
                          {categories.map(category => (
                            <option key={category} value={category}>{category}</option>
                          ))}
                        </select>
                        <input
                          type="number"
                          name="productPrice"
                          step="0.01"
                          placeholder="Price"
                          value={newProduct.price}
                          onChange={(e) => setNewProduct({...newProduct, price: e.target.value})}
                          className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-orange-500"
                          required
                        />
                        <select
                          name="productUnit"
                          value={newProduct.unit}
                          onChange={(e) => setNewProduct({...newProduct, unit: e.target.value})}
                          className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-orange-500"
                        >
                          <option value="kg">kg</option>
                          <option value="pieces">pieces</option>
                          <option value="liters">liters</option>
                          <option value="packets">packets</option>
                        </select>
                        <input
                          type="number"
                          name="minOrderQuantity"
                          placeholder="Min Order Quantity"
                          value={newProduct.min_order_quantity}
                          onChange={(e) => setNewProduct({...newProduct, min_order_quantity: e.target.value})}
                          className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-orange-500"
                          required
                        />
                        <input
                          type="number"
                          name="stockQuantity"
                          placeholder="Stock Quantity"
                          value={newProduct.stock_quantity}
                          onChange={(e) => setNewProduct({...newProduct, stock_quantity: e.target.value})}
                          className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-orange-500"
                          required
                        />
                        <textarea
                          name="productDescription"
                          placeholder="Description"
                          value={newProduct.description}
                          onChange={(e) => setNewProduct({...newProduct, description: e.target.value})}
                          className="md:col-span-2 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-orange-500"
                          rows="3"
                          required
                        />
                        <div className="md:col-span-2 flex space-x-2">
                          <button
                            type="submit"
                            className="px-4 py-2 bg-orange-500 text-white rounded hover:bg-orange-600 transition-colors"
                          >
                            Add Product
                          </button>
                          <button
                            type="button"
                            onClick={() => setShowAddProduct(false)}
                            className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400 transition-colors"
                          >
                            Cancel
                          </button>
                        </div>
                      </form>
                    </div>
                  )}

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {products.map(product => (
                      <div key={product.id} className="border rounded-lg p-4">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                            {product.category}
                          </span>
                        </div>
                        <h3 className="font-medium text-gray-800">{product.name}</h3>
                        <p className="text-sm text-gray-600 mt-1">{product.description}</p>
                        <div className="mt-2 flex justify-between items-center">
                          <span className="text-lg font-semibold text-orange-600">
                            ₹{product.price}/{product.unit}
                          </span>
                          <span className="text-sm text-gray-500">
                            Stock: {product.stock_quantity}
                          </span>
                        </div>
                        <div className="mt-2">
                          <span className="text-sm text-gray-500">
                            Min Order: {product.min_order_quantity} {product.unit}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'orders' && (
                <div>
                  <h2 className="text-lg font-semibold mb-4">Orders</h2>
                  {orders.length === 0 ? (
                    <p className="text-gray-500">No orders yet</p>
                  ) : (
                    <div className="space-y-4">
                      {orders.map(order => (
                        <div key={order.id} className="border rounded-lg p-4">
                          <div className="flex justify-between items-start mb-3">
                            <div>
                              <h3 className="font-medium">Order #{order.id.substring(0, 8)}</h3>
                              <p className="text-sm text-gray-600">
                                {new Date(order.created_at).toLocaleDateString()}
                              </p>
                            </div>
                            <div className="text-right">
                              <span className={`px-2 py-1 rounded text-xs ${
                                order.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                                order.status === 'confirmed' ? 'bg-blue-100 text-blue-800' :
                                order.status === 'delivered' ? 'bg-green-100 text-green-800' :
                                'bg-gray-100 text-gray-800'
                              }`}>
                                {order.status.toUpperCase()}
                              </span>
                            </div>
                          </div>
                          
                          <div className="space-y-2">
                            {order.items.map((item, index) => (
                              <div key={index} className="flex justify-between text-sm">
                                <span>{item.product_name} x {item.quantity}</span>
                                <span>₹{item.total.toFixed(2)}</span>
                              </div>
                            ))}
                          </div>
                          
                          <div className="mt-3 pt-3 border-t flex justify-between items-center">
                            <div>
                              <p className="text-sm"><strong>Subtotal:</strong> ₹{order.subtotal.toFixed(2)}</p>
                              <p className="text-sm"><strong>Tax:</strong> ₹{order.tax.toFixed(2)}</p>
                              <p className="font-medium"><strong>Total:</strong> ₹{order.total.toFixed(2)}</p>
                            </div>
                            <button
                              onClick={() => downloadReceipt(order.id)}
                              className="px-4 py-2 bg-orange-500 text-white rounded hover:bg-orange-600 transition-colors"
                            >
                              Download Receipt
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'analytics' && (
                <div>
                  <h2 className="text-lg font-semibold mb-6">Supplier Analytics</h2>
                  {analytics ? (
                    <div className="space-y-6">
                      {/* Summary Cards */}
                      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <div className="bg-green-50 rounded-lg p-4">
                          <div className="flex items-center">
                            <DollarSign className="h-8 w-8 text-green-600" />
                            <div className="ml-4">
                              <p className="text-sm font-medium text-green-600">Total Revenue</p>
                              <p className="text-2xl font-bold text-green-900">₹{analytics.total_revenue.toFixed(2)}</p>
                            </div>
                          </div>
                        </div>
                        <div className="bg-blue-50 rounded-lg p-4">
                          <div className="flex items-center">
                            <ShoppingCart className="h-8 w-8 text-blue-600" />
                            <div className="ml-4">
                              <p className="text-sm font-medium text-blue-600">Total Orders</p>
                              <p className="text-2xl font-bold text-blue-900">{analytics.total_orders}</p>
                            </div>
                          </div>
                        </div>
                        <div className="bg-purple-50 rounded-lg p-4">
                          <div className="flex items-center">
                            <TrendingUp className="h-8 w-8 text-purple-600" />
                            <div className="ml-4">
                              <p className="text-sm font-medium text-purple-600">Avg Order Value</p>
                              <p className="text-2xl font-bold text-purple-900">
                                ₹{analytics.total_orders > 0 ? (analytics.total_revenue / analytics.total_orders).toFixed(2) : 0}
                              </p>
                            </div>
                          </div>
                        </div>
                        <div className="bg-orange-50 rounded-lg p-4">
                          <div className="flex items-center">
                            <Calendar className="h-8 w-8 text-orange-600" />
                            <div className="ml-4">
                              <p className="text-sm font-medium text-orange-600">Active Months</p>
                              <p className="text-2xl font-bold text-orange-900">
                                {Object.keys(analytics.monthly).length}
                              </p>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Daily Revenue Chart */}
                      <div className="bg-white rounded-lg border p-6">
                        <h3 className="text-lg font-semibold mb-4">Daily Revenue Trend</h3>
                        <ResponsiveContainer width="100%" height={300}>
                          <LineChart data={prepareChartData(analytics.daily, 'supplier')}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="date" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Line type="monotone" dataKey="revenue" stroke="#059669" strokeWidth={2} />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>

                      {/* Weekly Orders */}
                      <div className="bg-white rounded-lg border p-6">
                        <h3 className="text-lg font-semibold mb-4">Weekly Order Analysis</h3>
                        <ResponsiveContainer width="100%" height={300}>
                          <BarChart data={prepareChartData(analytics.weekly, 'supplier')}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="date" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Bar dataKey="orders" fill="#059669" />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>

                      {/* Monthly Revenue */}
                      <div className="bg-white rounded-lg border p-6">
                        <h3 className="text-lg font-semibold mb-4">Monthly Revenue Overview</h3>
                        <ResponsiveContainer width="100%" height={300}>
                          <LineChart data={prepareChartData(analytics.monthly, 'supplier')}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="date" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Line type="monotone" dataKey="revenue" stroke="#047857" strokeWidth={3} />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  ) : (
                    <p className="text-gray-500">Loading analytics...</p>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Main render logic
  if (currentView === 'landing') {
    return <LandingPage />;
  } else if (currentView === 'login') {
    return <AuthForm isLogin={true} />;
  } else if (currentView === 'register') {
    return <AuthForm isLogin={false} />;
  } else if (currentView === 'register-vendor') {
    return <AuthForm isLogin={false} userType="vendor" />;
  } else if (currentView === 'register-supplier') {
    return <AuthForm isLogin={false} userType="supplier" />;
  } else if (currentView === 'vendor-dashboard' && user?.user_type === 'vendor') {
    return <VendorDashboard />;
  } else if (currentView === 'supplier-dashboard' && user?.user_type === 'supplier') {
    return <SupplierDashboard />;
  }

  return <LandingPage />;
};

export default App;