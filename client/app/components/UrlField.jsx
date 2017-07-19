import React from 'react';
import PropTypes from 'prop-types';

import './URLField.scss';

export default class URLField extends React.PureComponent {
  static get propTypes() {
    return {
      url: PropTypes.string.isRequired,
    };
  }

  render() {
    return (
      <div className="url-field">
        {this.props.url}
      </div>
    );
  }
}
