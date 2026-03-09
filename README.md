# TravelGo – Cloud-Based Travel Booking System

TravelGo is a cloud-enabled travel booking platform that allows users to search and reserve **buses, trains, flights, and hotels** through a single system.

The application is built using **Flask** and deployed on **AWS EC2**, with **Amazon DynamoDB** used for scalable data storage and **AWS SNS** for booking notifications.

---

## Live Application

🌐 Frontend (CloudFront)  
http://d227ru6ryvnghn.cloudfront.net

---

# Features

## User Management
- User Registration
- Secure Login
- Session Management
- User-based booking records

## Travel Booking
Users can search and book:

- Bus
- Train
- Flight
- Hotels

## Filtering Options
Users can filter results based on:

- Route / Destination
- Travel Date
- Budget
- Travel Category
- Hotel Type (Luxury, Budget, Family)

## Seat Selection
- Dynamic seat selection system
- View available seats
- Choose preferred seats
- Prevent double bookings

## Booking System
- Booking summary
- Payment simulation
- Booking confirmation
- Booking cancellation

## Notifications
Booking confirmations and cancellations trigger **AWS SNS notifications**.

---

# Cloud Architecture

TravelGo integrates multiple AWS services to create a scalable cloud-based system.

## AWS Services Used
- Amazon EC2
- Amazon DynamoDB
- Amazon SNS
- Amazon CloudFront
- Amazon CloudWatch
- Flask
- boto3

---

# System Workflow

1. User registers or logs into the system  
2. User searches for travel options (bus/train/flight/hotel)  
3. Filters results based on preferences  
4. Selects seats or hotel room  
5. Confirms booking  
6. Payment simulation occurs  
7. Booking stored in DynamoDB  
8. SNS sends booking confirmation notification  
9. Users can view or cancel bookings  

---

# Project Architecture

```
User Browser
     │
     ▼
CloudFront (Frontend Delivery)
     │
     ▼
Flask Web Application
     │
 ┌───────────────┬───────────────┐
 ▼               ▼               ▼
DynamoDB        SNS         CloudWatch
(Database)   (Notifications)  (Monitoring)
     │
     ▼
EC2 Hosting
(Gunicorn + Nginx)
```

---

# Database Design

## Users Table

| Attribute | Description |
|----------|-------------|
| UserID | Unique user identifier |
| Name | User name |
| Email | User email |
| Password | Encrypted password |

---

## Transport Listings Table

| Attribute | Description |
|----------|-------------|
| TransportID | Unique transport identifier |
| TransportType | Bus / Train / Flight |
| Route | Source to Destination |
| Date | Travel date |
| SeatAvailability | Available seats |

---

## Hotels Table

| Attribute | Description |
|----------|-------------|
| HotelID | Unique hotel identifier |
| Name | Hotel name |
| Category | Luxury / Budget / Family |
| Location | City / Area |
| Price | Cost per night |

---

## Bookings Table

| Attribute | Description |
|----------|-------------|
| BookingID | Unique booking ID |
| UserID | User who booked |
| TransportType | Bus / Train / Flight / Hotel |
| Date | Booking date |
| Status | Confirmed / Cancelled |

---

# ER Diagram

![ER Diagram](er_diagram.png)

Place your ER diagram image in the project folder and name it **er_diagram.png**.

---

# Project Structure

```
TravelGo
│
├── app.py
├── requirements.txt
│
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── search.html
│   ├── booking_summary.html
│
├── static/
│   ├── css/
│   ├── js/
│
├── aws/
│   ├── dynamodb_config.py
│   ├── sns_notifications.py
│
└── README.md
```

---

# Installation (Local Setup)

## 1 Clone Repository

```
git clone https://github.com/yourusername/travelgo.git
cd travelgo
```

## 2 Install Dependencies

```
pip install -r requirements.txt
```

## 3 Configure AWS Credentials

```
aws configure
```

Provide:

- AWS Access Key  
- AWS Secret Key  
- Region  

---

## 4 Run Flask Application

```
python app.py
```

Application runs at:

```
http://localhost:5000
```

---

# Deployment

TravelGo is deployed using:

- **Amazon EC2** for hosting
- **Gunicorn** as WSGI server
- **Nginx** as reverse proxy
- **Amazon CloudFront** for frontend delivery

Deployment steps include:

- Launch EC2 instance
- Install Python and dependencies
- Configure Gunicorn
- Configure Nginx
- Connect DynamoDB
- Set up SNS topic
- Deploy static files via CloudFront

---

# Monitoring

The application uses:

- Amazon CloudWatch for logs and metrics
- DynamoDB monitoring for read/write usage
- EC2 monitoring for CPU and memory usage

---

# Learning Outcomes

This project demonstrates skills in:

- Cloud-based application development
- Backend development with Flask
- NoSQL database design
- AWS deployment and infrastructure
- Notification systems using SNS
- Monitoring using CloudWatch

---

# Future Improvements

- Payment gateway integration
- User dashboard
- Booking history analytics
- Mobile responsive UI
- Containerization with Docker
- CI/CD pipeline

---

# Author

Your Name

GitHub  
https://github.com/yourusername
