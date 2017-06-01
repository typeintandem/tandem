import React from 'react';
import { Card, Button } from 'antd';
import constants from '../constants';

const Splash = () => (
  <Card className="card">
    <h1>{constants.productName}</h1>
    <h2 style={{ marginTop: '-30px' }}>Welcome to {constants.appName}</h2>
    <h3 style={{ marginTop: '25px' }}>
      {constants.appName} helps you describe the flows you want to monitor and protect.
    </h3>
    <Button type="primary" style={{ height: '50px',  marginTop: '40px', marginBottom: '40px' }}>
      Get Started
    </Button>
  </Card>
);

export default Splash;
