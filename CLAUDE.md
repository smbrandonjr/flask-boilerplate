# Flask Project Guidelines

## Core Principles
- **Ask first** - Clarify requirements before implementing complex features
- **Stay consistent** - Match existing patterns in the codebase
- **Document changes** - Update README.md and docs after every change
- **Maintain AFS** - Keep AI Framework Schema updated as project evolves

## Project Structure
```
project/
├── app/
│   ├── models/         # DatabaseConstant, FlaskModel base + feature models
│   ├── routes/         # Blueprint routes by feature
│   ├── static/         # CSS, JS (validators/), images
│   ├── templates/      # Feature folders + base.html
│   ├── __init__.py     # App factory, extensions
│   └── config.py       # Config classes
├── migrations/         # Alembic migrations
├── .env               # Never commit
├── requirements.txt
├── main.py            # Entry point
├── AFS-README.md      # AI Framework Schema documentation
├── afs-spec.md        # AFS specification reference
└── project.afs.json   # AI Framework Schema for this project
```

## Key Patterns

### Models
```python
from app.models import DatabaseConstant, db, FlaskModel

class ExampleModel(db.Model, FlaskModel):
    __tablename__ = 'examples'
    
    # Always include these
    id = DatabaseConstant.COLUMN(DatabaseConstant.PRIMARY_ID, primary_key=True)
    created_at = DatabaseConstant.COLUMN(DatabaseConstant.DATETIME, default=db.func.current_timestamp())
    updated_at = DatabaseConstant.COLUMN(DatabaseConstant.DATETIME, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    # Your fields here using DatabaseConstant types
```

### Routes
```python
@blueprint.route('/path', methods=['GET', 'POST'])
@login_required  # Decorators in this order
def route_function():
    if request.method == 'POST':
        try:
            # Create and populate model
            model = ExampleModel(**request.form)
            model.save()  # Handles all database operations internally
            flash('Success!', 'success')
            return redirect(url_for('blueprint.route'))
        except Exception as e:
            # FlaskModel.save() already handled rollback and logging
            flash('Error processing request', 'error')
    
    return render_template('feature/template.html')
```

### Error Handling
- **Model Layer**: FlaskModel methods (save/delete) handle all database operations, logging, and rollbacks
- **Route Layer**: Catch exceptions from model operations and provide user feedback
- **Flash Messages**: Always show user-friendly flash messages for both success and error states
- **Separation of Concerns**: Routes handle HTTP concerns, models handle database concerns

## Architecture Principles

### Layer Responsibilities
- **Routes**: Handle HTTP requests/responses, authentication, validation, user feedback
- **Models**: Handle database operations, business logic, data integrity, error handling
- **Templates**: Handle presentation logic only

### Database Operations
- **Never** call `db.session` methods directly in routes
- **Always** use model methods (`save()`, `delete()`, etc.)
- **Model methods** handle all session management, logging, and rollbacks internally
- **Routes** only catch exceptions for user feedback

### Error Flow
1. Model detects database error
2. Model logs error details
3. Model rolls back transaction
4. Model raises appropriate exception (via abort())
5. Route catches exception
6. Route shows user-friendly flash message

## Tech Stack
- **Backend**: Flask, Flask-Login, Flask-SQLAlchemy, python-decouple
- **Frontend**: Jinja2, Tailwind CSS, Alpine.js, HTMX
- **Database**: MySQL/SQLite

## Shortcuts

**QNEW** - "Follow CLAUDE.md patterns"
**QPLAN** - "Analyze similar features and plan implementation"
**QCODE** - "Implement with all safety patterns"
**QCHECK** - "Review for security, errors, consistency, UX"
**QMIGRATE** - "Create and apply database migration"
**QDOCS** - "Update README.md and relevant documentation"
**QAFS** - "Update project.afs.json schema with new patterns and features"

## After Every Change
1. Update README.md if functionality changed
2. Update relevant docs (API docs, setup instructions, etc.)
3. Add/update docstrings for new functions
4. Update requirements.txt if dependencies added
5. Update project.afs.json with new patterns, models, or routes

## Quick Reference

