# Database System Project-1: Normalization and ER Diagram Generator

## 🎯 Project Overview

This project implements a comprehensive **Database Normalization and ER Diagram Generator** web application that automatically analyzes CSV datasets, detects functional dependencies, performs database normalization, and generates optimized ER diagrams.

**Submitted by:** MD Hasib Mia  
**ID:** 23701024  
**Date:** July 2, 2025

## 🚀 **Application is Running Successfully!**

The web application is now running at: **http://localhost:5000**

## ✨ Key Features Implemented

### Phase 1: Input Processing Module ✅
- **CSV File Upload**: Secure file upload with validation
- **Data Validation**: Automatic detection of data format and structure
- **Attribute Recognition**: Extracts column names and data types
- **Sample Data Preview**: Shows first few rows for verification

### Phase 2: Functional Dependency Detection ✅
- **Automatic FD Detection**: Uses attribute closure algorithms
- **Minimal Cover Generation**: Reduces redundant dependencies
- **Candidate Key Discovery**: Identifies all possible primary keys
- **Dependency Validation**: Ensures accuracy of detected relationships

### Phase 3: Normalization Engine ✅
- **Multi-level Normalization**: Supports 1NF, 2NF, 3NF, and BCNF
- **Synthesis Algorithm**: For 3NF normalization
- **Decomposition Algorithm**: For BCNF normalization
- **Optimal Form Recommendation**: Suggests best normal form

### Phase 4: Lossless Decomposition Check ✅
- **Chase Test Implementation**: Verifies lossless decomposition
- **Natural Join Verification**: Double-checks decomposition quality
- **Dependency Preservation**: Ensures no functional dependencies are lost
- **Quality Scoring**: Provides overall decomposition quality metrics

### Phase 5: Relational Schema Generation ✅
- **Primary Key Identification**: Automatically assigns primary keys
- **Foreign Key Detection**: Identifies referential integrity constraints
- **SQL DDL Generation**: Creates proper CREATE TABLE statements
- **Schema Optimization**: Ensures efficient database design

### Phase 6: ER Diagram Generator ✅
- **Graphviz Integration**: Professional diagram generation
- **Entity-Relationship Mapping**: Converts normalized tables to ER model
- **Cardinality Detection**: Determines relationship types
- **Multiple Export Formats**: PNG, SVG, PDF support

## 🏗️ Technical Architecture

### Backend Components
```
database/
├── fd_detection.py      # Functional dependency detection algorithms
├── normalization.py     # Database normalization engine
├── decomposition.py     # Lossless decomposition verification
└── schema_generator.py  # Schema and ER diagram generation
```

### Frontend Components
```
static/
├── css/style.css        # Modern responsive styling
└── js/main.js          # Interactive client-side functionality

templates/
├── base.html           # Base template with navigation
├── index.html          # Main application interface
├── results.html        # Detailed analysis results
├── 404.html           # Error page
└── 500.html           # Error page
```

### Core Technologies
- **Backend**: Python 3.13, Flask 3.1.1
- **Data Processing**: Pandas 2.3.1, NumPy 2.3.1
- **Visualization**: Graphviz 0.21, NetworkX 3.5
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **UI Framework**: Bootstrap 5.1.3
- **Database**: SQLite (for internal operations)

## 📊 Sample Dataset Included

The project includes `sample_data.csv` with student enrollment data containing:
- **Functional Dependencies**: student_id → student_name, course_id → course_name, etc.
- **Normalization Opportunities**: Multiple normal form violations
- **Realistic Data**: 16 tuples across 8 attributes

## 🔧 How to Use the Application

### 1. **Upload Dataset**
- Navigate to http://localhost:5000
- Click "Upload CSV File" and select your data file
- System validates and previews your data

### 2. **Analyze Functional Dependencies**
- Click "Analyze Data" to detect FDs automatically
- View discovered functional dependencies
- See candidate keys and current normal form

