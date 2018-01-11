import DocumentStore from '../stores/document';

/*
 * API Name: setTextInRange
 * Returns: An array of CRDT operations to be broadcasted to the other documents
 * Used for applying the plugin changes to the CRDT document
 */
export default (start, end, text, options) =>
    DocumentStore.getDocument().setTextInRange(start, end, text, options);
