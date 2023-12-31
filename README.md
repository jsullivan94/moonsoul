# Moon Soul Band Web Page 🌙🎵
Welcome to the official repository for the Moon Soul band's web page. Discover more about the band, view upcoming events, explore our store, and meet the members.

![Moon Soul Logo](client/public/pictures/RNI-Films-IMG-4CCAFE9E-3F30-4DFD-8C71-3D55E9D8410B.jpeg)

## Features
- **Home Page:** Discover upcoming events.
- **Store:** Shop exclusive Moon Soul merchandise from vinyls to apparel.
- **Photos Page:** Dive into the visual journey of the band.
- **About Page:** Meet the personalities and talent of Moon Soul.

## Technologies Used
- **Frontend:** React
- **Backend:** Python & Flask
- **Payment:** Stripe API

## Setup and Installation
### Ensure you have pipenv installed. If not, install it using:
```
pip install pipenv
```
### Clone the repository:
**Using HTTPS:** 
```
git clone https://github.com/jsullivan94/moonsoul.git
```
**Using SSH:**
``` 
git clone git@github.com:jsullivan94/moonsoul.git
```
### Navigate to the project directory:
```
cd moonsoul
```
### Install the required dependencies:
**Frontend:**
```
cd client
```
```
npm install
```
**Backend:**
```
cd server
```
```
pipenv install
```
### Activate the pipenv shell on backend:
```
pipenv shell
```
### Run the project:
**Frontend:**
```
npm start
```
**Backend:**
```
python app.py
```

## Environment Variables
**Stripe API:** The application uses Stripe for payment processing. You'll need to get both a secret key and a publishable key from your Stripe dashboard.

- **STRIPE_SECRET_KEY:** Your Stripe secret key. This should never be committed to the repository or exposed publicly.
- **STRIPE_PUBLISHABLE_KEY:** Your Stripe publishable key. This is safe to use in your frontend code.

- Create a .env file in the root of your project directory.
- Add the following line, replacing the placeholder with your actual key:
```
STRIPE_SECRET_KEY=your_secret_key_here
```
- Replace the key in Checkout.js with your publishable key.

For a complete demo of the web app, refer to this demo video link: https://www.loom.com/share/41a00647c6a2474a9f463de8cb0d81a8

