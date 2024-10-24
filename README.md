# iShare API
```iShare``` is a lightweight Flask-based API for sharing pictures and comments. It provides user authentication, picture uploading, and commenting functionality. This project is built with ```Flask```, ```SQLAlchemy```, ```Flask-Migrage```(Alembic) for migrations, and uses ```JWT``` for authentication.

## Table of Contents
- [Project Architecture](#project-architecture)
- [Setup Instructions](#setup-instructions)
- [Usage Guidelines](#usage-guidelines)
- [API Documentation](#api-documentation)

## Project Architecture
```md
.
├── README.md                  # Project documentation
├── api                        # Core API application
│   ├── __init__.py            # Initialize the Flask app and extensions
│   ├── app.py                 # Main application entry point
│   ├── auth.py                # Authentication logic (JWT-based)
│   ├── config.py              # Configuration settings (environment variables)
│   ├── models                 # SQLAlchemy models for the database
│   │   ├── __init__.py        
│   │   ├── comment.py         # Comment model
│   │   ├── picture.py         # Picture model
│   │   ├── tokenblacklist.py  # Token blacklist for JWT revocation
│   │   └── user.py            # User model
│   └── routes                 # API routes/endpoints
│       ├── __init__.py        
│       ├── admin_routes.py    # Routes for admin actions
│       ├── base_routes.py     # Base/utility routes
│       ├── comment_routes.py  # Comment-related routes
│       ├── picture_routes.py  # Picture-related routes
│       └── user_routes.py     # User-related routes
├── instance                   # Instance folder (contains local SQLite database)
│   └── ishare.db              # SQLite database file
├── migrations                 # Database migrations
│   ├── README                 # Migration tool instructions
│   ├── alembic.ini            # Alembic configuration
│   ├── env.py                 # Environment configurations for migrations
│   ├── script.py.mako         # Migration script templates
│   └── versions               # Individual migration scripts
│       └── 4a32d1a2bc80_add_created_at_and_updated_at_columns_.py
├── services                   # Helper services (for database queries, etc.)
│   └── __init__.py            
└── uploads                    # Folder to store uploaded pictures
```

## Setup Instructions

Follow these steps to set up and run the iShare API on your local machine:

### Prerequisites
- Python 3.8+
- `pip` (Python package manager)
- SQLite (already included with Python)
- Virtual environment tools (optional but recommended)

### Step 1: Clone the Repository
```bash
git clone https://github.com/MrGiddy/ishare.git
cd ishare
```

### Step 2: Set Up a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate   # On Windows use `venv\Scripts\activate`
```

### Step 3: Install Dependencies
```bash
pip install -r api/requirements.txt
```

### Step 4: Set Up the Database
You can initialize the ```SQLite``` database by running the following migration commands:
```bash
flask db upgrade
```
This will apply the necessary migrations to create the database schema.

### Step 5: Run the Application
Start the development server:
```bash
flask run
```

The API will now be available at ```http://127.0.0.1:5000```

The app's configurations can be adjusted using environment variables or the config.py file in the api folder. Common variables include:

* ```SQLALCHEMY_DATABASE_URI```: Specifies the database URL for SQLAlchemy. By default, it points to an SQLite database (ishare.db).
* ```SQLALCHEMY_TRACK_MODIFICATIONS```: Disables the SQLAlchemy event system to save resources.
* ```JWT_SECRET_KEY```: The secret key used to sign and verify JSON Web Tokens (JWT). You can set it via the environment variable JWT_SECRET_KEY, or it defaults to 'jwt_secret_key'.
* ```JWT_ACCESS_TOKEN_EXPIRES```: Sets the expiration time for JWT access tokens (default is 1 hour)

You can modify these settings as needed to suit your environment.


# Usage Guidelines
Once the API is running, you can interact with it via HTTP requests. Below are some key routes and examples:

## Authentication
To interact with the protected routes, you must first log in to obtain a JWT token.

### 1. Sign Up
* Endpoint: ```api/register```
* Method: ```POST```
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "password123"
}
```

### 2. Login
* Endpoint: ```api/login```
* Method: ```POST```
```json
{
  "email": "newuser@example.com",
  "password": "password123"
}
```

### 3. Logout
* Endpoint: ```api/logout```
* Method: ```POST```
Token: Must include a valid token in the Authorization header.


# API Documentation
Comprehensive Documentation (using Swagger UI) of iShare API to be found via:
* Endpoint: ```api/swagger```
* Method: ```GET```

after setting up and running the api
