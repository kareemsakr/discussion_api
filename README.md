# Discussion API

A Django REST Framework API for managing discussions and comments with threaded replies.

## Overview

This API provides endpoints for creating and managing discussions with a threaded comment system. It supports hierarchical comments (replies to comments) and provides a flat tree structure for easy display and manipulation.

## Key features:

- Create and retrieve discussions
- Add comments to discussions
- Reply to existing comments
- Get comments with hierarchical information (path and level)
- Filter comments by nesting level

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

#### Clone the repository:

```
git clone https://github.com/kareemsakr/discussion_api.git
cd discussion_api
```

#### Create and activate a virtual environment:

```
python -m venv venv
source venv/bin/activate # On Windows, use: venv\Scripts\activate
```

#### Install dependencies:

```
pip install -r requirements.txt
```

#### Apply migrations:

```
python manage.py migrate
```

#### Run the development server:

```
python manage.py runserver
```

The API will be available at http://127.0.0.1:8000/api/

## API Documentation

### Interactive API documentation is available at:

Swagger UI: http://127.0.0.1:8000/swagger/
ReDoc: http://127.0.0.1:8000/redoc/

## Endpoints

### Discussions

- GET /api/discussions/ - List all discussions
- POST /api/discussions/ - Create a new discussion
- GET /api/discussions/{id}/ - Retrieve a specific discussion

### Comments

- GET /api/discussions/{id}/comments/ - List all comments for a discussion`

#### Query Parameters:

- level (optional): Filter comments by nesting level (0 for top-level only, 1 for top-level and their direct replies, None for all levels)

- POST /api/discussions/{id}/comments/ - Add a comment to a discussion
- GET /api/discussions/{id}/comments/{comment_id}/replies/ - Get all replies to a specific comment (for lazy loading on the UI)

## Data Models

### Discussion

```
{
"id": 1,
"user": "username",
"title": "Discussion title",
"created_at": "2023-01-01T12:00:00Z",
}
```

### Comment

Note: 'parent' is can point to another comment (which represents a reply), if null means it's a top level comment on the discussion

```
{
"id": 1,
"discussion": 1,
"user": "username",
"parent": null,
"content": "Comment content",
"created_at": "2023-01-01T12:00:00Z",
"level": 0,
"path": "1"
}
```

## Testing

Run the test suite with:

```
python manage.py test
```

For more detailed test output, add the verbosity flag:

```
python manage.py test --verbosity=2
```

### Postman Collection

For rapid API testing, export the postman collection and environment from ./postman and run the saved calls in order. ALternatively, use the swagger page for the same result.

## Design Decisions

### Comment Tree Structure

The API uses an adjacency list with materialized path approach for the comment tree structure. This provides:

- Efficient querying of comment hierarchies
- Easy sorting of comments in threaded order
- Simple level information for indentation in UIs

### Database

The project uses SQLite for simplicity and ease of setup. This requires no additional configuration from reviewers.
