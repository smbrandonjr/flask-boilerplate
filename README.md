# Flask Boilerplate 🚀

A production-ready Flask boilerplate with modern architecture, security best practices, and AI-enhanced development workflow. Built for rapid prototyping and scalable web applications.

## ✨ Features

### 🏗️ **Modern Architecture**
- **Clean separation of concerns** with proper layering
- **Custom FlaskModel** base class with built-in CRUD operations
- **DatabaseConstant** wrapper for consistent database types
- **Blueprint-based routing** for modular organization
- **Environment-based configuration** for multiple deployment targets

### 🔐 **Security First**
- **Flask-Login** integration for user authentication
- **CSRF protection** enabled globally
- **Encrypted database fields** using SQLAlchemy-Utils
- **Password hashing** with Werkzeug security
- **Environment variables** for sensitive configuration
- **Input validation** and sanitization

### 🎨 **Modern Frontend Stack**
- **Tailwind CSS** for utility-first styling
- **Alpine.js** for reactive JavaScript components
- **HTMX** for seamless AJAX interactions
- **Remix Icons** for comprehensive iconography
- **Notiflix** for beautiful notifications

### 🤖 **AI-Enhanced Development**
- **AI Framework Schema (AFS)** for better AI assistance
- **Comprehensive documentation** in CLAUDE.md
- **Standardized patterns** for consistent code generation
- **AI-readable project schema** for context-aware help

### 🛠️ **Developer Experience**
- **Flask-Migrate** for database migrations
- **Structured error handling** with proper logging
- **Development shortcuts** and quick commands
- **Comprehensive project guidelines**
- **Environment-specific configurations**

## 📋 Prerequisites

- Python 3.8+
- MySQL/MariaDB or SQLite
- Node.js (for Tailwind CSS compilation)

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd boilerplate
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
cp example.env .env
# Edit .env with your configuration
```

**Required Environment Variables:**
```env
SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here
DEBUG=True
DOMAIN=localhost:5000
PROD_TARGET=local

# Database Configuration
DB_ENGINE=mysql+pymysql
DB_USERNAME=your-username
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=your-database
```

### 3. Database Setup
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 4. Run the Application
```bash
python main.py
```

Visit `http://localhost:5000` to see your application!

## 📁 Project Structure

```
boilerplate/
├── app/
│   ├── models/          # DatabaseConstant, FlaskModel base + feature models
│   ├── routes/          # Blueprint routes by feature
│   ├── static/          # CSS, JS, images, icons
│   ├── templates/       # Jinja2 templates
│   ├── __init__.py      # App factory, extensions
│   └── config.py        # Configuration classes
├── migrations/          # Alembic database migrations
├── .env                 # Environment variables (create from example.env)
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
├── CLAUDE.md            # Development guidelines and patterns
├── AFS-README.md        # AI Framework Schema documentation
├── afs-spec.md          # AFS specification
└── project.afs.json     # AI-readable project schema
```

## 🔧 Configuration

The boilerplate supports multiple deployment targets:

### Development
```env
DEBUG=True
PROD_TARGET=local
```

### Production (Standard Server)
```env
DEBUG=False
PROD_TARGET=server
```

### Production (Google App Engine)
```env
DEBUG=False
PROD_TARGET=gae
```

### Production (Custom - XPS 15)
```env
DEBUG=False
PROD_TARGET=xps_15
```

## 🏗️ Architecture Principles

### Layer Responsibilities
- **Routes**: Handle HTTP requests/responses, authentication, validation, user feedback
- **Models**: Handle database operations, business logic, data integrity, error handling
- **Templates**: Handle presentation logic only

### Database Operations
- **Never** call `db.session` methods directly in routes
- **Always** use model methods (`save()`, `delete()`, etc.)
- **Model methods** handle all session management, logging, and rollbacks internally

### Example Usage

