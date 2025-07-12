# 📧 SharedMailbox Editor

A professional web application for managing Exchange Online shared mailbox permissions with automated PowerShell script generation.

## 🚀 Features

- **CSV Import**: Import existing shared mailbox permissions from CSV files
- **Interactive Management**: Web-based interface for managing shared mailbox permissions
- **PowerShell Generation**: Automatically generates Exchange Online PowerShell scripts
- **Permission Operations**: Add, remove, and modify mailbox permissions
- **Authentication Support**: Optional credential inclusion in generated scripts
- **Modern UI**: Responsive design with professional styling
- **Docker Support**: Easy deployment with Docker containers

## 🏗️ Tech Stack

- **Backend**: Python Flask
- **Frontend**: Vanilla JavaScript, SCSS/CSS
- **Containerization**: Docker & Docker Compose
- **Package Management**: npm (for frontend tools), pip (for Python)

## 📋 Prerequisites

### Option 1: Docker (Recommended)
- Docker Desktop
- Docker Compose

### Option 2: Local Development
- Python 3.9+
- Node.js 18+
- npm

## 🚀 Quick Start

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/Poutchouli/SharedMailbox_editor.git
   cd SharedMailbox_editor
   ```

2. **Start with Docker**
   
   **Windows (PowerShell):**
   ```powershell
   .\start_app.ps1
   ```
   
   **Linux/macOS:**
   ```bash
   chmod +x start_app.sh
   ./start_app.sh
   ```

3. **Access the application**
   
   Open your browser and navigate to: `http://localhost:5000`

### Local Development Setup

1. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Node.js dependencies** (for SCSS compilation)
   ```bash
   npm install
   ```

3. **Build CSS** (optional, for development)
   ```bash
   npm run build:css
   ```

4. **Start the application**
   ```bash
   python app.py
   ```

## 📖 Usage

### 1. Import CSV Data

Upload a CSV file with the following format:
```csv
Identity;User;AccessRights
shared-mailbox1;user@domain.com;FullAccess,SendAs
shared-mailbox2;admin@domain.com;FullAccess
```

### 2. Manage Permissions

- Select shared mailboxes from the imported data
- Add or remove user permissions for shared mailboxes
- Specify access rights (FullAccess, SendAs, etc.)

### 3. Generate PowerShell Script

- Review pending operations
- Optionally include credentials for automation
- Generate Exchange Online PowerShell script
- Download or copy the script for execution

### 4. Execute in Exchange Online

Run the generated PowerShell script in your Exchange Online environment:
```powershell
# Connect to Exchange Online (if credentials not included)
Connect-ExchangeOnline

# Execute the generated script
.\GeneratedPermissionsScript_[timestamp].ps1
```

## 📁 Project Structure

```
SharedMailbox_editor/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── package.json                    # Node.js dependencies & scripts
├── Dockerfile                      # Docker container definition
├── docker-compose.yml             # Docker Compose configuration
├── start_app.ps1                  # Windows startup script
├── start_app.sh                   # Linux/macOS startup script
├── static/                        # Static assets
│   ├── css/                       # Compiled CSS (generated)
│   └── scss/                      # SCSS source files
├── templates/                     # HTML templates
│   └── index.html                 # Main application template
└── sample_southpark_permissions.csv # Demo data file
```

## 🛠️ Development

### Available Scripts

```bash
# Start application
npm start

# Development with auto-reload & CSS watching
npm run dev

# Build CSS from SCSS
npm run build:css

# Watch SCSS files for changes
npm run watch:css

# Frontend development server
npm run dev:frontend
```

### Docker Commands

```bash
# Build and start
docker-compose up --build

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Restart
docker-compose restart
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file for custom configuration:

```env
FLASK_ENV=development
FLASK_DEBUG=true
SECRET_KEY=your-secret-key-here
PORT=5000
```

### Authentication

By default, the application doesn't require authentication credentials to be included in generated scripts. You can enable this feature in the web interface when generating scripts.

## 📝 CSV Format

The application expects CSV files with semicolon (`;`) separators and the following columns:

- **Identity**: Shared mailbox name or UPN
- **User**: User account with permissions
- **AccessRights**: Comma-separated list of permissions

### Supported Access Rights

- `FullAccess`
- `SendAs` 
- `ReadPermission`
- `ChangePermission`
- `ChangeOwner`

## 🔒 Security Notes

- **Credentials**: Only include credentials in scripts if absolutely necessary
- **Generated Scripts**: Always review generated PowerShell scripts before execution
- **NT AUTHORITY\SELF**: This system permission cannot be removed
- **SSL/HTTPS**: Consider enabling HTTPS for production deployments

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the ISC License.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/Poutchouli/SharedMailbox_editor/issues)
- **Documentation**: This README and inline code comments

## 🎯 Roadmap

- [ ] Multi-language support
- [ ] Advanced permission templates
- [ ] Bulk operations optimization
- [ ] Exchange on-premises support
- [ ] REST API for automation
- [ ] Permission auditing features

---

**⚠️ Important**: This tool generates PowerShell scripts for Exchange Online. Always test in a non-production environment first and review all generated scripts before execution.
