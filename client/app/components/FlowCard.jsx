import React from 'react';
import PropTypes from 'prop-types';
import cn from 'classnames';
import Button from 'components/Button';

import './FlowCard.scss';

export default class FlowCard extends React.PureComponent {
  static get propTypes() {
    return {
      flow: PropTypes.object.isRequired,
      runFlow: PropTypes.func.isRequired,
      editFlow: PropTypes.func.isRequired,
    };
  }

  renderSubtext() {
    const getStr = () => {
      const runs = this.props.flow.runs;
      if (runs.length <= 0) {
        return 'Never executed';
      } else if (runs.some(run => !run.start_time)) {
        return 'Waiting to be checked';
      } else if (runs.some(run => !run.complete_time)) {
        return 'Checking now';
      }
      return `Last Checked: ${runs[runs.length - 1].complete_time}`;
    };

    return (
      <div className="flow-card__text__last-run">{ getStr() }</div>
    );
  }

  render() {
    return (
      <div className="flow-card">
        <div className={cn('flow-card__icon', { 'flow-card__icon--running': this.props.flow.runs.some(run => !run.complete_time) })} />
        <div className="flow-card__text">
          <div className="flow-card__text__name">{ this.props.flow.name }</div>
          { this.renderSubtext() }
        </div>
        <div className="flow-card__menu">
          {/* <Button className="flow-card__menu__item" onClick={this.props.editFlow}>Edit</Button> */}
          <Button className="flow-card__menu__item" onClick={() => this.props.runFlow(this.props.flow)}>Run</Button>
        </div>
      </div>
    );
  }
}
