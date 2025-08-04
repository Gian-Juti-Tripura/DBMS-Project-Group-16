# PharmaCare Analytics Dashboard

A comprehensive pharmaceutical data management and analytics system built with Flask and modern web technologies. This application allows you to upload, analyze, and visualize pharmaceutical data including drug information, side effects, clinical trials, and company details.

## Features

### 🔍 **Data Management**
- **File Upload**: Support for CSV and Excel files (up to 16MB)
- **Drag & Drop**: Intuitive file upload with drag-and-drop interface
- **Sample Data**: Pre-loaded sample pharmaceutical dataset for testing
- **Data Validation**: Automatic validation of uploaded files

### 📊 **Analytics & Visualization**
- **Interactive Charts**: Beautiful charts using Plotly.js
- **Drug Categories**: Pie chart showing distribution of drug categories
- **Company Analysis**: Bar chart of top pharmaceutical companies
- **Disease Categories**: Doughnut chart of disease categories
- **Side Effects**: Horizontal bar chart of most common side effects
- **Clinical Trials**: Analysis of trial status and participant distribution

### 🔎 **Search & Filter**
- **Advanced Search**: Search across all data fields
- **Category Filtering**: Filter by drugs, diseases, or companies
- **Real-time Results**: Instant search results as you type
- **Pagination**: Efficient data browsing with pagination

### 🎨 **Modern UI/UX**
- **Responsive Design**: Works perfectly on all devices
- **Bootstrap 5**: Modern, clean interface
- **Font Awesome Icons**: Beautiful iconography
- **Smooth Animations**: Enhanced user experience with CSS animations
- **Dark Theme**: Professional color scheme

## Dataset Structure

The system works with pharmaceutical datasets containing the following columns:

| Column | Description |
|--------|-------------|
| `drug name` | Name of the pharmaceutical drug |
| `side effect` (1-5) | Multiple side effect columns |
| `interacts with` (1-3) | Drug interaction information |
| `disease name` | Associated disease or condition |
| `disease category` | Category of the disease |
| `drug category` | Category of the drug |
| `product name` | Commercial product name |
| `company name` | Pharmaceutical company |
| `clinical trial title` | Title of clinical trial |
| `clinical trial start date` | Trial start date |
| `clinical trial completion date` | Trial completion date |
| `clinical trial participants` | Number of participants |
| `clinical trial status` | Trial status (Completed, Active, etc.) |
| `clinical trial condition` (1-3) | Trial conditions |
| `clinical trial address` | Trial location |
| `clinical trial institution` | Research institution |
| `clinical trial main researcher` | Principal investigator |

## Installation

### Prerequisites
- Python 3.8 or higher
- Flask (included in both versions)

### Quick Start (Simplified Version)

1. **Navigate to the project directory**
   ```bash
   cd pharmacare-analytics
   ```

2. **Install minimal dependencies**
   ```bash
   pip install --break-system-packages Flask Werkzeug
   ```

3. **Run the simplified application**
   ```bash
   python3 run_simple.py
   ```

4. **Access the dashboard**
   Open your browser and navigate to: `http://localhost:5000`

### Full Version (Advanced Features)

1. **Install all dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the full application**
   ```bash
   python app.py
   ```

**Note**: The simplified version (`app_simple.py`) works with basic Python libraries and provides core functionality. The full version includes advanced analytics with pandas and plotly.

## Usage

### 1. Loading Data

**Option A: Upload Your Own Data**
1. Click "Choose File" or drag and drop your CSV/Excel file
2. Ensure your file follows the expected column structure
3. Click "Upload File" to process the data

**Option B: Use Sample Data**
1. Click "Load Sample Data" to use the pre-loaded dataset
2. This loads a sample of pharmaceutical data for testing

### 2. Exploring Data

**Overview Cards**
- View key metrics: total records, drug categories, companies, clinical trials

**Data Table**
- Browse all pharmaceutical records with pagination
- View detailed information for each drug and associated data

**Search Functionality**
- Use the search bar to find specific drugs, diseases, or companies
- Apply category filters for targeted searches
- Clear filters to return to the full dataset

### 3. Analytics Dashboard

**Drug Categories Chart**
- Pie chart showing distribution of drug types
- Includes Antineoplastic agents, Antirheumatic agents, etc.

**Top Companies Chart**
- Bar chart of pharmaceutical companies by number of drugs
- Identifies major players in the dataset

**Disease Categories Chart**
- Doughnut chart of disease categories
- Shows distribution across Cancer, Respiratory, Neurological, etc.

**Side Effects Chart**
- Horizontal bar chart of most common side effects
- Helps identify prevalent drug side effects

**Clinical Trials Charts**
- Trial status distribution (Completed, Active, Terminated)
- Participant distribution by trial status

## API Endpoints

### Data Management
- `POST /upload` - Upload pharmaceutical data file
- `GET /load_sample` - Load sample dataset
- `GET /api/data` - Retrieve paginated data
- `GET /api/search` - Search and filter data

### Analytics
- `GET /api/analytics/drugs` - Drug and company analytics
- `GET /api/analytics/clinical_trials` - Clinical trial analytics
- `GET /api/analytics/side_effects` - Side effect analytics

## File Structure

```
pharmacare-analytics/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── sample_pharmaceutical_data.csv  # Sample dataset
├── templates/
│   └── index.html                 # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css             # Custom CSS styles
│   └── js/
│       └── app.js                # JavaScript application
└── uploads/                       # Uploaded files directory
```

## Technologies Used

### Backend
- **Flask**: Python web framework
- **Pandas**: Data processing and analysis
- **NumPy**: Numerical computing

### Frontend
- **Bootstrap 5**: CSS framework
- **Font Awesome**: Icon library
- **Plotly.js**: Interactive charting library
- **Vanilla JavaScript**: Client-side functionality

### Data Processing
- **CSV/Excel Support**: Read multiple file formats
- **Data Validation**: Ensure data integrity
- **Real-time Analytics**: Dynamic chart generation

## Sample Data

The application includes sample pharmaceutical data featuring:
- Popular drugs like Cetuximab, Etanercept, Urokinase
- Various disease categories (Cancer, Respiratory, Neurological)
- Clinical trial information with real research data
- Side effect profiles and drug interactions

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the development team.

---

**PharmaCare Analytics Dashboard** - Empowering pharmaceutical data analysis and visualization.
