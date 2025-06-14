# Distraction Free Learning Platform-Havelse 📚 

A comprehensive web-based platform designed for focused programming education through YouTube tutorials, articles, and interactive coding challenges. Features AI-powered doubt resolution and an integrated coding environment for seamless hands-on learning.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [API Integration](#api-integration)
- [Contributing](#contributing)
- [Built with](#built-with)

## Features

- **Article Library**: Curated programming articles and tutorials
- **YouTube Tutorial Integration**: Embedded videos with custom focus-maintaining features
- **Multi-language Code Execution**: Support for various programming languages
- **AI-Powered Doubt Resolution**: Get instant help with Gemini Assistant integration
- **Responsive Design**: Works seamlessly across desktop and mobile devices

## Tech Stack

- **Backend**: Django (Python)
- **Database**: MySQL
- **Frontend**: HTML5, CSS3,Bootstrap,JavaScript
- **AI Integration**: Google Gemini Assistant
- **Video Platform**: YouTube API v3
- **Code Execution**: In-browser code runner using Judge0 API

## Installation

### Prerequisites

Ensure you have the following installed:

```bash
Python >= 3.8
MySQL >= 8.0
Node.js >= 14.0 (for frontend dependencies)
```

### Clone Repository

```bash
git clone https://github.com/siddaramaiah-j-v/HAVELSE.git
cd distraction-free-learning-platform
```

### Backend Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Set up MySQL database:
```bash
mysql -u root -p
CREATE DATABASE learning_platform;
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run database migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```


## Usage

### Running the Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` to access the platform.

## API Integration

### YouTube API

The platform uses YouTube Data API v3 for:
- Video embedding
- Playlist management
- Custom player controls
- Video metadata retrieval

### Gemini AI Integration

AI features powered by Google Gemini:
- Natural language doubt resolution
- Code explanation and debugging
- Personalized learning recommendations


## Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide for Python code
- Write comprehensive tests for new features
- Update documentation for any API changes
- Ensure responsive design for frontend changes

## Built With

- **[Django](https://djangoproject.com/)** - Web framework
- **[MySQL](https://mysql.com/)** - Database
- **[YouTube Data API v3](https://developers.google.com/youtube/v3)** - Video integration
- **[Google Gemini](https://ai.google.dev/)** - AI assistant
- **[Bootstrap](https://getbootstrap.com/)** - Frontend framework
- **[Monaco Editor](https://microsoft.github.io/monaco-editor/)** - Code editor


If you encounter any issues or have questions:

- Create an [issue](https://github.com/siddaramaiah-j-v/HAVELSE/issues)
- Email: support@HAVELSE.com
- Documentation: [Wiki](https://github.com/siddaramaiah-j-v/HAVELSE/wiki)

---

🚀 **Start your distraction-free learning journey today!**
