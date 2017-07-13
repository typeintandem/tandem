import React from 'react';

import './Button.scss';

class Button extends React.PureComponent {
  render() {
    return (
      <div className="button" {...this.props} />
    );
  }
}


export default Button;

