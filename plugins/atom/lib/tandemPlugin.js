'use babel';

import { CompositeDisposable } from 'atom';
import {
  createPatches,
  eventForBuffer,
  getStringPort,
  spawnAgent,
} from './utils';
import * as m from './messages';

export default class TandemPlugin {
  constructor() {
    this._isActive = false;
  }

  _getAgentPort() {
    return this._agentPort;
  }

  _initialize(buffer) {
    this._buffer = buffer;
    this._bufferText = buffer.getText();
    this._subscriptions = new CompositeDisposable();

    this._sendPatches = this._sendPatches.bind(this);
    this._subscriptions.add(buffer.onDidChange(this._sendPatches));
    this._processingMessage = false;
  }

  isActive() {
    return this._isActive;
  }

  _sendPatches(event) {
    if (this._processingMessage) {
      return;
    }

    const patches = createPatches(event);
    const message = new m.NewPatches(patches);
    this._agent.stdin.write(m.serialize(message));
    this._agent.stdin.write('\n');
  }

  _startAgent() {
    this._agentPort = getStringPort();
    this._agent = spawnAgent([
      '--port',
      this._agentPort,
      '--log-file',
      `/tmp/tandem-agent-${this._agentPort}.log`,
    ]);
    this._agent.stdin.setEncoding('utf-8');

    if (this._connectTo) {
      const { hostIP, hostPort } = this._connectTo;
      const message = new m.ConnectTo(hostIP, parseInt(hostPort, 10));
      this._agent.stdin.write(m.serialize(message));
      this._agent.stdin.write('\n');
    }

    atom.notifications.addSuccess(`Bound agent to port ${this._agentPort}`);

    this._agent.stdout.setEncoding('utf-8');
    this._agent.stdout.on('data', this._readAgent.bind(this));
  }

  _readAgent(data) {
    // Prevent future 'data' callbacks from being invoked until stream is
    // unpaused
    this._agent.stdout.pause();
    const message = m.deserialize(data);

    if (!this._processingMessage) {
      if (!(message instanceof m.WriteRequest)) {
        console.log('Inavlid message. Expected WriteRequest.');
      } else {
        // Prevent non-Apply Patches messages from being processed
        this._processingMessage = true;

        const ack = new m.WriteRequestAck(message.getSeq());
        this._agent.stdin.write(m.serialize(ack));
        this._agent.stdin.write('\n');
      }
    } else {
      if (!(message instanceof m.ApplyPatches)) {
        console.log('Inavlid message. Expected ApplyPatches');
      } else {
        const patches = message.getPatchList();
        for (let i = 0; i < patches.length; i++) {
          const { oldStart, oldEnd, newText } = patches[i];
          this._buffer.setTextInRange(
            [
              [oldStart.row, oldStart.column],
              [oldEnd.row, oldEnd.column],
            ],
            newText,
          );
        }
        this._processingMessage = false;
      }
    }
    this._agent.stdout.resume();
  }

  _shutDownAgent() {
    this._subscriptions.dispose();
    this._processingMessage = false;
    this._agent.kill('SIGKILL');
    this._isActive = false;
  }

  start(textBuffer, hostIP, hostPort) {
    if (this._isActive) {
      atom.notifications.addError(`Cannot start. An instance is already running on :${this._agentPort}`);
      return;
    }

    if (!!hostIP && !hostPort) {
      atom.notifications.addError('Cannot start. IP specified. You must also provide a port');
      return;
    }

    this._connectTo = hostIP ? Object.freeze({ hostIP, hostPort }) : null;
    this._initialize(textBuffer);

    this._startAgent();
    this._isActive = true;

    if (!this._connectTo) {
      this._sendPatches(eventForBuffer(textBuffer));
    }
  }

  stop() {
    if (!this._isActive) {
      atom.notifications.addError('Cannot stop. No instance running.');
      return;
    }

    this._shutDownAgent();
    atom.notifications.addInfo('Tandem instance shut down.');
  }
}
