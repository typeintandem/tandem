import React from 'react';
import RecorderBar from 'components/RecorderBar';
import RecorderWebView from 'components/RecorderWebView';

import './RecorderApp.scss';

export default class RecorderApp extends React.Component {
  render() {
    return (
      <div className="recorder">
        <RecorderBar url={'http://www.jamiboy.com/'} clickDone={() => {}} clickSteps={() => {}} />
        <RecorderWebView url={'http://www.jamiboy.com/'} />
      </div>
    );
  }
}
