import React from 'react';
import PropTypes from 'prop-types';

import './Input.scss';

export default class Input extends React.Component {
  static get propTypes() {
    return {
      text: PropTypes.string,
      type: PropTypes.string,
      onChange: PropTypes.func,
      placeholder: PropTypes.string,
      disabled: PropTypes.bool,
    };
  }

  static get defaultProps() {
    return {
      text: '',
      placeholder: '',
      type: 'text',
      onChange: () => {},
      disabled: false,
    };
  }

  constructor(props) {
    super(props);
    this.state = {
      text: this.props.text,
    };
  }

  handleChange(event) {
    const value = event.target.value;
    this.setState({ text: value });
    this.props.onChange(value);
  }

  render() {
    return (
      <input
        className="input"
        type={this.props.type}
        value={this.state.text}
        placeholder={this.props.placeholder}
        onChange={(event) => { this.handleChange(event); }}
        disabled={this.props.disabled}
      />
    );
  }
}
