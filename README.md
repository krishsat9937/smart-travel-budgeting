# **Smart Travel Budgeting Application**

This application is a full-stack project built with **Next.js** and **Django**. It demonstrates a secure authentication system with features such as user registration, login, password reset, and session handling, integrated with a modern frontend interface.

Additionally, this application serves as a foundation for a smart travel budgeting platform, showcasing the ability to fetch, display, and manage real-time travel data.

---

## **Features**
- User authentication with **Djoser** and **JWT**.
- Secure session handling for logged-in users.
- Real-time travel suggestions using **Amadeus API** and **Google Maps API**.
- Frontend built with **Next.js** and styled using **Tailwind CSS**.
- Responsive and modern UI with **Material-UI** components.
- API integration with **Django REST Framework (DRF)**.

---

## **Tech Stack**
### Backend:
- **Django**: For robust API development.
- **Django REST Framework**: For building RESTful APIs.
- **Djoser**: To handle user authentication seamlessly.
- **PostgreSQL**: For secure and scalable data storage.

### Frontend:
- **Next.js**: For server-side rendering and dynamic content.
- **Tailwind CSS**: For rapid and responsive UI design.
- **React-Query**: For efficient API data fetching.
- **Material-UI**: For pre-designed, customizable components.

---

## **Setup**

### **With Docker**
For a quick setup, use Docker to spin up the application:
```bash
docker compose up -d --build
```
- The Django backend will run on **http://localhost:8000**.
- The Next.js frontend will run on **http://localhost:3000**.

---

### **Manual Setup**

1. Clone the repository and navigate into the project folder:
    ```bash
    git clone https://github.com/your-username/smart-travel-budgeting.git
    cd smart-travel-budgeting
    ```

2. Use the provided script to install backend and frontend dependencies:
    ```bash
    chmod +x setup.sh
    ./setup.sh
    ```

3. **Start the Backend**:
    - Activate the virtual environment:
        ```bash
        source venv/bin/activate
        ```
    - Run the development server:
        ```bash
        python manage.py runserver
        ```
    - The backend will be available at **http://localhost:8000**.

4. **Start the Frontend**:
    - Navigate to the `frontend` directory:
        ```bash
        cd frontend
        ```
    - Start the Next.js development server:
        ```bash
        npm run dev
        ```
    - The frontend will be available at **http://localhost:3000**.

---

## **How It Works**
- Users can register, log in, and manage their sessions securely.
- Travel suggestions are fetched from **Amadeus API** and transit information from **Google Maps API**.
- Data is cached for 5 minutes to improve performance and reduce API load.
