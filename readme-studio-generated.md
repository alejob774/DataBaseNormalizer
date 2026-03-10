# 📊 DataBaseNormalizer

<div align="center">

![Logo](https://raw.githubusercontent.com/alejob774/DataBaseNormalizer/main/assets/logo.png) <!-- TODO: Add project logo specific to a data normalizer -->

[![GitHub stars](https://img.shields.io/github/stars/alejob774/DataBaseNormalizer?style=for-the-badge)](https://github.com/alejob774/DataBaseNormalizer/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/alejob774/DataBaseNormalizer?style=for-the-badge)](https://github.com/alejob774/DataBaseNormalizer/network)
[![GitHub issues](https://img.shields.io/github/issues/alejob774/DataBaseNormalizer?style=for-the-badge)](https://github.com/alejob774/DataBaseNormalizer/issues)
[![GitHub license](https://img.shields.io/github/license/alejob774/DataBaseNormalizer?style=for-the-badge)](LICENSE) <!-- TODO: Add actual license file -->

**An intelligent ETL desktop application for automated inventory normalization, featuring dynamic data mapping and standardized report generation.**

</div>

## 📖 Overview

DataBaseNormalizer is a robust ETL (Extract, Transform, Load) automation tool designed to streamline the process of inventory normalization. Built with Python and a user-friendly PySide6 graphical interface, this application intelligently processes raw data files, linking them to a comprehensive system of country-specific and global dictionaries. It automates complex data mapping, including dynamic date conversions, to export standardized, high-quality reports. This tool is ideal for businesses and analysts seeking to harmonize disparate inventory data sources efficiently and accurately.

## ✨ Features

-   🎯 **ETL Automation**: Automates the entire Extract, Transform, Load process for inventory data.
-   🧠 **Intelligent Table Detection**: Smartly identifies and extracts tabular data from various file formats.
-   🔗 **Dynamic Data Mapping**: Links raw inventory data with pre-defined country-specific and global dictionaries for consistent categorization.
-   🗓️ **Automated Date Normalization**: Dynamically maps and standardizes diverse date formats within reports.
-   📈 **Standardized Report Generation**: Produces clean, consistent, and standardized reports, ready for analysis and integration.
-   💻 **Intuitive Graphical User Interface (GUI)**: Powered by PySide6, offering an easy-to-use interface for managing the normalization process.

## 🖥️ Screenshots

![Screenshot 1](path-to-screenshot-of-main-window) <!-- TODO: Add actual screenshots of the GUI -->
![Screenshot 2](path-to-screenshot-of-processing-view) <!-- TODO: Add screenshot of processing or results -->

## 🛠️ Tech Stack

**Application Runtime:**
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

**GUI Framework:**
![PySide6](https://img.shields.io/badge/PySide6-41CD52?style=for-the-badge&logo=qt&logoColor=white)

**Data Processing:**
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)

## 🚀 Quick Start

### Prerequisites
Before you begin, ensure you have the following installed:
-   **Python**: Version 3.8 or higher. You can download it from [python.org](https://www.python.org/downloads/).

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/alejob774/DataBaseNormalizer.git
    cd DataBaseNormalizer
    ```

2.  **Install dependencies**
    It is recommended to use a virtual environment.
    ```bash
    # Create a virtual environment
    python -m venv venv
    # Activate the virtual environment
    # On Windows:
    # venv\Scripts\activate
    # On macOS/Linux:
    # source venv/bin/activate

    # Install required packages
    pip install PySide6 pandas
    # If a requirements.txt file existed, it would be:
    # pip install -r requirements.txt
    ```

3.  **Data Dictionaries Setup**
    The application relies on country-specific and global dictionaries for data mapping. These are expected to be available in a structured format (e.g., CSV, Excel) that the application can read.
    -   Place your dictionary files within a designated `data/dictionaries` directory (or configure the path through the GUI).
    -   Ensure the dictionary files adhere to the expected format for columns and data types as required by the normalization logic.

### Run Application

1.  **Activate your virtual environment** (if not already active)
    ```bash
    # On Windows:
    # venv\Scripts\activate
    # On macOS/Linux:
    # source venv/bin/activate
    ```

2.  **Start the application**
    ```bash
    python app.py
    ```

    The graphical user interface will launch, allowing you to select input files, configure normalization settings, and generate reports.

## 📁 Project Structure

```
DataBaseNormalizer/
├── app.py              # Main application entry point and GUI initialization
├── core/               # Core ETL logic, data processing, table detection algorithms
│   ├── __init__.py
│   └── (e.g., etl_processor.py, table_detector.py, normalizer.py)
├── gui/                # PySide6 UI components, layouts, and event handlers
│   ├── __init__.py
│   └── (e.g., main_window.py, settings_dialog.py)
├── models/             # Data models, classes for representing inventory items, dictionaries, etc.
│   ├── __init__.py
│   └── (e.g., inventory_item.py, dictionary_entry.py)
├── assets/             # (Suggested) Directory for application icons, images, logos
│   └── logo.png
└── README.md           # This documentation file
```

## ⚙️ Configuration

The application's configuration, primarily related to input/output paths and dictionary management, is handled through the graphical user interface.

### Data Dictionaries
The effectiveness of the normalization relies on accurate and up-to-date data dictionaries.
-   Ensure your `core/dictionaries` or similar data directories contain the necessary country-specific and global mapping files. The GUI will guide you in loading and managing these.

## 🔧 Development

### Development Setup
To contribute to the DataBaseNormalizer or develop new features:

1.  Follow the **Installation** steps to set up the project and its dependencies.
2.  Open the project in your preferred Python IDE (e.g., VS Code, PyCharm).
3.  The main application logic resides in `app.py`, `core/`, and `gui/`.

### Running Tests
Currently, no explicit testing framework is configured or detected within the repository. For development, manual testing through the GUI is the primary method. It is recommended to implement unit and integration tests for core logic in future iterations.

## 🚀 Deployment

To create a standalone executable for the DataBaseNormalizer application, you can use tools like `PyInstaller`. This allows users to run the application without needing a Python environment installed.

### Creating an Executable (e.g., with PyInstaller)

1.  **Install PyInstaller**
    ```bash
    pip install pyinstaller
    ```

2.  **Generate the executable**
    Navigate to the root directory of the project (where `app.py` is located) and run:
    ```bash
    pyinstaller --onefile --windowed app.py
    ```
    -   `--onefile`: Packages everything into a single executable file.
    -   `--windowed`: Prevents a console window from appearing when the application runs (suitable for GUI apps).
    -   You might need to include additional assets (like `core` or `gui` directories, or specific data files) using PyInstaller's `--add-data` flag if they are not automatically detected.

    The executable will be generated in the `dist/` directory.

## 🤝 Contributing

We welcome contributions to enhance DataBaseNormalizer! If you're interested in improving the tool, please consider:
-   Forking the repository.
-   Creating a new branch for your feature or bug fix.
-   Submitting a pull request with a clear description of your changes.

### Development Setup for Contributors
Follow the **Quick Start** instructions to get the development environment up and running. Ensure your code adheres to Python's PEP 8 style guidelines.

## 📄 License

This project is currently without an explicit license file. Please contact the author for licensing details. <!-- TODO: Add actual license like MIT -->

## 🙏 Acknowledgments

-   **PySide6**: For providing a powerful framework for building cross-platform desktop applications with Python.
-   **Pandas**: For its invaluable data manipulation and analysis capabilities, crucial for the ETL processes.

## 📞 Support & Contact

-   🐛 Issues: For bug reports or feature requests, please use [GitHub Issues](https://github.com/alejob774/DataBaseNormalizer/issues).
-   📧 Contact: For any other inquiries, please contact [alejo.b774@example.com](mailto:alejo.b774@example.com). <!-- TODO: Add actual contact email for the author -->

---

<div align="center">

**⭐ Star this repo if you find it helpful!**

Made with ❤️ by [alejob774](https://github.com/alejob774)

</div>