import React, { useState } from 'react';

/* Det här dokumentet är till för att göra en sorts rund rektangel, (ser lite ut som en mobiltelefon),
som vi ser på login skärmen. Vi har input för användaren att interagera med 'databasen' för att antingen logga in
eller skapa en ny användare med Register knappen. Än sålänge har vi inte använt google eller facebook tjänster
för att införa login. Det är enkelt att implimentera men jag tycker att det inte är bra för vår uppgift. */

function PhoneForm() {
    const [showPassword, setShowPassword] = useState(false);

    const togglePasswordVisibility = () => {
        setShowPassword(!showPassword);
    };

    return (
        <div className="phone-form">
            <label htmlFor="email">Email or Username</label>
            <input type="text" id="email" placeholder="Email or Username" />

            <label htmlFor="password">Password</label>
            <div className="password-input">
                <input type={showPassword ? "text" : "password"} id="password" placeholder="Password" />
                <button onClick={togglePasswordVisibility} className="toggle-password" type="button">
                    {showPassword ? (
                        // Super long copy & paste länk från w3 schools.
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="feather feather-eye-off"><path d="M17.94 17.94A10 10 0 0 0 21 12c-1.74-4.41-7-7-9-7-1.26 0-2.4.38-3.4 1.02"/><path d="M1 1l22 22"/><path d="M9.9 4.24A9.958 9.958 0 0 0 3 12c1.74 4.41 7 7 9 7 1.26 0 2.4-.38 3.4-1.02"/><circle cx="12" cy="12" r="3"/></svg>
                    ) : (
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="feather feather-eye"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                    )}
                </button>
            </div>

            <button className="login-button">login</button>
            <a href="#" className="forgot-password">Forgot your password?</a>
        </div>
    );
}

export default PhoneForm;