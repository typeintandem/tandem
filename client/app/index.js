import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter } from 'react-router-dom';
import FlowCheck from './pages/FlowCheck';

/* eslint-disable */
ReactDOM.render((
  <BrowserRouter>
    <FlowCheck />
  </BrowserRouter>
), document.getElementById('app'));
/* eslint-enable */
