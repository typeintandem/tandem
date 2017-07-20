import React from 'react';
import WebView from 'react-electron-web-view';
import PropTypes from 'prop-types';

import constants from '../constants';

import './RecorderWebView.scss';

export default class RecorderWebView extends React.Component {
  static get propTypes() {
    return {
      url: PropTypes.string.isRequired,
    };
  }

  constructor(props) {
    super(props);
    this.state = {
      ready: false,
    };
    this.webview = null;
  }

  onDidFinishLoad() {
    this.webview.executeJavaScript('attachHooks()');
  }

  handleMessage(event) {
    switch (event.channel) {
      case constants.RecorderWebView.EventType.READY:
        this.setState({ ready: true });
        break;
      case constants.RecorderWebView.EventType.CLICK:
        break;
      case constants.RecorderWebView.EventType.KEYUP:
        break;
      default:
        break;
    }
  }

  render() {
    return (
      <div>
        <WebView
          className="recorder-web-view"
          src={this.props.url}
          ref={(view) => { this.webview = view; }}
          onDidFinishLoad={() => { this.onDidFinishLoad(); }}
          onDidStartLoading={() => { this.setState({ ready: false }); }}
          onDidNavigateInPage={() => { this.onDidFinishLoad(); }}
          onIpcMessage={(event) => { this.handleMessage(event); }}
          style={{ height: '100%' }}
          preload="./bundle.guest.js"
        />
      </div>
    );
  }
}
