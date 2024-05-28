import React from 'react';
import { Link, useNavigate } from 'react-router-dom';

function Header() {
  const navigate = useNavigate();
  const token = localStorage.getItem('token');

  const handleLogout = () => {
    // Clear the authentication token
    localStorage.removeItem('token');
    // Redirect to login page
    navigate('/login');
  };

  return (
    <header>
      <nav>
        {!token ? (
          <>
          </>
        ) : (
          <button onClick={handleLogout}>Logout</button>
        )}
      </nav>
    </header>
  );
}

export default Header;