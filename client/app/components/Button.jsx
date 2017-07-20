import React from 'react';
import PropTypes from 'prop-types';
import cn from 'classnames';

import './Button.scss';

export default class Button extends React.PureComponent {
  static get propTypes() {
    return {
      className: PropTypes.string,
    };
  }

  static get defaultProps() {
    return {
      className: '',
    };
  }

  render() {
    const { className, ...props } = this.props;
    return (
      <div className={cn('button', className)} {...props} />
    );
  }
}
