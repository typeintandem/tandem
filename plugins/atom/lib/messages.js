'use babel';

const EditorProtocolMessageType = Object.freeze({
  ApplyText: 'apply-text',
  ApplyPatches: 'apply-patches',
  CheckDocumentSync: 'check-document-sync',
  ConnectTo: 'connect-to',
  WriteRequest: 'write-request',
  WriteRequestAck: 'write-request-ack',
  NewPatches: 'new-patches',
  UserChangedEditorText: 'user-changed-editor-text',
});

class ConnectTo {
  constructor(host, port) {
    this._type = EditorProtocolMessageType.ConnectTo;
    this._host = host;
    this._port = port;
  }

  getType() {
    return this._type;
  }

  toPayload() {
    return {
      host: this._host,
      port: this._port,
    };
  }

  static fromPayload(payload) {
    return new ConnectTo(payload.host, payload.port);
  }
}

class NewPatches {
  constructor(patchList) {
    this._type = EditorProtocolMessageType.NewPatches;
    this._patchList = patchList;
  }

  getType() {
    return this._type;
  }

  toPayload() {
    return {
      patch_list: this._patchList,
    };
  }

  static fromPayload(payload) {
    return new NewPatches(payload.patchList);
  }
}

class ApplyPatches {
  constructor(patchList) {
    this._type = EditorProtocolMessageType.ApplyPatches;
    this._patchList = patchList;
  }

  getType() {
    return this._type;
  }

  getPatchList() {
    return this._patchList;
  }

  toPayload() {
    return {
      patch_list: this._patchList,
    };
  }

  static fromPayload(payload) {
    return new ApplyPatches(payload.patch_list);
  }
}

class WriteRequest {
  constructor(seq) {
    this._type = EditorProtocolMessageType.WriteRequest;
    this._seq = seq;
  }

  getType() {
    return this._type;
  }

  getSeq() {
    return this._seq;
  }

  toPayload() {
    return {
      seq: this._seq,
    };
  }

  static fromPayload(payload) {
    return new WriteRequest(payload.seq);
  }
}

class WriteRequestAck {
  constructor(seq) {
    this._type = EditorProtocolMessageType.WriteRequestAck;
    this._seq = seq;
  }

  getType() {
    return this._type;
  }

  getSeq() {
    return this._seq;
  }

  toPayload() {
    return {
      seq: this._seq,
    };
  }

  static fromPayload(payload) {
    return new WriteRequestAck(payload.seq);
  }
}

const serialize = message =>
  JSON.stringify({
    type: message.getType(),
    payload: message.toPayload(),
    version: 1,
  });

const deserialize = (data) => {
  try {
    const { type, payload } = JSON.parse(data);

    switch (type) {
      case EditorProtocolMessageType.ConnectTo:
        return ConnectTo.fromPayload(payload);

      case EditorProtocolMessageType.NewPatches:
        return NewPatches.fromPayload(payload);

      case EditorProtocolMessageType.ApplyPatches:
        return ApplyPatches.fromPayload(payload);

      case EditorProtocolMessageType.WriteRequest:
        return WriteRequest.fromPayload(payload);

      case EditorProtocolMessageType.WriteRequestAck:
        return WriteRequestAck.fromPayload(payload);

      default:
        throw new Error();
    }
  } catch (e) {
    throw new Error('Deserialization error.');
  }
};

export default {
  ConnectTo,
  NewPatches,
  ApplyPatches,
  WriteRequest,
  WriteRequestAck,
  serialize,
  deserialize,
};
