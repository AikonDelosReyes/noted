# Noted - Django REST API Note-Taking Application

A modern, feature-rich note-taking application built with Django REST Framework, featuring JWT authentication, rate limiting, and a beautiful responsive UI.

## Features

### Authentication & User Management
- JWT-based authentication system
- User registration with profile photo upload
- Secure password handling
- Profile photo validation and automatic square cropping
- Support for JPEG, PNG, and WebP formats (max 2MB)

### Note Management
- Create, read, update, and delete notebooks
- Organize notes within notebooks
- Tag system for better note organization
- Rich text editing capabilities
- Search functionality

### API Rate Limiting
- Custom rate limiting implementation
- Different limits for anonymous and authenticated users
- DRF's built-in throttling mechanism
- Protection against abuse and DoS attacks

### Modern UI Features
- Responsive design for all screen sizes
- Sidebar navigation system
- Card-based layout
- Interactive elements
- Modern color scheme
- Form validation with instant feedback
- Image upload preview
- Bootstrap and Font Awesome integration

## Technical Stack

- **Backend**: Django REST Framework
- **Database**: SQLite (default), compatible with PostgreSQL
- **Authentication**: JWT (JSON Web Tokens)
- **Frontend**: 
  - HTML5/CSS3
  - Bootstrap 5
  - Font Awesome icons
  - JavaScript
- **Image Processing**: Pillow

## Installation

1. Clone the repository:
```bash
git clone https://github.com/AikonDelosReyes/noted.git
cd noted
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Apply migrations:
```bash
python manage.py migrate
```

5. Create a superuser (admin):
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## API Endpoints

### Authentication
- `POST /api/token/` - Obtain JWT token
- `POST /api/token/refresh/` - Refresh JWT token
- `POST /api/register/` - Register new user

### Notes
- `GET /api/notebooks/` - List all notebooks
- `POST /api/notebooks/` - Create new notebook
- `GET /api/notebooks/{id}/` - Retrieve notebook
- `PUT /api/notebooks/{id}/` - Update notebook
- `DELETE /api/notebooks/{id}/` - Delete notebook
- `GET /api/notes/` - List all notes
- `POST /api/notes/` - Create new note
- `GET /api/notes/{id}/` - Retrieve note
- `PUT /api/notes/{id}/` - Update note
- `DELETE /api/notes/{id}/` - Delete note

### Tags
- `GET /api/tags/` - List all tags
- `POST /api/tags/` - Create new tag
- `GET /api/tags/{id}/` - Retrieve tag
- `PUT /api/tags/{id}/` - Update tag
- `DELETE /api/tags/{id}/` - Delete tag

## Rate Limiting

- Anonymous users: 100 requests per hour
- Authenticated users: 1000 requests per hour
- Throttling applies to all API endpoints

## Security Features

- JWT token authentication
- Password hashing
- CSRF protection
- XSS prevention
- Secure file upload handling
- Rate limiting
- Input validation

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Acknowledgments

- Django REST Framework documentation
- Bootstrap documentation
- Font Awesome icons 
