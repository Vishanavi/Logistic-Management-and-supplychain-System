# Logistics Management System 🚚📦

A web-based logistics and supply chain management system built with **Flask**, **SQLite**, and **Flask-Login**.  
It allows you to manage products, warehouses, inventories, orders, deliveries, and routes efficiently — complete with user authentication.

---

## 📌 Features

### 🔐 Authentication
- **Signup & Login** using CSV-based user storage.
- Gmail-based email validation.
- Secure sessions with Flask-Login.

### 📦 Product & Inventory Management
- Add new products to the factory inventory.
- Track product quantities in **factory** and **warehouses**.
- Auto-update stock on shipments and deliveries.

### 🏢 Warehouse Operations
- Multiple warehouses with separate inventory.
- Dispatch products from warehouse to customer.
- Shipment from factory to warehouse.

### 🛒 Order Management
- Place customer orders with automatic **warehouse selection** based on:
  - Stock availability.
  - Shortest delivery route (Dijkstra's algorithm on map data).
- Auto-create linked delivery orders.

### 📊 Reports & Summaries
- Inventory summaries (total products & quantities per location).
- Delivery status summary.
- Recent calculated routes.

### 🗺️ Map & Routing
- Route optimization using **greedy nearest neighbor algorithm** for batch deliveries.
- Uses `real_map_with_distances.json` for map data.
- Interactive map with Leaflet.js.

---

## ⚙️ Tech Stack

- **Backend:** Flask, Flask-SQLAlchemy, Flask-Login
- **Database:** SQLite
- **Frontend:** HTML, CSS, Jinja2 Templates
- **Data Storage:** CSV (for users), JSON (for map data)
- **Algorithms:** Dijkstra's algorithm, Greedy nearest neighbor

---

## 📂 Project Structure

