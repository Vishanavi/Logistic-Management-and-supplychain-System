#include <iostream>
#include <vector>
#include <queue>
#include <map>
#include <string>
#include <limits>
#include <algorithm>
#include <sstream>
#include <fstream>
#include <json/json.h>

using namespace std;

// Structure to represent a node in the graph
struct Node {
    string id;
    string name;
    double x, y;
    
    Node(string id, string name, double x, double y) 
        : id(id), name(name), x(x), y(y) {}
};

// Structure to represent an edge in the graph
struct Edge {
    string from, to;
    double distance;
    
    Edge(string from, string to, double distance) 
        : from(from), to(to), distance(distance) {}
};

// Structure for Dijkstra's algorithm
struct DijkstraNode {
    string id;
    double distance;
    string previous;
    
    DijkstraNode(string id, double distance, string previous) 
        : id(id), distance(distance), previous(previous) {}
    
    bool operator>(const DijkstraNode& other) const {
        return distance > other.distance;
    }
};

class RoutingEngine {
private:
    map<string, Node> nodes;
    map<string, vector<pair<string, double>>> adjacencyList;
    
public:
    // Add a node to the graph
    void addNode(const string& id, const string& name, double x, double y) {
        nodes[id] = Node(id, name, x, y);
        adjacencyList[id] = vector<pair<string, double>>();
    }
    
    // Add an edge to the graph
    void addEdge(const string& from, const string& to, double distance) {
        adjacencyList[from].push_back({to, distance});
        adjacencyList[to].push_back({from, distance}); // Undirected graph
    }
    
    // Calculate distance between two points using Euclidean distance
    double calculateDistance(const Node& a, const Node& b) {
        double dx = a.x - b.x;
        double dy = a.y - b.y;
        return sqrt(dx*dx + dy*dy);
    }
    
    // Dijkstra's algorithm for shortest path
    vector<string> findShortestPath(const string& start, const string& end) {
        if (nodes.find(start) == nodes.end() || nodes.find(end) == nodes.end()) {
            return vector<string>();
        }
        
        map<string, double> distances;
        map<string, string> previous;
        priority_queue<DijkstraNode, vector<DijkstraNode>, greater<DijkstraNode>> pq;
        
        // Initialize distances
        for (const auto& node : nodes) {
            distances[node.first] = numeric_limits<double>::infinity();
        }
        distances[start] = 0;
        
        pq.push(DijkstraNode(start, 0, ""));
        
        while (!pq.empty()) {
            DijkstraNode current = pq.top();
            pq.pop();
            
            if (current.distance > distances[current.id]) {
                continue;
            }
            
            if (current.id == end) {
                break;
            }
            
            for (const auto& neighbor : adjacencyList[current.id]) {
                string neighborId = neighbor.first;
                double weight = neighbor.second;
                double newDistance = current.distance + weight;
                
                if (newDistance < distances[neighborId]) {
                    distances[neighborId] = newDistance;
                    previous[neighborId] = current.id;
                    pq.push(DijkstraNode(neighborId, newDistance, current.id));
                }
            }
        }
        
        // Reconstruct path
        vector<string> path;
        string current = end;
        while (!current.empty()) {
            path.push_back(current);
            current = previous[current];
        }
        reverse(path.begin(), path.end());
        
        return path;
    }
    
    // A* algorithm for pathfinding with heuristic
    vector<string> findPathAStar(const string& start, const string& end) {
        if (nodes.find(start) == nodes.end() || nodes.find(end) == nodes.end()) {
            return vector<string>();
        }
        
        map<string, double> gScore;
        map<string, double> fScore;
        map<string, string> cameFrom;
        priority_queue<pair<double, string>, vector<pair<double, string>>, greater<pair<double, string>>> openSet;
        
        // Initialize scores
        for (const auto& node : nodes) {
            gScore[node.first] = numeric_limits<double>::infinity();
            fScore[node.first] = numeric_limits<double>::infinity();
        }
        
        gScore[start] = 0;
        fScore[start] = calculateDistance(nodes[start], nodes[end]);
        openSet.push({fScore[start], start});
        
        while (!openSet.empty()) {
            string current = openSet.top().second;
            openSet.pop();
            
            if (current == end) {
                // Reconstruct path
                vector<string> path;
                while (!current.empty()) {
                    path.push_back(current);
                    current = cameFrom[current];
                }
                reverse(path.begin(), path.end());
                return path;
            }
            
            for (const auto& neighbor : adjacencyList[current]) {
                string neighborId = neighbor.first;
                double weight = neighbor.second;
                double tentativeGScore = gScore[current] + weight;
                
                if (tentativeGScore < gScore[neighborId]) {
                    cameFrom[neighborId] = current;
                    gScore[neighborId] = tentativeGScore;
                    fScore[neighborId] = gScore[neighborId] + calculateDistance(nodes[neighborId], nodes[end]);
                    openSet.push({fScore[neighborId], neighborId});
                }
            }
        }
        
        return vector<string>();
    }
    
