import uuid from 'uuid';
import DocumentStore from '../stores/document';

/*
 * API Name: replicateDocument
 * Returns: A replica of the local document
 * Used for sending the local document to a new agent
 */
export default () => DocumentStore.getDocument().replicate(uuid());
