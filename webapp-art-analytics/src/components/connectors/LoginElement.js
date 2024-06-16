import React from 'react';
import { Link } from 'react-router-dom';

function LoginElement({
    handleSubmit,
    email,
    password,
    error,
    message,
    setEmail,
    setPassword
}) {
 
  return (
        <div className="login-form">
          <h2>Login</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Email:</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email"
                required
              />
            </div>
            <div className="form-group">
              <label>Password:</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                required
              />
            </div>
            <button type="submit" className="login-button">Login</button>
          </form>
          {message && <p className="message">{message}</p>}
          {error && <p className="error">{error}</p>}
          <hr className="login-delimiter" />
          <div className='login-trial'>
            <p><Link to="/reset-password">Mot de passe oublié ?</Link> | Pas encore inscrit, <Link to="/trial">Essayez gratuitement</Link> </p>
          </div>
        </div>
  );
}

export default LoginElement;