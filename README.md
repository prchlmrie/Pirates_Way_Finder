# Pirates Way Finder

A comprehensive indoor navigation application designed to help users navigate through building floors with accessibility features and intelligent pathfinding.

## 📂 Repository Structure

This repository uses a multi-branch structure for organized development:

- **`main`**: Main branch containing project overview and documentation
- **`develop-frontend`**: Frontend React Native application code and designs
- **`develop-backend`**: Backend FastAPI application code and designs

> **Note**: The frontend and backend source code, designs, and implementation details are located in their respective development branches (`develop-frontend` and `develop-backend`).

## 📸 Interface

![Recording 2025-11-29 090423 (online-video-cutter com) (online-video-cutter com) (2)](https://github.com/user-attachments/assets/2552d193-3606-47d6-bb38-9b9611befc20)


## 📸 Algorithm Comparison

![Recording 2025-11-29 095932 (online-video-cutter com)](https://github.com/user-attachments/assets/4449d41d-b7b3-4374-814a-38b71dbcc552)


## 🚀 Features

- **Grid-Based Pathfinding**: Efficient navigation using Dijkstra and A* algorithms
- **Accessibility Support**: Routes that avoid stairs and prefer ramps for wheelchair users
- **Real-Time Navigation**: Step-by-step instructions with distance and time estimates
- **Multi-Building Support**: Navigate across different buildings and floors
- **Admin Dashboard**: Manage nodes, edges, and building data
- **Search Functionality**: Find locations quickly with search
- **Bookmark System**: Save favorite locations for quick access

## 🏗️ Architecture

### Backend
- **Framework**: FastAPI (Python)
- **Database**: MongoDB
- **Pathfinding**: Grid-based Dijkstra and A* algorithms
- **API**: RESTful endpoints for navigation, search, and admin operations

### Frontend
- **Framework**: React Native with Expo
- **Map Library**: Leaflet
- **Navigation**: React Navigation
- **State Management**: React Context API

### Admin Panel
- **Framework**: React with TypeScript
- **Build Tool**: Vite

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- MongoDB (local or cloud instance)
- Expo CLI (for mobile development)

## 🔧 Installation

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend_pirates_way_finder
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Create a .env file with your MongoDB connection string
MONGODB_URI=your_mongodb_connection_string
```

5. Run the backend server:
```bash
python main.py
# Or
uvicorn main:app --reload
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend_pirates_way_finder
```

2. Install dependencies:
```bash
npm install
```

3. Configure API URL in `api/mapApi.js`:
```javascript
const BASE_URL = "http://your-backend-ip:8000";
```

4. Start the Expo development server:
```bash
npm start
```

### Admin Panel Setup

1. Navigate to the admin directory:
```bash
cd pirates-admin
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

## 🧮 Algorithm Details

### Pathfinding Algorithm

The application uses **grid-based pathfinding** with two algorithm options:

#### Dijkstra's Algorithm
- **Type**: Uninformed search algorithm
- **Guarantee**: Finds the shortest path
- **Use Case**: General pathfinding when optimal path is required
- **Time Complexity**: O(V log V + E) where V is vertices and E is edges

#### A* Algorithm
- **Type**: Informed search algorithm with heuristic
- **Heuristic**: Manhattan distance
- **Guarantee**: Finds the shortest path (admissible heuristic)
- **Advantage**: Faster than Dijkstra by exploring toward the goal
- **Time Complexity**: O(V log V + E) with better average case performance

### Grid System

The pathfinding operates on a grid-based system:
- **Cell Size**: Configurable pixel-to-grid conversion
- **Walkable Cells**: Predefined walkable areas loaded from JSON
- **Wall Detection**: Automatic wall detection for path optimization
- **Accessibility Mapping**: Special handling for ramps and stairs

### Accessibility Features

When accessibility mode is enabled:
- **Stair Avoidance**: Paths automatically avoid stair cells
- **Ramp Preference**: Paths prefer ramp cells when available
- **Cost Adjustment**: Ramp cells have reduced cost (0.6 vs 1.0) to encourage their use
- **Blocked Areas**: Stair cells are marked as non-walkable

### Path Optimization

The algorithm includes several optimizations:
- **Wall Penalty**: Adds cost to cells near walls to keep paths centered in corridors
- **Aesthetic Paths**: Prefers paths that stay away from walls for better visual appearance
- **Smoothing**: Path reconstruction ensures smooth navigation

## 📁 Project Structure

```
pirateswayfinder/
├── backend_pirates_way_finder/     # FastAPI backend
│   ├── app/
│   │   ├── core/                   # Core functionality
│   │   ├── models/                  # Database models
│   │   ├── routers/                 # API routes
│   │   ├── services/                # Business logic (pathfinding)
│   │   └── static/                  # Grid data and maps
│   └── main.py                      # Application entry point
├── frontend_pirates_way_finder/    # React Native mobile app
│   ├── app/                         # Expo router pages
│   ├── components/                  # React components
│   ├── api/                         # API client
│   └── utils/                       # Utility functions
└── pirates-admin/                   # Admin dashboard
    └── src/                          # React components
```

## 🔌 API Endpoints

### Pathfinding
- `POST /path/shortest` - Calculate shortest path between two points
- `GET /path/walkable-grid` - Get all walkable grid cells

### Map Data
- `GET /map/nodes` - Get all navigation nodes
- `GET /map/edges` - Get all navigation edges

### Search
- `GET /search?q={query}` - Search for locations

### Admin
- `POST /admin/nodes` - Create/update nodes
- `POST /admin/edges` - Create/update edges
- `GET /admin/audit-logs` - View audit logs

## 🧪 Testing

### Backend Tests
```bash
cd backend_pirates_way_finder
python -m pytest app/test/
```

### Frontend Tests
```bash
cd frontend_pirates_way_finder
npm test
```

## 📝 Configuration

### Grid Configuration
The grid system is configured in `backend_pirates_way_finder/app/static/grid.json`:
- Grid dimensions (width, height)
- Cell size in pixels
- Walkable cells
- Accessibility markers (ramps, stairs)

### API Configuration
Update the API base URL in `frontend_pirates_way_finder/api/mapApi.js`:
```javascript
const BASE_URL = "http://your-backend-ip:8000";
```

