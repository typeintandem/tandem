import React from 'react';
import PropTypes from 'prop-types';

import './RecorderWebView.scss';

export default class RecorderWebView extends React.PureComponent {
  static get propTypes() {
    return {
      url: PropTypes.string.isRequired,
    };
  }

  render() {
    return (
      <div className="recorder-web-view">
        <webview
          src={this.props.url}
          style={{ height: '100%' }}
        />
      </div>
    );
  }
}
