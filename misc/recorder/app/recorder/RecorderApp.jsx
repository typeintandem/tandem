import React, { Component } from 'react';

import FlowStarter from './FlowStarter';
import FlowRecorder from './FlowRecorder';
import './RecorderApp.scss';

export default class RecorderApp extends Component {
  constructor(props) {
    super(props);
    this.state = {
      website: null,
    };
  }

  render() {
    let innerComponent;
    if (this.state.website) {
      innerComponent = <FlowRecorder website={this.state.website} />;
    } else {
      innerComponent = <FlowStarter onSubmit={website => this.setState({ website })} />;
    }
    return (
      <div className="app">
        {innerComponent}
      </div>
    );
  }
}
