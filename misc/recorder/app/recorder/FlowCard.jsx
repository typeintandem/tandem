import React, { Component } from 'react';
import { Card } from 'antd';
import PropTypes from 'prop-types';
import constants from '../constants';

class FlowCard extends Component {
  static get propTypes() {
    return {
      flowList: PropTypes.object,
    };
  }

  getRows() {
    if (!this.props.flowList || this.props.flowList.actions.length === 0) {
      return ['No Actions Taken'];
    }
    const actions = this.props.flowList.actions;
    let i = 0;
    let word = '';
    const rows = [];
    while (i < actions.length)  {
      const curr = actions[i];
      if (curr.action === constants.EventType.KEYUP) {
        word += curr.key;
      } else {
        if (word !== '') {
          rows.push(`TYPED in "${word}"`);
          word = '';
        }
        rows.push(`${curr.action} on ${curr.target}`);
      }
      i += 1;
    }
    if (word !== '') {
      rows.push(`TYPED in "${word}"`);
    }
    return rows;
  }

  render() {
    const rows = this.getRows()
      .map((r, a) => <p key={a}>{r}</p>);
    return (
      <Card className="card">
        {rows}
      </Card>
    );
  }
}

export default FlowCard;
