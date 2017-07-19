import React from 'react';
import PropTypes from 'prop-types';
import HeroBanner from 'components/HeroBanner';
import FlowCard from 'components/FlowCard';
import Button from 'components/Button';
import { Link } from 'react-router-dom';

import './DashboardView.scss';

export default class DashboardView extends React.PureComponent {
  static get propTypes() {
    return {
      flows: PropTypes.array.isRequired,
      runFlow: PropTypes.func.isRequired,
      runFlows: PropTypes.func.isRequired,
      editFlow: PropTypes.func.isRequired,
    };
  }

  renderHeroBanner() {
    const heroText = this.props.flows.every(flow => flow.pass) ?
      'All tests are passings!' :
      'There are failing flows!';

    return <HeroBanner text={heroText} />;
  }

  render() {
    return (
      <div className="dashboard-view">
        { this.renderHeroBanner() }
        <div className="dashboard-view__menu">
          <Link to={'recorder'}><Button className="dashboard-view__menu__item">New Flow</Button></Link>
          <Button className="dashboard-view__menu__item" onClick={this.props.runFlows()}>Run All</Button>
        </div>
        <div className="dashboard-view__flow-list">
          { this.props.flows.map(flow => (
            <FlowCard
              key={flow.id}
              flow={flow}
              runFlow={() => this.props.runFlow(flow)}
              editFlow={() => this.props.editFlow(flow)}
            />
          )) }
        </div>
      </div>
    );
  }
}
