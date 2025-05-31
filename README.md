# Noted - A Note Management API

A Django REST Framework API for managing notes, notebooks, and tags with JWT authentication, rate limiting, and profile photo management.

## Features

- User authentication using JWT tokens
- Rate limiting for API endpoints
- Profile photo upload with automatic square cropping
- CRUD operations for Notebooks, Notes, and Tags
- Proper error handling and authentication checks
- Relationship management between Notes, Tags, and Notebooks

## Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run migrations: `python manage.py migrate`
6. Start the development server: `python manage.py runserver`

## API Documentation

### Rate Limiting

The API implements rate limiting to prevent abuse. Different limits apply to authenticated and anonymous users:

- Anonymous users: 5 requests per minute
- Authenticated users: 20 requests per minute
- Registration endpoint: 3 requests per minute
- Protected view: 10 requests per minute

When rate limit is exceeded, the API returns:
- Status code: 429 Too Many Requests
- Response body:
```json
{
    "error": "Too many requests",
    "detail": "Please wait before making another request. Maximum X requests per Y seconds.",
    "retry_after": seconds_to_wait
}
```

### Authentication and Profile Management

All endpoints except registration and token generation require JWT authentication.
Include the token in the Authorization header: `Authorization: Bearer <your_token>`

#### Register a new user with photo
- **POST** `/api/users/register/`
- **Rate Limit**: 3 requests per minute
- **Content-Type**: `multipart/form-data`
- **Body**:
  - `username`: string
  - `password`: string
  - `photo`: file (optional, max 2MB, JPEG/PNG/WebP)
- **Response**: 201 Created
```json
{
    "message": "User registered successfully!",
    "user": {
        "id": 1,
        "username": "your_username",
        "profile": {
            "photo": "/media/profile_photos/your_photo.jpg"
        }
    }
}
```

#### Get user profile
- **GET** `/api/users/profile/`
- **Rate Limit**: 20 requests per minute
- **Headers Required**: Authorization
- **Response**: 200 OK
```json
{
    "id": 1,
    "username": "your_username",
    "profile": {
        "photo": "/media/profile_photos/your_photo.jpg"
    }
}
```

#### Update profile photo
- **PATCH** `/api/users/profile/`
- **Rate Limit**: 20 requests per minute
- **Headers Required**: 
  - Authorization
  - Content-Type: multipart/form-data
- **Body**:
  - `photo`: file (max 2MB, JPEG/PNG/WebP)
- **Response**: 200 OK
```json
{
    "id": 1,
    "username": "your_username",
    "profile": {
        "photo": "/media/profile_photos/new_photo.jpg"
    }
}
```

#### Get JWT Token
- **POST** `/api/token/`
- **Rate Limit**: 5 requests per minute (anonymous)
- **Body**:
```json
{
    "username": "your_username",
    "password": "your_password"
}
```
- **Response**: 200 OK
```json
{
    "access": "your.jwt.token",
    "refresh": "your.refresh.token"
}
```

### Notebooks

#### List all notebooks
- **GET** `/api/users/notebooks/`
- **Rate Limit**: 20 requests per minute
- **Headers Required**: Authorization
- **Response**: 200 OK
```json
[
    {
        "id": 1,
        "title": "Work Notes",
        "description": "All work-related notes",
        "created_at": "2024-03-20T10:00:00Z",
        "updated_at": "2024-03-20T10:00:00Z"
    }
]
```

#### Create a notebook
- **POST** `/api/users/notebooks/`
- **Body**:
```json
{
    "title": "Work Notes",
    "description": "All work-related notes"
}
```
- **Response**: 201 Created

#### Get a single notebook
- **GET** `/api/users/notebooks/{id}/`
- **Response**: 200 OK

#### Update a notebook
- **PUT/PATCH** `/api/users/notebooks/{id}/`
- **Body**:
```json
{
    "title": "Updated Title",
    "description": "Updated description"
}
```
- **Response**: 200 OK

#### Delete a notebook
- **DELETE** `/api/users/notebooks/{id}/`
- **Response**: 204 No Content

### Notes

#### List all notes
- **GET** `/api/users/notes/`
- **Response**: 200 OK
```json
[
    {
        "id": 1,
        "title": "Meeting Notes",
        "content": "Important points from the meeting",
        "notebook": 1,
        "tags": [
            {
                "id": 1,
                "name": "work"
            }
        ],
        "created_at": "2024-03-20T10:00:00Z",
        "updated_at": "2024-03-20T10:00:00Z"
    }
]
```

#### Create a note
- **POST** `/api/users/notes/`
- **Body**:
```json
{
    "title": "Meeting Notes",
    "content": "Important points from the meeting",
    "notebook": 1,
    "tag_ids": [1, 2]
}
```
- **Response**: 201 Created

#### Get a single note
- **GET** `/api/users/notes/{id}/`
- **Response**: 200 OK

#### Update a note
- **PUT/PATCH** `/api/users/notes/{id}/`
- **Body**:
```json
{
    "title": "Updated Title",
    "content": "Updated content",
    "tag_ids": [1, 3]
}
```
- **Response**: 200 OK

#### Delete a note
- **DELETE** `/api/users/notes/{id}/`
- **Response**: 204 No Content

### Tags

#### List all tags
- **GET** `/api/users/tags/`
- **Response**: 200 OK
```json
[
    {
        "id": 1,
        "name": "work",
        "created_at": "2024-03-20T10:00:00Z"
    }
]
```

#### Create a tag
- **POST** `/api/users/tags/`
- **Body**:
```json
{
    "name": "work"
}
```
- **Response**: 201 Created

#### Get a single tag
- **GET** `/api/users/tags/{id}/`
- **Response**: 200 OK

#### Update a tag
- **PUT/PATCH** `/api/users/tags/{id}/`
- **Body**:
```json
{
    "name": "updated-tag"
}
```
- **Response**: 200 OK

#### Delete a tag
- **DELETE** `/api/users/tags/{id}/`
- **Response**: 204 No Content

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- 400 Bad Request: Invalid input or file validation error
- 401 Unauthorized: Missing or invalid authentication
- 403 Forbidden: Insufficient permissions
- 404 Not Found: Resource not found
- 429 Too Many Requests: Rate limit exceeded
- 500 Internal Server Error: Server-side error

Example rate limit error response:
```json
{
    "error": "Too many requests",
    "detail": "Please wait before making another request. Maximum 20 requests per 60 seconds.",
    "retry_after": 30
}
```

Example file validation error response:
```json
{
    "photo": [
        "File size must be less than 2MB.",
        "Unsupported file extension. Please use JPEG, PNG, or WebP."
    ]
}
```

## Security

- All endpoints (except registration and token generation) require JWT authentication
- Rate limiting implemented to prevent API abuse
- File upload restrictions:
  - Maximum file size: 2MB
  - Allowed formats: JPEG, PNG, WebP
  - Automatic square cropping
- Users can only access their own notebooks, notes, and tags
- Passwords are securely hashed
- JWT tokens expire after a set time
- CSRF protection enabled
- Input validation and sanitization implemented 