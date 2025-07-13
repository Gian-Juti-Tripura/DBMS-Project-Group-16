# Database System Project-1: Normalization and ER Diagram Generator

**Submitted by:** Gian Juti Tripura  
**ID:** 22701073  
**Date:** July 13, 2025

## Project Goal

To develop a system where the user can input a dataset, and the system will:
- Automatically detect functional dependencies (FDs)
- Check for redundancy and normalize the dataset
- Perform lossless decomposition with dependency preservation
- Generate an optimized ER diagram and relational schema

## Features

### Phase 1: Input Processing Module
- User uploads a CSV file
- System reads attribute names and tuples
- Basic data validation and formatting

### Phase 2: Functional Dependency (FD) Detection
- Use algorithms to identify FDs from data (attribute closure)
- Display candidate keys and all discovered FDs

### Phase 3: Normalization Engine
- Normalize based on identified FDs (1NF, 2NF, 3NF, BCNF)
- Suggest optimal normal form level (3NF or BCNF)
- Ensure minimal loss of data and preserve dependencies

### Phase 4: Lossless Decomposition Check
- Apply algorithms (join dependency or attribute closure)
- Ensure all decomposed relations are lossless
- Verify dependency preservation

### Phase 5: Relational Schema Generation
- Construct relational schema with primary keys and foreign keys
- Optimize schema structure

### Phase 6: ER Diagram Generator
- Map tables, attributes, and relationships to ER components
- Auto-generate ER diagram with entities, relationships, cardinality
- Export ER Diagram as PNG / SVG / PDF

## Technologies and Tools

- **Backend:** Python (pandas, FD detection logic)
- **Frontend:** HTML, CSS, JavaScript (for visualization)
- **Database:** SQLite for internal representation
- **Visualization:** Graphviz for diagrams

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and go to `http://localhost:5000`

## Usage

1. Upload a CSV file through the web interface
2. The system will automatically detect functional dependencies
3. View the normalization results and decomposed relations
4. Download the generated ER diagram and relational schema

## Project Structure

```
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── database/             # Database modules
│   ├── __init__.py
│   ├── fd_detection.py   # Functional dependency detection
│   ├── normalization.py  # Normalization algorithms
│   ├── decomposition.py  # Lossless decomposition
│   └── schema_generator.py # Schema generation
├── static/               # Static files (CSS, JS, images)
├── templates/            # HTML templates
├── uploads/              # CSV file uploads
└── exports/              # Generated diagrams and schemas
```
