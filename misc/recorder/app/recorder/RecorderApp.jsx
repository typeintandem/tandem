import { Card, Layout, Carousel, Button, Dropdown, Progress } from 'antd';
import React, { Component } from 'react';

import FlowCard from './FlowCard';
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
      done: false,
      percent: 0,
      timeout: null,
    };

    this.setFlowList = this.setFlowList.bind(this);
    this.handleDoneClicked = this.handleDoneClicked.bind(this);
  }

  setFlowList(flowList) {
    this.setState({ flowList });
  }

  innerComponent() {
    if (this.state.website && !this.state.done) {
      return <FlowRecorder setFlow={this.setFlowList} website={this.state.website} />;
    }
    if (this.state.website && this.state.done) {
      const completeText = this.state.percent >= 100 ? 'You\'re all Set!' : '...';
      return (
        <div id="overlay">
          <Card id="spinner2">
            <Progress type="circle" percent={this.state.percent} />
            <h1>{completeText}</h1>
          </Card>
        </div>
      );
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

  handleDoneClicked() {
    this.setState({ done: true });
    this.state.timeout = setTimeout(() => {
      clearTimeout(this.state.timeout);
      const percent = this.state.percent;
      this.setState({ percent: percent + 1 });
      if (percent < 100) {
        this.handleDoneClicked();
      }
    }, 30);
  }

  navBarComponent() {
    if (!this.state.website) {
      return null;
    }
    const overlay = <FlowCard flowList={this.state.flowList} />;
    return (
      <div
        style={{ marginLeft: 'auto' }}
      >
        <Dropdown
          overlay={overlay}
        >
          <Button
            type="primary"
            style={{ marginRight: '20px' }}
            shape="circle"
            icon="down"
          />
        </Dropdown>
        <Button
          type="primary"
          shape="circle"
          icon="check"
          onClick={this.handleDoneClicked}
        />
      </div>
    );
  }


  render() {
    return (
      <div id="recorder">
        <Layout className="layout">
          <Header
            id="header"
            style={{ display: 'flex', alignItems: 'center', position: 'fixed', width: '100%', height: '64px' }}
          >
            <div className="title" >{constants.appName}</div>
            {this.navBarComponent()}
          </Header>
          {this.innerComponent()}
        </Layout>
      </div>
    );
  }
}
