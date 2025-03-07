# PDF Quiz Maker

PDF Quiz Maker is a fully functional, full-stack web application designed for creating and managing PDF-based quizzes. This open-source project leverages modern web technologies and is built to be scalable, maintainable, and easy to deploy.

## Features

- **Full-Stack Functionality:** A complete web application covering both front-end and back-end operations.
- **Built with Django:** The application is developed using the Django web framework.
- **Docker Support:** Easily containerize and deploy the application using Docker.
- **Redis Integration:** Utilizes Redis for caching and as a message broker.
- **Celery Task Queue:** Asynchronous task processing powered by Celery.
- **SMTP Integration:** Built-in support for SMTP for sending emails.

## Prerequisites

- [Docker](https://www.docker.com/get-started) installed on your machine.
- [Docker Compose](https://docs.docker.com/compose/install/) installed.

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/pdf-quiz-maker.git
cd pdf-quiz-maker
```

### 2. Build the Docker Containers

```bash
docker-compose build
```

### 3. Collect Static Files

After building the containers, run the following command to collect static assets:

```bash
docker-compose run django python manage.py collectstatic --noinput
```

### 4. Start the Application

```bash
docker-compose up -d
```

### 5. Access the Application

Open your browser and navigate to [http://localhost:8000](http://localhost:8000) (or the appropriate port as configured) to start using PDF Quiz Maker.

## Usage Instructions

Users need to highlight the correct answers in the PDFs before uploading them. The application extracts questions and answers while recognizing the highlighted option as the correct answer.

For example:

```
1. What is the capital of France?
   A) Madrid
   B) Berlin
   C) Paris  ← (Highlighted)
   D) Rome
```

Ensure that the correct answers are clearly highlighted in the document to achieve accurate quiz generation.

## Configuration

### Environment Variables:

Customize your setup by modifying the environment variables in the `.env` file. Key configurations include:

- Configuration settings
- SMTP server details

### Docker Compose:

The `docker-compose.yml` file includes services for:

- **Django** (web application)
- **Redis** (caching and message broker)
- **Celery** (asynchronous task processing)

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and ensure that tests pass.
4. Submit a pull request with a detailed description of your changes.

## License

This project is open-source and available under the **MIT License**.

## Contact

For any questions, issues, or feature requests, please open an issue on the GitHub repository or contact the maintainer at `hikmetezimzade936@gmail.com`.