### 3. **Generate Normalizations**
- Choose between 3NF or BCNF normalization
- System creates optimized relation decompositions
- View lossless decomposition verification

### 4. **Create ER Diagrams**
- Generate professional ER diagrams automatically
- Download as PNG, SVG, or PDF
- Export SQL schema files

### 5. **Download Results**
- SQL DDL statements for database creation
- High-quality ER diagrams
- Detailed analysis reports

## 📈 Advanced Features

### Intelligent Analysis
- **Anomaly Detection**: Identifies data quality issues
- **Optimization Suggestions**: Recommends best practices
- **Performance Metrics**: Quality scoring for decompositions

### User Experience
- **Responsive Design**: Works on all devices
- **Progressive Loading**: Step-by-step analysis
- **Interactive Results**: Expandable sections and tooltips
- **Error Handling**: Graceful error messages and recovery

### Export Options
- **Multiple Formats**: PNG, SVG, PDF for diagrams
- **Standard SQL**: DDL compatible with major databases
- **Detailed Reports**: Comprehensive analysis documentation

## 🎨 Modern UI Design

The application features a beautiful, modern interface with:
- **Gradient Backgrounds**: Professional color schemes
- **Smooth Animations**: Enhanced user interactions
- **Responsive Layout**: Mobile-friendly design
- **Interactive Cards**: Hover effects and transitions
- **Progress Indicators**: Real-time feedback

## 📋 Algorithm Implementations

### Functional Dependency Detection
- **Attribute Closure**: Efficient FD discovery
- **Minimal Cover**: Reduces redundancy
- **Candidate Key Finding**: Comprehensive key detection

### Normalization Algorithms
- **3NF Synthesis**: Dependency-preserving decomposition
- **BCNF Decomposition**: Lossless join decomposition
- **Normal Form Checking**: Automated validation

### Quality Verification
- **Chase Test**: Mathematical lossless verification
- **Dependency Preservation**: Ensures no information loss
- **Join Reconstruction**: Validates decomposition quality

## 🚀 Running the Application

The application is currently running and ready to use:

```bash
# The app is already running at http://localhost:5000
# To restart if needed:
source venv/bin/activate
python app.py
```

## 📁 Project Structure

```
Database-Normalization-ER-Generator/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── sample_data.csv       # Sample dataset for testing
├── database/             # Core algorithm modules
│   ├── fd_detection.py
│   ├── normalization.py
│   ├── decomposition.py
│   └── schema_generator.py
├── static/               # Frontend assets
│   ├── css/style.css
│   └── js/main.js
├── templates/            # HTML templates
├── uploads/              # User uploaded files
└── exports/              # Generated diagrams and schemas
```

## 🎯 Key Achievements

✅ **Complete Implementation**: All 6 phases successfully implemented  
✅ **Advanced Algorithms**: State-of-the-art normalization techniques  
✅ **Professional UI**: Modern, responsive web interface  
✅ **Robust Testing**: Comprehensive error handling and validation  
✅ **Production Ready**: Scalable architecture and clean code  

## 🔮 Future Enhancements

- **Multiple Database Support**: MySQL, PostgreSQL integration
- **Advanced Visualizations**: Interactive diagram editing
- **Batch Processing**: Multiple file analysis
- **API Endpoints**: RESTful API for programmatic access
- **Cloud Deployment**: Docker containerization

## 🏆 Project Success

This project successfully demonstrates:
- **Deep Understanding**: Database theory and normalization
- **Technical Excellence**: Clean, efficient algorithm implementations
- **User Experience**: Intuitive, professional interface
- **Academic Rigor**: Proper theoretical foundations
- **Practical Application**: Real-world usability

---

## 🎉 **Ready to Use!**

The application is now fully functional and ready for testing. Visit **http://localhost:5000** to start analyzing your database schemas!

**For testing, use the included `sample_data.csv` file which contains student enrollment data with various functional dependencies and normalization opportunities.**