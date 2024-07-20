import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import Cookies from 'js-cookie';
import { PATHS } from '../../utils/constants';

const ProtectedRoute = () => {
  const token = Cookies.get('token');
  return token ? <Outlet /> : <Navigate to={PATHS["LOGIN"]} />;
};

export default ProtectedRoute;
