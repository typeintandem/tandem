import React from 'react';
import PropTypes from 'prop-types';

import Button from 'components/Button';
import Input from 'components/Input';

import './RecorderBar.scss';

export default class RecorderBar extends React.Component {
  static get propTypes() {
    return {
      url: PropTypes.string,
      editable: PropTypes.bool.isRequired,
      showNavigationOptions: PropTypes.bool.isRequired,
      onGo: PropTypes.func.isRequired,
      onSteps: PropTypes.func.isRequired,
      onDone: PropTypes.func.isRequired,
    };
  }

  static get defaultProps() {
    return {
      url: '',
    };
  }

  constructor(props) {
    super(props);
    this.state = {
      url: this.props.url || '',
    };
  }

  handleGo() {
    if (this.state.url !== null && this.state.url.trim() !== '') {
      this.props.onGo(this.state.url);
    }
  }

  render() {
    const renderGo = () => {
      if (!this.props.editable) {
        return null;
      }
      return (
        <div className="recorder-bar__button">
          <Button onClick={() => { this.handleGo(); }}>Go</Button>
        </div>
      );
    };

    const renderDone = () => {
      if (!this.props.showNavigationOptions) {
        return null;
      }
      return (
        <div className="recorder-bar__button">
          <Button onClick={this.props.onDone}>Done</Button>
        </div>
      );
    };

    const renderSteps = () => {
      if (!this.props.showNavigationOptions) {
        return null;
      }
      return (
        <div className="recorder-bar__button">
          <Button onClick={this.props.onSteps}>Steps</Button>
        </div>
      );
    };

    return (
      <div className="recorder-bar">
        <div className="recorder-bar__url-field">
          <Input
            disabled={this.props.url !== null}
            text={this.state.url}
            onChange={(value) => { this.setState({ url: value }); }}
          />
        </div>
        { renderGo() }
        { renderDone() }
        { renderSteps() }
      </div>
    );
  }
}
