import React, { Component } from 'react';
import WebView from 'react-electron-web-view';
import PropTypes from 'prop-types';
import './FlowRecorder.scss';

class FlowRecorder extends Component {
  static get propTypes() {
    return {
      website: PropTypes.string.isRequired,
    };
  }

  constructor(props) {
    super(props);
    this.webview = null;
    this.handleMessage = this.handleMessage.bind(this);
    this.onDidFinishLoad = this.onDidFinishLoad.bind(this);
  }

  onDidFinishLoad() {
    this.webview.executeJavaScript('attachHooks()');
  }

  // eslint-disable-next-line class-methods-use-this
  handleMessage(event) {
    // eslint-disable-next-line no-console
    console.log(event.channel);
  }

  render() {
    const webviewStyles = {
      height: '95vh',
      display: 'block',
    };
    return (
      <div className="center">
        <span>{this.props.website}</span>
        <WebView
          src={this.props.website}
          style={webviewStyles}
          ref={(view) => { this.webview = view; }}
          onDidFinishLoad={this.onDidFinishLoad}
          onIpcMessage={this.handleMessage}
          preload="./bundle.guest.js"
        />
      </div>
    );
  }
}

export default FlowRecorder;
