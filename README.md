# Social-Media-Api
RESTful API for a social media platform

### Introduction
Welcome to the Social Media API Service!
This is a Django-based API for a social media platform.

### Social-Media-Api Service Features
* All the features are available only after registration on the platform and authentication.
* Authenticated users can follow other users, create and retrieve posts, manage likes and comments, and perform basic social media actions.
* Users can update and delete only their own profiles, posts and comments.
* Users can be searched by first name and last name separately or simultaneously. Posts can be searched by tags.
* User can schedule Post creation (you can select the time to create the Post before creating of it).
* Users can add Images to their profiles and to the posts.

### Installation Guide
* Clone this repository [here](https://github.com/nickkozlov90/social-media-api).
    ```bash
    git clone https://github.com/nickkozlov90/social-media-api.git
    cd social-media-api
    ```
* The main branch is the most stable branch at any given time, ensure you're working from it.

* If you want to run the app locally follow the next steps:
1. Create a virtual environment:

    ```bash
   python -m venv venv
    ```
2. Activate the virtual environment:

   On Windows: 
   ```bash
    venv\Scripts\activate
    ```
   On macOS and Linux:
   ```bash
   source venv/bin/activate
   ```
   
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
4. Copy this file ".env_sample" and rename it to ".env", then fill in the actual values for your local development environment.
5. Apply the migrations:

   ```bash
   python manage.py migrate
   ```

6. To run the development server, use the following command:

   ```bash
   python manage.py runserver
   ```

You can also run the application via the Docker. For this purpose make sure the Docker is installed on your computer and follow the next steps:
1. Fill the actual data for ".env" file (see above).
2. Build the app image and start the containers for the application and the database:
   ```bash
   docker-compose up --build
   ```

Access the application in your web browser at http://localhost:8000.

### API Endpoints

The list of available endpoints you can find at http://127.0.0.1:8000/api/doc/swagger/.

### Technologies Used
* [Django REST framework](https://www.django-rest-framework.org/) This is toolkit for building Web APIs, providing features such as serialization, authentication, viewsets, and class-based views to simplify the development of RESTful services in Django applications.
* [Celery](https://docs.celeryq.dev/en/stable/index.html#) It is a system to process task queue with focus on real-time processing, while also supporting task scheduling.
* [Redis](https://redis.io/) This is caching backend, session store, or for other purposes where you need a fast and scalable in-memory data store.
* [Docker](https://www.docker.com/) This is a platform that enables developers to automate the deployment and scaling of applications across various computing environments.
* [PostgreSQL](https://www.postgresql.org/) This is a powerful, open source object-relational database system.
* [Swagger](https://swagger.io/) This is open source and professional toolset to simplify documentation of API.

Authentication of users is implemented with means of JSON Web Tokens.
