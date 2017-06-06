import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { title } from '../constants';

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
    this.props.onSubmit(this.state.value);
    event.preventDefault();
  }

  render() {
    return (
      <div>
        <div className="app-header">
          <h1>{title}</h1>
        </div>
        <span>Website:</span>
        <form onSubmit={this.handleSubmit}>
          <input type="text" value={this.state.value} onChange={this.handleChange} />
          <input type="submit" value="Start Recording" />
        </form>
      </div>
    );
  }
}

export default FlowStarter;
