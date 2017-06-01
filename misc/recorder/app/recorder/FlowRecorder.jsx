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
      setFlow: PropTypes.func.isRequired,
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
      let targetString = `<${event.args[1]}`;
      if (event.args[2]) {
        targetString += ` id="${event.args[2]}"`;
      }
      if (event.args[3]) {
        targetString += ` class="${event.args[3]}"`;
      }
      let text = event.args[4];
      if (text && text !== '') {
        if (text.length > 10) {
          text = `${text.substr(0, 10)}...`;
        }
        targetString += ` />${text}</${event.args[2]}`;
      }
      targetString += '>';
      this.flowList.addAction(
        constants.EventType.CLICK, /* action */
        event.args[0], /* key */
        targetString,
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
    this.props.setFlow(this.flowList);
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