    // Load graph from JSON file
    bool loadFromJSON(const string& filename) {
        ifstream file(filename);
        if (!file.is_open()) {
            return false;
        }
        
        Json::Value root;
        Json::CharReaderBuilder builder;
        string errors;
        
        if (!Json::parseFromStream(builder, file, &root, &errors)) {
            return false;
        }
        
        // Load nodes
        if (root.isMember("nodes")) {
            const Json::Value& nodesArray = root["nodes"];
            for (const Json::Value& node : nodesArray) {
                string id = node["id"].asString();
                string name = node["name"].asString();
                double x = node["x"].asDouble();
                double y = node["y"].asDouble();
                addNode(id, name, x, y);
            }
        }
        
        // Load edges
        if (root.isMember("edges")) {
            const Json::Value& edgesArray = root["edges"];
            for (const Json::Value& edge : edgesArray) {
                string from = edge["from"].asString();
                string to = edge["to"].asString();
                double distance = edge["distance"].asDouble();
                addEdge(from, to, distance);
            }
        }
        
        return true;
    }
    
    // Create default warehouse network
    void createDefaultNetwork() {
        // Factory - Clock Tower Dehradun
        addNode("factory", "Clock Tower Factory", 0, 0);
        
        // Warehouses in Dehradun
        addNode("warehouse_clement", "Clement Town Warehouse", 5, 3);
        addNode("warehouse_prem", "Prem Nagar Warehouse", -4, 2);
        addNode("warehouse_raipur", "Raipur Warehouse", 2, -6);
        
        // Connections from factory to warehouses
        addEdge("factory", "warehouse_clement", 6.0);
        addEdge("factory", "warehouse_prem", 4.5);
        addEdge("factory", "warehouse_raipur", 6.3);
        
        // Inter-warehouse connections
        addEdge("warehouse_clement", "warehouse_prem", 9.2);
        addEdge("warehouse_clement", "warehouse_raipur", 9.4);
        addEdge("warehouse_prem", "warehouse_raipur", 8.1);
    }
    
    // Print route information
    void printRoute(const vector<string>& path) {
        if (path.empty()) {
            cout << "No path found!" << endl;
            return;
        }
        
        cout << "Route found:" << endl;
        double totalDistance = 0;
        
        for (size_t i = 0; i < path.size(); i++) {
            cout << (i + 1) << ". " << nodes[path[i]].name << " (" << path[i] << ")";
            
            if (i < path.size() - 1) {
                // Find distance to next node
                for (const auto& neighbor : adjacencyList[path[i]]) {
                    if (neighbor.first == path[i + 1]) {
                        totalDistance += neighbor.second;
                        cout << " -> " << neighbor.second << " km";
                        break;
                    }
                }
            }
            cout << endl;
        }
        
        cout << "Total distance: " << totalDistance << " km" << endl;
        cout << "Estimated travel time: " << (totalDistance / 60.0) << " hours (60 km/h)" << endl;
    }
};

int main(int argc, char* argv[]) {
    if (argc != 3) {
        cout << "Usage: " << argv[0] << " <start_point> <end_point>" << endl;
        cout << "Example: " << argv[0] << " factory warehouse_north" << endl;
        return 1;
    }
    
    string startPoint = argv[1];
    string endPoint = argv[2];
    
    RoutingEngine router;
    
    // Try to load from JSON file first
    if (!router.loadFromJSON("map_data.json")) {
        // Create default network if no JSON file
        router.createDefaultNetwork();
    }
    
    cout << "Calculating route from " << startPoint << " to " << endPoint << "..." << endl;
    cout << "Algorithm: Dijkstra's Shortest Path" << endl;
    cout << "=====================================" << endl;
    
    vector<string> path = router.findShortestPath(startPoint, endPoint);
    router.printRoute(path);
    
    cout << endl;
    cout << "Algorithm: A* Pathfinding" << endl;
    cout << "=========================" << endl;
    
    vector<string> pathAStar = router.findPathAStar(startPoint, endPoint);
    router.printRoute(pathAStar);
    
    return 0;
} 