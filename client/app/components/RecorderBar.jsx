import React from 'react';
import PropTypes from 'prop-types';

import Button from 'components/Button';
import UrlField from 'components/UrlField';

import './RecorderBar.scss';

class RecorderBar extends React.PureComponent {
  static get propTypes() {
    return {
      url: PropTypes.string,
      clickDone: PropTypes.func.isRequired,
      clickSteps: PropTypes.func.isRequired,
    };
  }

  static get defaultProps() {
    return {
      url: '',
    };
  }

  render() {
    return (
      <div className="recorder-bar">
        <div className="recorder-bar__url-field">
          <UrlField url={this.props.url} />
        </div>
        <div className="recorder-bar__button">
          <Button onClick={this.props.clickDone}>Done</Button>
        </div>
        <div className="recorder-bar__button">
          <Button onClick={this.props.clickSteps}>Steps</Button>
        </div>
      </div>
    );
  }
}

export default RecorderBar;

