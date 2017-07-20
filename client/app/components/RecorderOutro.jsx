import React from 'react';
import PropTypes from 'prop-types';

import Button from './Button';
import Input from './Input';

export default class RecorderOutro extends React.Component {
  static get propTypes() {
    return {
      onSubmit: PropTypes.func.isRequired,
    };
  }

  constructor(props) {
    super(props);
    this.state = {
      name: '',
      frequency: '',
    };
  }

  render() {
    return (
      <div className="recorder-outro">
        <div className="recorder-outro__name">
          <div>Enter name:</div>
          <Input
            onChange={(value) => { this.setState({ name: value }); }}
          />
        </div>
        <div className="recorder-outro__freqency">
          <div>Enter frequency:</div>
          <Input
            onChange={(value) => { this.setState({ frequency: value }); }}
          />
        </div>
        <div className="recorder-outro__submit_button">
          <Button
            onClick={() => { this.props.onSubmit(this.state.name, this.state.frequency); }}
          >
            Submit
          </Button>
        </div>
      </div>
    );
  }
}
