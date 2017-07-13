import React from 'react';

import './Button.scss';

export default class Button extends React.PureComponent {
  render() {
    return (
      <div className="button" {...this.props} />
    );
  }
}
