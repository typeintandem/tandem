import React from 'react';

import RecorderBar from 'components/RecorderBar';
import RecorderOutro from 'components/RecorderOutro';
import RecorderSetup from 'components/RecorderSetup';
import RecorderWebView from 'components/RecorderWebView';

import Action from 'models/Action';
import Flow from 'models/Flow';

import constants from '../../constants';

export default class RecorderApp extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      url: null,
      actions: [],
      finalURL: null,
      showOutro: false,
    };
  }

  completeFlow(name, frequency) {
    const actions = this.state.actions;
    actions.push(new Action(
      constants.ActionType.ASSERT_URL,
      this.state.finalURL,
    ));

    const flow = new Flow(
      name,
      frequency,
      this.state.url,
      actions,
    );
    // TODO: Send flow to API

    this.setState({
      url: null,
      actions: [],
      finalURL: null,
      showOutro: false,
    });
  }

  addAction(action) {
    const actions = this.state.actions;
    actions.push(action);
    this.setState({ actions });
  }


  render() {
    const renderSetup = () =>
      (this.state.url ? null : <RecorderSetup />);

    const renderWebView = () =>
      (!this.state.url || this.state.showOutro ?
        null :
        <RecorderWebView
          url={this.state.url}
          addAction={(a) => { this.addAction(a); }}
          onURLChanged={(url) => { this.setState({ finalURL: url }); }}
        />
      );

    const renderOutro = () =>
      (!this.state.showOutro ?
        null :
        <RecorderOutro
          onSubmit={(name, frequency) => { this.completeFlow(name, frequency); }}
        />
      );

    return (
      <div className="recorder">
        <RecorderBar
          editable={this.state.url === null}
          url={this.state.url}
          showNavigationOptions={this.state.url !== null && !this.state.showOutro}
          onGo={(value) => { this.setState({ url: value, finalURL: value }); }}
          onSteps={() => {}}
          onDone={() => { this.setState({ showOutro: true }); }}
        />
        { renderSetup() }
        { renderWebView() }
        { renderOutro() }
      </div>
    );
  }
}
