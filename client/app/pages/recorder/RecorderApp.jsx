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
        <RecorderBar url={this.state.url} clickDone={() => {}} clickSteps={() => {}} />
        { renderSetup() }
        { renderWebView() }
      </div>
    );
  }
}
