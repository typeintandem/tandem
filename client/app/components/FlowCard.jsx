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

  render() {
    return (
      <div className="flow-card">
        <div className={cn('flow-card__icon', { 'flow-card__icon--failed': this.props.flow.status === 'fail', 'flow-card__icon--running': this.props.flow.status === 'running' })} />
        <div className="flow-card__text">
          <div className="flow-card__text__name">{ this.props.flow.name }</div>
          <div className="flow-card__text__last-run">{ this.props.flow.status === 'running' ? 'Running now' : `Last Checked: ${this.props.flow.lastRun}` }</div>
        </div>
        <div className="flow-card__menu">
          <Button className="flow-card__menu__item" onClick={this.props.editFlow}>Edit</Button>
          <Button className="flow-card__menu__item" onClick={this.props.runFlow}>Run</Button>
        </div>
      </div>
    );
  }
}
