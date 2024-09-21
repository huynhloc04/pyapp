# Standard FastAPI Application

## Local setup

The project uses [Poetry](https://python-poetry.org/) for dependency management
and packaging. First, make sure that you have poetry installed on your system and
ensure that you have Python 3.10 or higher installed. Once setup, simply
install all dependencies into a virtual environment using:

```bash
poetry install
```

Run Celery as a message broker

```bash
poetry run celery -A app.core.tasks worker --loglevel=info --logfile=app/logging/celery.log
```

To run the API locally, run the following command from the root directory.

```bash
poetry run uvicorn app.api.main:app --reload
```

Alternatively, open a new shell in the virtual environment through the following
command and run the API from there.

```bash
poetry shell && uvicorn api.main:app --reload
```

To verify that everything is working locally as expected, you can query the API
from the command line

```bash
curl http://localhost:8000
```

Alternatively, open the above URL in a browser. The entire API is automatically
documented through FastAPI at the routes `/docs` (SwaggerUI) and `/redoc` (Redoc).

**_Note_**: Please create database (DATABASE_NAME: pyapp) firstly and setup .env file (follow .env.example for more clearly)

## Deployment

I use [`Docker`] for deployment. The `Dockerfile` specifies how to build
and run the FastAPI docker image using poetry as a package management tool and `docker compose` for deploy all of the services.

To deploy the app, run the following command from the root directory.

```bash
docker compose up -d --build
```

The FastAPI app is exposed on port 8080 of the public port. If run locally,
you can again access the API at the local IP `127.0.0.1`. If run on a remote
machine (like a VM), then the API is available at the public IP of the service.

Currently, I am hosting the API on a remote server, on public port `13.229.185.26`. Thus, you can query the API through:

```bash
curl http://13.229.185.26:8080
```

# Developer Guide

## Techstack

- Poetry: Package management and dependency resolution.
- Python 3.10: Primary Programming language.
- FastAPI: Web framework for building APIs.
- SQLModel (SQLAlchemy + Pydantic): ORM for interacting with the database and validate data.
- Alembic: Database migrations.
- PostgreSQL: Database for storing data.
- Celery: Distributed task queue that allows users to execute task asynchronously.
- Redis: Message broker for Celery.
- Flower: web-based monitoring tool for Celery.
- Docker: Creating, deploying, and running applications
- ShipEngine: Rendering PDF shipping label (fulfillment)

Note: I use Celery for sending email, Flower to monitor Celery's activities

## Architecture Overview

The project is structured as follows:

```bash
.
├── app/
│   ├── api
│   │   ├── main.py
│   │   └── routes
│   │       └── v1
│   │           ├── group.py
│   │           ├── order.py
│   │           ├── product.py
│   │           ├── store.py
│   │           └── user.py
│   ├── db
│   │   ├── session.py
│   │   └── utils.py
│   ├── logging
│   ├── models
│   │   ├── base.py
│   │   ├── order.py
│   │   ├── product.py
│   │   ├── store.py
│   │   └── user.py
│   └── repository
│
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── migrations/
├── pyproject.toml
├── README.md

```

## Editor Setup - Visual Studio Code

- Black Formatter: Maintains consistent code formatting regarding line length, indentation, and spacing.
- Ruff: Lints code for errors and warnings.

## Database

The database contains the following tables:

- users: (id, name, phone, email, password, address, is_admin, group_id) - Save user information
- groups: (id, name, description) - Save group information that a user belongs to.
- products: (id, name, base_price, description) - Basic information of a product.
- stores: (id, name, address, is_store) - Store information.
- orders: (id, user_id, total_price, shipping_method, shipping_location, fulfill_status, fulfill_at, from_admin) - Information of an order of an customer.
- order_product: (order_id, product_id, quantity) - Product information of a specific order.

=> Check the Entity Reletionship Diagram of this app [here](figures/ERD.jpg).

## Error Handling

Response codes that can be expected from the API:

- 200: Success
- 201: Created
- 401: Unauthenticated - Access token missing or invalid.
- 403: Forbidden - Client is not authorized to access the requested resource.
- 404: Not found - Resource not found.
- 422: Validation Error - Request body does not match schema.

## User flow

1. Account

- Customers sign up an account `POST /v1/users/signup` (Please choose group for each customer `GET /v1/groups`).
- They can then log in through a call to `POST /v1/users/login` with username & password as form data

2. Create products

- BSA (Admin) creates products `POST /v1/products` (name, base_price and description)
- BSA can then manage (GET, UPDATE, DELETE) a product

3. Order products

- Both BSA or customer can place an order: ` POST /v1/orders`
- We have some following information when place a new order:
  - Select shipping methods: Freeship or Pickup.
  - Select shipping location: Select from a list of BSA's stores (Pickup) or shipped from the main warehouse (Freeship).
  - Enter customer email to be shipped (BSA).
  - Enter product type and quantity.
- The order status will be `unfulfilled` as default.
- The discounts will be applied to prducts based on type of customer (5% for Starter, 7% for Professional and 10% for VIP).

4. Fulfillment (BSA)

- BSA fulfill orders `POST /v1/orders/{order_id}/fulfill` by fill out all of the following information
  - ship_from (name, phone, address, city, ...)
  - ship_to (name, phone, address, city, ...)
  - packages (all package's information: weight, height, ...)
- To be fulfilled, an order must go through some steps:
  - Updating order status: Change from "Unfulfilled" to "fulfilled".
  - Generating shipping labels.
  - Notifying customers via email or SMS (email in this case).
  - Generate the `tracking number` to track the order (Freeship method)

=> Check the workflow [here](figures/workfow.jpg)

## API documents

Check [this link](https://documenter.getpostman.com/view/20233800/2sAXqpAPpY) for the API document with Postman or [Redoc](http://13.229.185.26:8080/redoc) of FastAPI
