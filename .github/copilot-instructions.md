# Copilot Instructions

## Architecture

This is a Python-based web application with a Vue.js front end. The back end is built with Flask and uses a PostgreSQL database. The front end is a single-page application that communicates with the back end via a REST API.

### Back End

The back-end code is in the `desktop-app/src` directory. The main entry point is `main.py`. The database models are in `desktop-app/src/models`, and the API endpoints are in `desktop-app/src/api`.

### Front End

The front-end code is in the `desktop-app/static` and `desktop-app/templates` directories. The main HTML file is `index.html`, and the JavaScript is in `unified-realtime.js`. The CSS is in `sentinel-dash.css`.

## Developer Workflows

### Back End

To run the back end for development, use the following command:

```bash
python desktop-app/src/main.py
```

### Front End

The front end is served by the Flask application, so no separate build step is required.

## Project Conventions

*   All new features should be developed on a feature branch and submitted as a pull request.
*   All code should be formatted with Black.
*   All new API endpoints should be documented with OpenAPI specifications.
