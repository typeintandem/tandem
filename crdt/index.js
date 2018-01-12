import uuid from 'uuid';
import { Document } from '@atom/teletype-crdt';
import DocumentStore from './stores/document';
import api from './api';
import io from './io';

const localDocument = new Document({ siteId: uuid(), text: '' });
DocumentStore.setDocument(localDocument);

const processPayload = (payload) => {
    const { function: fcn, parameters: params = [] } = JSON.parse(payload);
    const res = { value: api[fcn](...params) };

    io.write(JSON.stringify(res));
};

io.addIoHandler(processPayload);
