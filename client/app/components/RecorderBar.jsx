import React from 'react';
import PropTypes from 'prop-types';

import Button from 'components/Button';
import Input from 'components/Input';

import './RecorderBar.scss';

export default class RecorderBar extends React.PureComponent {
  static get propTypes() {
    return {
      url: PropTypes.string,
      editable: PropTypes.bool.isRequired,
      showSteps: PropTypes.bool.isRequired,
      onDone: PropTypes.func.isRequired,
      onSteps: PropTypes.func.isRequired,
    };
  }

  constructor(props) {
    super(props);
    this.state = {
      url: this.props.url || '',
    };
  }

  handleDone() {
    if (this.state.url !== null && this.state.url.trim() !== '') {
      console.log("done!");
      console.log(this.state.url);
      this.props.onDone(this.state.url);
    }
  }

  render() {
    const renderDone = () => {
      if (!this.props.editable) {
        return null;
      }
      return (
        <div className="recorder-bar__button">
          <Button onClick={() => { this.handleDone(); }}>Done</Button>
        </div>
      );
    };

    const renderSteps = () => {
      if(!this.props.showSteps) {
        return null;
      }
      return (
        <div className="recorder-bar__button">
          <Button onClick={this.props.onSteps}>Steps</Button>
        </div>
      );
    }

    return (
      <div className="recorder-bar">
        <div className="recorder-bar__url-field">
          <Input disabled={this.props.url !== null} text={this.state.url} onChange={(value) => { this.setState({ url: value }); }} />
        </div>
        { renderDone() }
        { renderSteps() }
      </div>
    );
  }
}