**Creating a Model:**
```python
from app.models import DatabaseConstant, db, FlaskModel

class PostModel(db.Model, FlaskModel):
    __tablename__ = 'posts'
    
    id = DatabaseConstant.COLUMN(DatabaseConstant.PRIMARY_ID, primary_key=True)
    title = DatabaseConstant.COLUMN(DatabaseConstant.STRING(200), nullable=False)
    content = DatabaseConstant.COLUMN(DatabaseConstant.TEXT, nullable=False)
    created_at = DatabaseConstant.COLUMN(DatabaseConstant.DATETIME, default=db.func.current_timestamp())
    updated_at = DatabaseConstant.COLUMN(DatabaseConstant.DATETIME, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
```

**Creating a Route:**
```python
@blueprint.route('/posts', methods=['GET', 'POST'])
@login_required
def posts():
    if request.method == 'POST':
        try:
            post = PostModel(**request.form)
            post.save()  # Handles all database operations internally
            flash('Post created successfully!', 'success')
            return redirect(url_for('posts.index'))
        except Exception as e:
            flash('Error creating post', 'error')
    
    return render_template('posts/index.html')
```

## 🔐 Security Features

### Encrypted Fields
```python
# Email encryption example
email_address = DatabaseConstant.COLUMN(
    CacheCompatibleEncryptedType(
        DatabaseConstant.STRING(255),
        DatabaseConstant.ENCRYPTION_KEY,
        DatabaseConstant.AES_ENGINE,
        DatabaseConstant.PKCS5
    ),
    nullable=False, unique=True
)
```

### User Authentication
Built-in user authentication with Flask-Login integration and secure password handling.

## 🎨 Frontend Development

### Tailwind CSS
```bash
# Compile Tailwind CSS (see compile-tailwind.md for details)
npx tailwindcss -i ./app/static/css/tailwind_input.css -o ./app/static/css/root.css --watch
```

### Alpine.js Components
```html
<div x-data="{ open: false }">
    <button @click="open = !open">Toggle</button>
    <div x-show="open">Content</div>
</div>
```

## 🤖 AI-Enhanced Development

This boilerplate includes AI Framework Schema (AFS) for better AI assistance:

- **CLAUDE.md**: Comprehensive development guidelines
- **project.afs.json**: AI-readable project schema
- **Standardized patterns**: Consistent code generation
- **Context-aware help**: AI understands your project structure

### Quick Commands
- **QNEW**: "Follow CLAUDE.md patterns"
- **QPLAN**: "Analyze similar features and plan implementation"
- **QCODE**: "Implement with all safety patterns"
- **QCHECK**: "Review for security, errors, consistency, UX"
- **QMIGRATE**: "Create and apply database migration"
- **QDOCS**: "Update README.md and relevant documentation"
- **QAFS**: "Update project.afs.json schema with new patterns"

## 📚 Documentation

- **[CLAUDE.md](CLAUDE.md)**: Complete development guidelines and patterns
- **[AFS-README.md](AFS-README.md)**: AI Framework Schema documentation
- **[afs-spec.md](afs-spec.md)**: AFS specification reference

## 🧪 Testing

```bash
# Run tests (when implemented)
python -m pytest

# Type checking (when configured)
mypy app/
```

## 🚀 Deployment

### Environment Setup
1. Set `DEBUG=False`
2. Configure production database
3. Set secure `SECRET_KEY` and `ENCRYPTION_KEY`
4. Configure `PROD_TARGET` appropriately

### Database Migration
```bash
flask db upgrade
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Follow patterns in CLAUDE.md
4. Update project.afs.json with new patterns
5. Commit changes: `git commit -am 'Add feature'`
6. Push to branch: `git push origin feature-name`
7. Submit a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Flask** community for the excellent web framework
- **Tailwind CSS** for utility-first CSS framework
- **Alpine.js** for lightweight reactive framework
- **SQLAlchemy** for powerful ORM capabilities

---

Built with ❤️ for rapid Flask development. Perfect for prototypes, MVPs, and production applications.