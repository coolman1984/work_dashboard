# Work Dashboard - Professional File Management Application

A modern, multi-panel file management dashboard with advanced tagging, search, and workspace persistence capabilities.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python work_dashboard.py

# Run tests
python -m unittest tests/verify_features.py
```

## 📦 Project Structure

The Work Dashboard follows a modular architecture with clear separation of concerns:

```
work_dashboard/
├── work_dashboard.py          # Main application entry point
├── README.md                  # This document
├── AGENTS.md                  # Project architecture and conventions
├── requirements.txt           # Python dependencies
├── config/                    # Configuration management
│   ├── manager.py             # ConfigManager for persistence
│   └── AGENTS.md              # Config layer documentation
├── services/                  # Business logic services
│   ├── metadata_service.py    # File tagging and metadata
│   ├── clipboard.py           # Internal file clipboard
│   ├── watchdog_service.py    # File system monitoring
│   ├── preview/               # File preview services
│   │   └── excel_preview.py   # Excel file data extraction
│   └── AGENTS.md              # Services layer documentation
├── ui/                        # User interface components
│   ├── folder_card.py         # Main file browser panel
│   ├── dashboard.py           # Alternative main window
│   ├── quick_look.py          # File preview popup
│   ├── styles.py              # Theme and color definitions
│   ├── analytics_bar.py       # Statistics display
│   └── AGENTS.md              # UI layer documentation
├── utils/                     # Shared utilities
│   ├── files.py               # File system operations
│   ├── debounce.py            # Input debouncing
│   └── AGENTS.md              # Utilities documentation
├── tests/                     # Test suite
│   ├── verify_features.py     # Feature verification tests
│   └── test_file_operations.py # File operation tests
├── icons/                     # File type icons
├── diagrams/                  # Architecture diagrams
│   ├── architecture.mmd      # System architecture
│   └── data_flow.mmd         # Data flow diagram
└── dist/                      # Built executables
```

## 🎨 Key Features

### Multi-Panel File Management
- **Flexible Layouts**: Grid, Vertical, and Horizontal arrangements
- **Dynamic Panels**: 2-9 panels with customizable sizes
- **Focus Mode**: Single panel focus for distraction-free work

### Advanced File Operations
- **Tagging System**: Color-coded tags (red, green, yellow) with notes
- **Global Search**: Instant search across all panels
- **File Previews**: Quick look functionality for various file types
- **Workspace Persistence**: Save and load complete workspace configurations

### User Experience
- **Theming**: Light/Dark mode with customizable colors
- **Font Scaling**: Adjustable font sizes (10-28pt)
- **Keyboard Shortcuts**: Efficient navigation and operations
- **Drag & Drop**: Intuitive file management

## 📊 Technical Stack

- **Language**: Python 3.8+
- **GUI Framework**: CustomTkinter (modern Tkinter wrapper)
- **File Monitoring**: Watchdog library
- **Data Persistence**: JSON-based configuration
- **Testing**: Unittest framework

## 🔧 Configuration

The application uses a JSON-based configuration system:

```json
{
  "num_panels": 6,
  "layout_mode": "G",
  "theme_name": "Dark",
  "font_size": 16,
  "1": "/path/to/folder1",
  "2": "/path/to/folder2",
  "workspaces": {
    "my_workspace": {
      "num_panels": 4,
      "layout_mode": "V",
      "paths": {"1": "/path1", "2": "/path2"}
    }
  }
}
```

## 🏗️ Architecture

The application follows a clean separation of concerns:

- **UI Layer**: CustomTkinter-based components in `ui/`
- **Services Layer**: Business logic and data operations in `services/`
- **Config Layer**: Persistence and settings management in `config/`
- **Utils Layer**: Shared utilities and helpers in `utils/`

## 📈 Development Workflow

1. **Make changes** to the codebase following the conventions in `AGENTS.md`
2. **Test** your changes with `python -m unittest tests/verify_features.py`
3. **Run** the application with `python work_dashboard.py`
4. **Document** new features in this README

## 🎯 Roadmap

### Recent Improvements
- ✅ Consolidated ConfigManager (removed duplication)
- ✅ Enhanced error handling with proper exception handling
- ✅ Added cross-platform file opening support
- ✅ Improved MetadataService with auto-loading
- ✅ Added comprehensive type hints

### Upcoming Features
- 🔄 Virtual scrolling for large directories
- 📊 Enhanced analytics and file statistics
- 🔍 Advanced search with filters and sorting
- 🎨 Customizable themes and color schemes

## 📚 Documentation

- **[AGENTS.md](AGENTS.md)**: Complete project architecture and conventions
- **[IMPROVEMENT_REPORT.md](IMPROVEMENT_REPORT.md)**: Detailed improvement analysis
- **[OPTIMIZATION_PRINCIPLES.md](OPTIMIZATION_PRINCIPLES.md)**: Development guidelines
- **[technical_report.md](technical_report.md)**: Technical architecture details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the coding conventions in `AGENTS.md`
4. Add tests for new functionality
5. Update documentation
6. Submit a pull request

## 📝 License

This project is open-source and follows standard MIT licensing.

## 📞 Support

For issues, questions, or feature requests:
- Check the **[IMPROVEMENT_REPORT.md](IMPROVEMENT_REPORT.md)** for known issues
- Review the **[AGENTS.md](AGENTS.md)** for architecture details
- Consult the **[technical_report.md](technical_report.md)** for implementation specifics