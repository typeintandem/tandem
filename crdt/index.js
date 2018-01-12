import uuid from 'uuid';
import { Document } from '@atom/teletype-crdt';
import DocumentStore from './stores/document';
import api from './api';
// import io from './io';

const localDocument = new Document({ siteId: uuid(), text: '' });
DocumentStore.setDocument(localDocument);

console.log(api.setTextInRange(
    { column: 0, row: 0 },
    { column: 0, row: 0 },
    'hello, world!',
));
console.log();
console.log(api.getDocumentText());
