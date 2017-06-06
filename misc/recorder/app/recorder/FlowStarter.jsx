import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { Card, Form, Button, Input } from 'antd';

import './FlowStarter.scss';

class FlowStarter extends Component {
  static get propTypes() {
    return {
      onSubmit: PropTypes.func.isRequired,
    };
  }

  constructor(props) {
    super(props);
    this.state = {
      value: '',
    };
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleChange = this.handleChange.bind(this);
  }

  handleChange(event) {
    this.setState({ value: event.target.value });
  }

  handleSubmit(event) {
    this.props.onSubmit(`http://${this.state.value}`);
    event.preventDefault();
  }

  render() {
    return (
      <Card className="card center">
        <Form onSubmit={this.handleSubmit} className="login-form">
          <h2>Enter your URL</h2>
          <div className="login-form-width-restrict">
            <Input addonBefore="http://" type="text" placeholder="www.yelp.com" value={this.state.value} onChange={this.handleChange} style={{ padding: '20px', marginTop: '0px' }} />

            <Button type="primary" htmlType="submit" className="login-form-button" style={{ width: '60%', height: '50px', marginTop: '60px' }}>
              Start Recording
            </Button>
          </div>
        </Form>
      </Card>
    );
  }
}

export default FlowStarter;
