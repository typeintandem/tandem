import React from 'react';
import DashboardView from 'components/DashboardView';

export default class DashboardApp extends React.Component {
  constructor() {
    super();

    fetch('http://localhost:8080/api/flows', { method: 'GET' })
      .then(response => response.json())
      .then(flows => Promise.all(flows.map(flow => (
        fetch(`http://localhost:8080/api/runs/${flow.id}`, { method: 'GET' })
          .then(response => response.json())
          .then(runs => Object.assign({}, flow, { runs }))))))
      .then(flows => this.setState({ flows }));

    this.state = {
      flows: [],
    };
  }

  runFlow(flow) {
    fetch(`http://localhost:8080/api/run/${flow.id}`, { method: 'POST' });
  }

  render() {
    return (
      <DashboardView
        flows={this.state.flows}
        runFlow={flow => this.runFlow(flow)}
        runFlows={() => this.state.flows.forEach(flow => this.runFlow(flow))}
        editFlow={() => {}}
      />
    );
  }
}
