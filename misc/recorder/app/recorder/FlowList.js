import Action from './Action';

export default class FlowList {
  constructor() {
    this.actions = [];
    this.finalUrl = null;
  }

  addAction(action, key, target) {
    this.actions.push(new Action(action, key, target));
  }

  toString() {
    return `${this.actions.toString()} - ${this.finalUrl}`;
  }
}
