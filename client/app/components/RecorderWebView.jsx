import React from 'react';
import WebView from 'react-electron-web-view';
import PropTypes from 'prop-types';

import constants from '../constants';
import Action from '../models/Action';

import './RecorderWebView.scss';

export default class RecorderWebView extends React.Component {
  static get propTypes() {
    return {
      url: PropTypes.string.isRequired,
      addAction: PropTypes.func.isRequired,
      onURLChanged: PropTypes.func.isRequired,
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
        this.props.addAction(new Action(
          constants.ActionType.CLICK,
          event.args[0],
        ));
        break;
      case constants.RecorderWebView.EventType.KEYUP:
        this.props.addAction(new Action(
          constants.ActionType.KEY_PRESS,
          event.args[0],
        ));
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
          onDidNavigate={(event) => { this.props.onURLChanged(event.url); }}
          onIpcMessage={(event) => { this.handleMessage(event); }}
          style={{ height: '100%' }}
          preload="./bundle.guest.js"
        />
      </div>
    );
  }
}
