import csv
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import subprocess
import os
import json
from collections import deque
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Ensure users.csv exists at startup
USERS_CSV = 'users.csv'
def ensure_users_csv():
    if not os.path.exists(USERS_CSV):
        with open(USERS_CSV, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'email', 'password'])
        print('users.csv created with header: id,email,password')
ensure_users_csv()

# SQLite database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///logistics.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Warehouse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    location = db.Column(db.String(100), nullable=False)  # 'factory' or warehouse name
    quantity = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    product = db.relationship('Product', backref='inventory_items')

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)  # 'customer_order', 'shipment', 'delivery'
    customer_name = db.Column(db.String(100))
    customer_email = db.Column(db.String(100))
    customer_address = db.Column(db.Text)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.id'))
    warehouse_name = db.Column(db.String(100))
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    product = db.relationship('Product', backref='orders')
    warehouse = db.relationship('Warehouse', backref='orders')

class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)  # 'map_data', 'calculated_route'
    start_point = db.Column(db.String(100))
    end_point = db.Column(db.String(100))
    route_data = db.Column(db.Text)
    data = db.Column(db.Text)  # For map data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, email, password):
        self.id = id
        self.email = email
        self.password = password

    def get_id(self):
        return self.id

# Load user from CSV
@login_manager.user_loader
def load_user(user_id):
    try:
        with open(USERS_CSV, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['id'] == user_id:
                    return User(row['id'], row['email'], row['password'])
    except Exception:
        pass
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()
        # Email format validation
        if '@' not in email or '.' not in email or 'gmail.com' not in email:
            flash('Invalid email format. Please enter a valid Gmail address.', 'error')
            return render_template('login.html')
        with open(USERS_CSV, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'email' not in row or 'password' not in row:
                    continue
                if row['email'].strip().lower() == email and row['password'].strip() == password:
                    user = User(row['id'], row['email'], row['password'])
                    login_user(user)
                    flash('Logged in successfully!', 'success')
                    return redirect(url_for('home'))
        flash('Invalid email or password', 'error')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()
        # Email format validation
        if '@' not in email or '.' not in email or 'gmail.com' not in email:
            flash('Invalid email format. Please enter a valid Gmail address.', 'error')
            return render_template('signup.html')
        # Check if email exists
        with open(USERS_CSV, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'email' not in row:
                    continue
                if row['email'].strip().lower() == email:
                    flash('Email already exists', 'error')
                    return render_template('signup.html')
        # Add new user
        with open(USERS_CSV, 'a', newline='') as f:
            writer = csv.writer(f)
            user_id = str(sum(1 for _ in open(USERS_CSV)) - 1)
            writer.writerow([user_id, email, password])
        flash('Signup successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

# Protect main pages
@app.route('/')
@login_required
def home():
    """Home page with system introduction"""
    return render_template('home.html')

@app.route('/factory')
def factory():
    """Factory dashboard showing products and shipment controls"""
    # Get products from factory inventory
    factory_inventory = Inventory.query.filter_by(location='factory').all()
    
    # Get recent shipments
    recent_shipments = Order.query.filter_by(type='shipment').order_by(Order.created_at.desc()).limit(10).all()
    
    return render_template('factory.html', 
                         inventory=factory_inventory, 
                         shipments=recent_shipments)

@app.route('/ship_to_warehouse', methods=['POST'])
def ship_to_warehouse():
    """Trigger shipment from factory to warehouse"""
    product_id = request.form.get('product_id')
    warehouse_id = request.form.get('warehouse_id')
    quantity = int(request.form.get('quantity', 1))
    
    # Get product and warehouse details
    product = Product.query.get(product_id)
    warehouse = Warehouse.query.get(warehouse_id)
    
    if product and warehouse:
        # Create shipment order
        shipment = Order(
            type='shipment',
            product_id=product.id,
            product_name=product.name,
            warehouse_id=warehouse.id,
            warehouse_name=warehouse.name,
            quantity=quantity,
            status='in_transit'
        )
        db.session.add(shipment)
        
        # Update factory inventory
        factory_inventory = Inventory.query.filter_by(product_id=product.id, location='factory').first()
        if factory_inventory:
            factory_inventory.quantity -= quantity
        else:
            factory_inventory = Inventory(product_id=product.id, location='factory', quantity=-quantity)
            db.session.add(factory_inventory)
        
        # Update warehouse inventory
        warehouse_inventory = Inventory.query.filter_by(product_id=product.id, location=warehouse.name).first()
        if warehouse_inventory:
            warehouse_inventory.quantity += quantity
        else:
            warehouse_inventory = Inventory(product_id=product.id, location=warehouse.name, quantity=quantity)
            db.session.add(warehouse_inventory)
        
        db.session.commit()
        flash(f'Shipped {quantity} {product.name} to {warehouse.name}', 'success')
    
    return redirect(url_for('factory'))

@app.route('/warehouses')
def warehouses():
    """Warehouse dashboard showing stock and dispatch controls"""
    # Get all warehouses
    warehouses_list = Warehouse.query.all()
    
    # Get inventory for each warehouse
    warehouse_inventory = {}
    for warehouse in warehouses_list:
        inventory = Inventory.query.filter_by(location=warehouse.name).all()
        warehouse_inventory[warehouse.name] = inventory
    
    # Get delivery status
    deliveries = Order.query.filter_by(type='delivery').order_by(Order.created_at.desc()).limit(20).all()
    
    return render_template('warehouses.html', 
                         warehouses=warehouses_list,
                         inventory=warehouse_inventory,
                         deliveries=deliveries)

@app.route('/dispatch_from_warehouse', methods=['POST'])
def dispatch_from_warehouse():
    """Dispatch product from warehouse to customer"""
    warehouse_id = request.form.get('warehouse_id')
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))
    customer_address = request.form.get('customer_address')
    
    warehouse = Warehouse.query.get(warehouse_id)
    product = Product.query.get(product_id)
    
    if warehouse and product:
        # Create delivery order
        delivery = Order(
            type='delivery',
            product_id=product.id,
            product_name=product.name,
            warehouse_id=warehouse.id,
            warehouse_name=warehouse.name,
            quantity=quantity,
            customer_address=customer_address,
            status='processing'
        )
        db.session.add(delivery)
        
        # Update warehouse inventory
        warehouse_inventory = Inventory.query.filter_by(product_id=product.id, location=warehouse.name).first()
        if warehouse_inventory:
            warehouse_inventory.quantity -= quantity
        
        db.session.commit()
        flash(f'Dispatched {quantity} {product.name} from {warehouse.name}', 'success')
    
    return redirect(url_for('warehouses'))

@app.route('/orders', methods=['GET', 'POST'])
def orders():
    """Order management page with form to place orders"""
    if request.method == 'POST':
        # Process new order
        customer_name = request.form.get('customer_name')
        customer_email = request.form.get('customer_email')
        customer_address = request.form.get('customer_address')
        product_id = request.form.get('product_id')
        quantity = int(request.form.get('quantity', 1))
        
        product = Product.query.get(product_id)
        
        if product:
            # Find best warehouse based on inventory and location
            warehouses_list = Warehouse.query.all()
            best_warehouse = None
            best_distance = float('inf')
            best_path = []
            
            # Load map data
            with open('real_map_with_distances.json', 'r') as f:
                map_data = json.load(f)
            nodes = {node['name']: node for node in map_data['nodes']}
            edges = map_data['edges']
            # Build adjacency list
            adj = {node['name']: [] for node in map_data['nodes']}
            for edge in edges:
                from_name = next(n['name'] for n in map_data['nodes'] if n['id'] == edge['from'])
                to_name = next(n['name'] for n in map_data['nodes'] if n['id'] == edge['to'])
                adj[from_name].append((to_name, edge['distance']))
                adj[to_name].append((from_name, edge['distance']))
            
            def dijkstra(source, target):
                import heapq
                dist = {n: float('inf') for n in adj}
                prev = {n: None for n in adj}
                dist[source] = 0
                heap = [(0, source)]
                while heap:
                    d, u = heapq.heappop(heap)
                    if u == target:
                        break
                    for v, w in adj[u]:
                        if w is None:
                            continue  # Skip edges with no distance
                        if dist[v] > d + w:
                            dist[v] = d + w
                            prev[v] = u
                            heapq.heappush(heap, (dist[v], v))
                # Reconstruct path
                path = []
                u = target
                while u:
                    path.append(u)
                    u = prev[u]
                path.reverse()
                return dist[target], path
            
            for warehouse in warehouses_list:
                inventory = Inventory.query.filter_by(product_id=product.id, location=warehouse.name).first()
                if inventory and inventory.quantity >= quantity:
                    # Calculate shortest path from warehouse to customer address
                    if warehouse.name in adj and customer_address in adj:
                        d, path = dijkstra(warehouse.name, customer_address)
                        if d < best_distance:
                            best_distance = d
                            best_warehouse = warehouse
                            best_path = path
            
            if best_warehouse:
                # Create customer order
                order = Order(
                    type='customer_order',
                    customer_name=customer_name,
                    customer_email=customer_email,
                    customer_address=customer_address,
                    product_id=product.id,
                    product_name=product.name,
                    quantity=quantity,
                    warehouse_id=best_warehouse.id,
                    warehouse_name=best_warehouse.name,
                    status='assigned'
                )
                db.session.add(order)
                db.session.commit()

                # Automatically create a delivery order for batch delivery
                delivery_order = Order(
                    type='delivery',
                    customer_name=customer_name,
                    customer_email=customer_email,
                    customer_address=customer_address,
                    product_id=product.id,
                    product_name=product.name,
                    quantity=quantity,
                    warehouse_id=best_warehouse.id,
                    warehouse_name=best_warehouse.name,
                    status='pending'
                )
                db.session.add(delivery_order)
                db.session.commit()

                flash(f'Order placed successfully! Assigned to {best_warehouse.name} (distance: {best_distance:.2f} km)', 'success')
            else:
                flash('Product not available in sufficient quantity or invalid address', 'error')
    
    # Get all orders
    orders_list = Order.query.filter_by(type='customer_order').order_by(Order.created_at.desc()).all()
    products_list = Product.query.all()
    
    return render_template('orders.html', orders=orders_list, products=products_list)

@app.route('/reports')
def reports():
    """Reports page showing summary tables"""
    # Inventory summary
    inventory_summary = db.session.query(
        Inventory.location,
        db.func.count(Inventory.id).label('total_products'),
        db.func.sum(Inventory.quantity).label('total_quantity')
    ).group_by(Inventory.location).all()
    
    # Delivery status summary
    delivery_summary = db.session.query(
        Order.status,
        db.func.count(Order.id).label('count')
    ).filter(Order.type == 'delivery').group_by(Order.status).all()
    
    # Recent routes
    recent_routes = Route.query.order_by(Route.created_at.desc()).limit(10).all()
    
    return render_template('reports.html',
                         inventory_summary=inventory_summary,
                         delivery_summary=delivery_summary,
                         recent_routes=recent_routes)

@app.route('/init_db')
def init_db():
    """Initialize database with sample data"""
    # Create all tables
    with app.app_context():
        db.create_all()
    
    # Clear existing data
    Product.query.delete()
    Warehouse.query.delete()
    Inventory.query.delete()
    Order.query.delete()
    Route.query.delete()
    
    # Sample products
    products = [
        Product(name='Laptop', category='Electronics', weight=2.5, price=49999.99),
        Product(name='Smartphone', category='Electronics', weight=0.2, price=34999.99),
        Product(name='Tablet', category='Electronics', weight=0.5, price=19999.99),
        Product(name='Headphones', category='Electronics', weight=0.3, price=9999.99),
        Product(name='Coffee Maker', category='Appliances', weight=3.0, price=4499.99),
        Product(name='Blender', category='Appliances', weight=1.5, price=2499.99)
    ]
    
    for product in products:
        db.session.add(product)
    
    db.session.commit()
    
    # Sample warehouses with Indian locations
    warehouses = [
        Warehouse(name='Clement Town Warehouse', location='Clement Town, Dehradun', capacity=10000),
        Warehouse(name='Prem Nagar Warehouse', location='Prem Nagar, Dehradun', capacity=8000),
        Warehouse(name='Raipur Warehouse', location='Raipur, Dehradun', capacity=12000)
    ]
    
    for warehouse in warehouses:
        db.session.add(warehouse)
    
    db.session.commit()
    
    # Sample inventory
    inventory_data = []
    
    # Factory inventory (Clock Tower Dehradun)
    for product in products:
        inventory_data.append(Inventory(product_id=product.id, location='factory', quantity=100))
    
    # Warehouse inventory
    for warehouse in warehouses:
        for i, product in enumerate(products):
            inventory_data.append(Inventory(product_id=product.id, location=warehouse.name, quantity=20 + (i * 5)))
    
    for inventory in inventory_data:
        db.session.add(inventory)
    
    db.session.commit()
    
    flash('Database initialized with sample data!', 'success')
    return redirect(url_for('home'))

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    """Add a new product to the system from the factory dashboard"""
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        weight = float(request.form.get('weight', 0))
        price = float(request.form.get('price', 0))
        quantity = int(request.form.get('quantity', 0))
        
        # Create product
        product = Product(name=name, category=category, weight=weight, price=price)
        db.session.add(product)
        db.session.commit()
        
        # Add to factory inventory
        inventory = Inventory(product_id=product.id, location='factory', quantity=quantity)
        db.session.add(inventory)
        db.session.commit()
        
        flash(f'Product "{name}" added to factory inventory!', 'success')
        return redirect(url_for('factory'))
    
    return render_template('add_product.html')

@app.route('/batch_delivery', methods=['GET', 'POST'])
def batch_delivery():
    """Batch delivery planner using greedy nearest neighbor algorithm"""
    warehouses = Warehouse.query.all()
    selected_warehouse_id = request.args.get('warehouse_id') or request.form.get('warehouse_id')
    orders = []
    route_result = None
    nodes = []
    edges = []
    route_path_edges = []
    
    if selected_warehouse_id:
        warehouse = Warehouse.query.get(selected_warehouse_id)
        # Get all pending or processing delivery orders for this warehouse
        orders = Order.query.filter(Order.type=='delivery', Order.warehouse_id==warehouse.id, Order.status.in_(['pending', 'processing'])).all()
        nodes = []
        edges = []
        route_path_edges = []
        if request.method == 'POST' and orders:
            # Load map data
            with open('real_map_with_distances.json', 'r') as f:
                map_data = json.load(f)
            nodes = map_data['nodes']
            edges = map_data['edges']
            # Build adjacency list
            adj = {node['name']: [] for node in map_data['nodes']}
            for edge in edges:
                from_name = next(n['name'] for n in map_data['nodes'] if n['id'] == edge['from'])
                to_name = next(n['name'] for n in map_data['nodes'] if n['id'] == edge['to'])
                adj[from_name].append((to_name, edge['distance']))
                adj[to_name].append((from_name, edge['distance']))
            def dijkstra(source, target):
                import heapq
                dist = {n: float('inf') for n in adj}
                prev = {n: None for n in adj}
                dist[source] = 0
                heap = [(0, source)]
                while heap:
                    d, u = heapq.heappop(heap)
                    if u == target:
                        break
                    for v, w in adj[u]:
                        if w is None:
                            continue  # Skip edges with no distance
                        if dist[v] > d + w:
                            dist[v] = d + w
                            prev[v] = u
                            heapq.heappush(heap, (dist[v], v))
                # Reconstruct path
                path = []
                u = target
                while u:
                    path.append(u)
                    u = prev[u]
                path.reverse()
                return dist[target], path
            # Greedy nearest neighbor
            current = warehouse.name
            remaining = [o.customer_address for o in orders]
            delivery_order = []
            total_distance = 0
            route_path_edges = []
            while remaining:
                # Find closest
                best = None
                best_dist = float('inf')
                best_path = []
                for addr in remaining:
                    if current not in adj:
                        print(f"Warning: current node '{current}' not in map nodes! Skipping.")
                        continue
                    if addr not in adj:
                        print(f"Warning: address '{addr}' not in map nodes! Skipping.")
                        continue
                    d, path = dijkstra(current, addr)
                    if d < best_dist:
                        best = addr
                        best_dist = d
                        best_path = path
                if best is None:
                    print(f"Error: No reachable address from '{current}'. Remaining: {remaining}")
                    break
                delivery_order.append({'from': current, 'to': best, 'distance': best_dist, 'path': best_path})
                # Add path edges for map visualization
                for i in range(len(best_path)-1):
                    route_path_edges.append((best_path[i], best_path[i+1]))
                total_distance += best_dist
                current = best
                if best in remaining:
                    remaining.remove(best)
                else:
                    print(f"Warning: {best} not in remaining list: {remaining}")
            route_result = {'order': delivery_order, 'total_distance': total_distance}
        elif request.method == 'POST':
            # If no orders, still load map data for map display
            with open('real_map_with_distances.json', 'r') as f:
                map_data = json.load(f)
            nodes = map_data['nodes']
            edges = map_data['edges']
    
    return render_template('batch_delivery.html', warehouses=warehouses, orders=orders, selected_warehouse_id=selected_warehouse_id, route_result=route_result, nodes=nodes, edges=edges, route_path_edges=route_path_edges)

@app.route('/complete_delivery/<int:order_id>', methods=['POST'])
def complete_delivery(order_id):
    """Mark a delivery order as completed"""
    order = Order.query.get(order_id)
    if order and order.type == 'delivery' and order.status in ['pending', 'processing', 'in_transit']:
        order.status = 'completed'
        db.session.commit()
        flash('Delivery marked as completed!', 'success')
    else:
        flash('Unable to complete delivery.', 'error')
    return redirect(url_for('warehouses'))

@app.route('/map/interactive')
def map_leaflet_view():
    """Interactive map page using Leaflet.js and OpenStreetMap"""
    with open('real_map_with_distances.json', 'r') as f:
        map_data = json.load(f)
    valid_nodes = [
        n for n in map_data['nodes']
        if isinstance(n, dict)
        and isinstance(n.get('lat'), (float, int))
        and isinstance(n.get('lon'), (float, int))
    ]
    edges = map_data['edges']
    return render_template('map_leaflet.html', nodes=valid_nodes, edges=edges)

@app.route('/complete_customer_order/<int:order_id>', methods=['POST'])
def complete_customer_order(order_id):
    """Mark a customer order as completed (shipped)"""
    order = Order.query.get(order_id)
    if order and order.type == 'customer_order' and order.status != 'shipped':
        order.status = 'shipped'
        db.session.commit()
        flash('Order marked as completed!', 'success')
    else:
        flash('Unable to complete order.', 'error')
    return redirect(url_for('orders'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000) 