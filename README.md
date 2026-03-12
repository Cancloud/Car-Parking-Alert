# Car Parking Notification App

A minimal viable Streamlit web application designed to help users quickly report parking wardens and alert others in the area. 

## Features
- **Fast Reporting:** A prominent, mobile-friendly button to instantly log a warden sighting.
- **Recent Alerts:** See the last 10 alerts in real-time.
- **User Authentication:** Simple License Plate and Password registration/login system.
- **Admin Dashboard:** Specific 'ADMIN-X' users can view all registered users, download full alert histories to CSV, and manage the database.

## Local Setup

### 1. Prerequisites
Ensure you have Python installed, then install the required dependencies:
```bash
pip install -r requirements.txt
```

### 2. Run the Application
Start the Streamlit server locally:
```bash
streamlit run app.py
```
*Note: A local SQLite database (`parking.db`) will be automatically generated on the first run.*

### 3. Access
- **Local URL:** `http://localhost:8501`
- **Network URL:** `http://<your-local-ip>:8501` (Great for testing the mobile UI on your phone!)

## Admin Access
By default, the application is configured with the following Admin License Plates:
- `ADMIN-1`
- `ADMIN-2`
- `ADMIN-3`
- `ADMIN-4`
- `ADMIN-5`

*Default Password:* `admin888`

*(You can easily modify these in the `admin_list` variable at the top of `app.py`)*
