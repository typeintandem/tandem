import React from 'react';
import { Link } from 'react-router-dom';

import './Navbar.scss';

export default class Navbar extends React.Component {
  render() {
    return (
      <div className="navbar">
        <Link to={'/'}><div className="navbar__logo" /></Link>
        <div className="navbar__menu">
          <Link to={'/dashboard'}><span className="navbar__menu__item">Dashboard</span></Link>
          <Link to={'/recorder'}><span className="navbar__menu__item">Recorder</span></Link>
        </div>
      </div>
    );
  }
}