### Naming Conventions
- `snake_case` - functions, variables, routes
- `PascalCase` - classes (e.g., UserModel)
- Model names: singular + "Model" suffix

### Must-Have Security
- Environment variables for secrets
- Password hashing (werkzeug.security)
- CSRF protection (enabled globally)
- Input validation
- Login required on protected routes

### Git Ignore
```
.env
*.pyc
__pycache__/
.venv/
instance/
*.db
```

## Base Requirements
```
flask==3.1.0
flask-login==0.6.3
flask-newui==1.0.0
flask-migrate==4.1.0
flask-sqlalchemy==3.1.1
python-decouple==3.8
pymysql==1.1.1
```

## AI Framework Schema (AFS) Maintenance

### Purpose
This project leverages AI Framework Schema (AFS) to help AI models understand our Flask boilerplate patterns and provide better assistance. The schema evolves with the project to maintain AI effectiveness.

### Schema Files
- **AFS-README.md** - Documentation about AFS concept and benefits
- **afs-spec.md** - Complete AFS specification reference
- **project.afs.json** - AI Framework Schema specific to this Flask boilerplate

### When to Update Schema
Update `project.afs.json` whenever you:
- Add new models with unique patterns
- Create new route patterns or decorators
- Implement new security patterns
- Add new utility functions or helpers
- Change core architectural patterns
- Add new frontend components or patterns

### Schema Update Process
1. **Identify Changes**: Note what patterns/concepts changed
2. **Update Core Concepts**: Add new critical concepts AI must understand
3. **Update Common Patterns**: Add working code examples for new patterns
4. **Update Troubleshooting**: Add common issues and solutions
5. **Validate Schema**: Ensure JSON is valid and follows AFS spec
6. **Test with AI**: Verify AI can understand and use new patterns

### Schema Sections to Maintain
- `core_concepts`: Critical Flask boilerplate patterns
- `architecture_patterns`: How components work together
- `common_patterns`: Frequent use cases with code examples
- `troubleshooting`: Common issues specific to this boilerplate
- `ai_assistance_guidelines`: How AI should help with this project

### Example: Adding New Model Pattern
When you add a new model with unique features:
```json
{
  "core_concepts": {
    "audit_model": {
      "description": "Model with automatic audit trail tracking",
      "importance": "high",
      "ai_guidance": "Use for sensitive data that needs history tracking",
      "patterns": [{"example": "working code here"}]
    }
  }
}
```

### Validation
Use available AFS validation tools to ensure schema correctness:
```bash
# If validation tool exists
python validate_afs.py project.afs.json
```

## AFS-Enhanced Documentation Standards

### Code Documentation
When documenting code, include AI-relevant context:
```python
def create_user_model():
    """Creates a new user with encrypted fields.
    
    AFS Context: This is the standard pattern for user creation
    in this boilerplate. Always use DatabaseConstant types and
    include audit fields (created_at, updated_at).
    
    Returns:
        UserModel: Configured user instance
    """
```

### Architecture Decisions
Document architectural decisions with AI guidance:
```markdown
## Decision: Use DatabaseConstant wrapper

### Context
Raw SQLAlchemy types scattered throughout models

### Decision
Centralize all column types through DatabaseConstant class

### AI Guidance
Always use DatabaseConstant.COLUMN() instead of db.Column()
Always use DatabaseConstant types (STRING, INTEGER, etc.)
This ensures consistency and proper encryption handling
```

### Pattern Documentation
For new patterns, document in both CLAUDE.md and project.afs.json:

**CLAUDE.md** (Human-readable):
```markdown
### New Pattern: Soft Delete
```python
# Add to all models that need soft delete
is_deleted = DatabaseConstant.COLUMN(DatabaseConstant.BOOLEAN, default=False)
```

**project.afs.json** (AI-readable):
```json
{
  "common_patterns": {
    "soft_delete": {
      "problem": "Need to hide records without losing data",
      "solution": "Add is_deleted boolean field with default False",
      "code_example": "is_deleted = DatabaseConstant.COLUMN(DatabaseConstant.BOOLEAN, default=False)",
      "ai_guidance": "Always add soft delete to user-facing models"
    }
  }
}
```