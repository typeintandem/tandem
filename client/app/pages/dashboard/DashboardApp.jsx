import React from 'react';
import DashboardView from 'components/DashboardView';

export default class DashboardApp extends React.Component {
  constructor() {
    super();
    this.state = {
      flows: [
        { id: 3, name: 'Another Flow', lastRun: '', status: 'running' },
        { id: 1, name: 'Login Flow', lastRun: '2 minutes ago', status: 'pass' },
        { id: 2, name: 'Checkout Flow', lastRun: '5 minutes ago', status: 'fail' },
      ],
    };
  }

  render() {
    return (
      <DashboardView
        flows={this.state.flows}
        runFlow={() => {}}
        runFlows={() => {}}
        editFlow={() => {}}
      />
    );
  }
}
