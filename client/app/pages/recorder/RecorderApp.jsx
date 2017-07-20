import React from 'react';

import RecorderBar from 'components/RecorderBar';
import RecorderSetup from 'components/RecorderSetup';
import RecorderWebView from 'components/RecorderWebView';

export default class RecorderApp extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      url: null,
    };
  }


  render() {
    const renderSetup = () =>
      (this.state.url ? null : <RecorderSetup />);

    const renderWebView = () =>
      (!this.state.url ? null : <RecorderWebView url={this.state.url} />);

    return (
      <div className="recorder">
        <RecorderBar
          editable={this.state.url === null}
          url={this.state.url}
          showSteps={this.state.url !== null}
          onDone={(value) => { this.setState({ url: value }); }}
          onSteps={() => {}}
        />
        { renderSetup() }
        { renderWebView() }
      </div>
    );
  }
}
