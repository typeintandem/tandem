import DocumentStore from '../stores/document';

/*
 * API Name: setDocument
 * Returns: null
 * Used for assigning the local document to a new document
 */
export default (newDocument) => {
    DocumentStore.setDocument(newDocument);
};
