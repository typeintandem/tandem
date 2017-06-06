import { Layout, Carousel, Button, Dropdown } from 'antd';
import React, { Component } from 'react';

import FlowStarter from './FlowStarter';
import FlowRecorder from './FlowRecorder';
import Splash from './Splash';
import constants from '../constants';

import './RecorderApp.scss';

const { Header, Content } = Layout;

export default class RecorderApp extends Component {
  constructor(props) {
    super(props);
    this.state = {
      website: null,
      flowList: null,
    };

    this.setFlowList = this.setFlowList.bind(this);
  }

  setFlowList(flowList) {
    this.setState({ flowList });
  }

  innerComponent() {
    if (this.state.website) {
      return <FlowRecorder setFlow={this.setFlowList} website={this.state.website} />;
    }
    return (
      <Content style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        <Carousel dots="false" className="carousel">
          <div><Splash /></div>
          <div><FlowStarter onSubmit={website => this.setState({ website })} /></div>
        </Carousel>
      </Content>
    );
  }

  navBarComponent() {
    if (!this.state.website) {
      return null;
    }
    const overlay = <p>{this.state.flowList ? this.state.flowList.toString() : 'No Flows.' }</p>;
    return (
      <div style={{ marginLeft: 'auto' }}>
        <Dropdown overlay={overlay}>
          <Button type="primary" style={{ marginRight: '20px' }} shape="circle" icon="down" />
        </Dropdown>
        <Button type="primary" shape="circle" icon="check" />
      </div>
    );
  }


  render() {
    return (
      <div id="recorder">
        <Layout className="layout">
          <Header id="header" style={{ display: 'flex', alignItems: 'center', position: 'fixed', width: '100%', height: '64px' }}>
            <div className="title" >{constants.appName}</div>
            {this.navBarComponent()}
          </Header>
          {this.innerComponent()}
        </Layout>
      </div>
    );
  }
}
