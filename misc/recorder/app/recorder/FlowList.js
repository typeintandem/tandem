import Action from './Action';

export default class FlowList {
  constructor() {
    this.actions = [];
  }

  addAction(action, key, target) {
    this.actions.push(new Action(action, key, target));
    // TODO: Add result?
  }

  // TODO: Serialize any other information
  toString() {
    return this.actions.toString();
  }
}
