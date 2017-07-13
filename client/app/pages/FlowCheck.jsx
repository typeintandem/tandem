import React from 'react';
import { Switch, Route } from 'react-router-dom';

import RecorderApp from 'recorder-app'; // eslint-disable-line

import Navbar from '../components/Navbar';
import DashboardApp from './dashboard/DashboardApp';
import LandingApp from './landing/LandingApp';

import './FlowCheck.scss';

export default () => (
  <div className="flow-check">
    <Navbar />
    <Switch>
      <Route exact path="/" component={LandingApp} />
      <Route exact path="/dashboard" component={DashboardApp} />
      <Route exact path="/recorder" component={RecorderApp} />
    </Switch>
  </div>
);
