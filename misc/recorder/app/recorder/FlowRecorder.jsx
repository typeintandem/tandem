import React, { Component } from 'react';
import WebView from 'react-electron-web-view';
import PropTypes from 'prop-types';
import { Spin } from 'antd';

import constants from '../constants';
import FlowList from './FlowList';
import './FlowRecorder.scss';

class FlowRecorder extends Component {
  static get propTypes() {
    return {
      website: PropTypes.string.isRequired,
    };
  }

  constructor(props) {
    super(props);
    this.state = {
      ready: false,
    };
    this.webview = null;
    this.handleMessage = this.handleMessage.bind(this);
    this.onDidFinishLoad = this.onDidFinishLoad.bind(this);
    this.flowList = new FlowList();
  }

  onDidFinishLoad() {
    this.webview.executeJavaScript('attachHooks()');
  }

  handleMessage(event) {
    if (event.channel === constants.EventType.READY) {
      this.setState({ ready: true });
      console.log(event.args[0]);
    }
    if (event.channel === constants.EventType.CLICK) {
      this.flowList.addAction(
        constants.EventType.CLICK, /* action */
        event.args[0], /* key */
        `<${event.args[1]} id=${event.args[2]} class=${event.args[3]}`, /* target */
      );
      console.log(this.flowList);
    }
    if (event.channel === constants.EventType.KEYUP) {
      this.flowList.addAction(
        constants.EventType.KEYUP, /* action */
        event.args[0], /* key */
        'TODO', /* target */
      );
      console.log(this.flowList);
    }
  }

  render() {
    const webviewStyles = {
      height: '95vh',
      display: 'block',
    };
    let overlay;
    if (!this.state.ready) {
      overlay = (
        <div id="overlay">
          <Spin
            id="spinner"
            tip="Please Wait..."
            size="large"/>
        </div>
      );
    }
    return (
      <div className="center">
        <span>{this.props.website}</span>
        {overlay}
        <WebView
          src={this.props.website}
          style={webviewStyles}
          ref={(view) => { this.webview = view; }}
          onDidFinishLoad={this.onDidFinishLoad}
          onDidStartLoading={() => { this.setState({ ready: false }); }}
          onDidNavigateInPage={this.onDidFinishLoad}
          onIpcMessage={this.handleMessage}
          preload="./bundle.guest.js"
        />
      </div>
    );
  }
}

export default FlowRecorder;
