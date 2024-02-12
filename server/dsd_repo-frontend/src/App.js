import React from 'react';
import './App.css';
import logo from './assets/logo.png';
import PhoneForm from './components/PhoneForm';

// Det här är huvud javascript appen. Här ligger "Creative Studios logon"
// och till höger ligger log in skärmen.

function App() {
  return (
    <div className="App">
      <div className="App-header">
        <img src={logo} alt="logo" className='App-logo' />
        <PhoneForm />
      </div>
    </div>
  );
}

export default App;
