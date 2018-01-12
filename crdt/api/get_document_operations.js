import DocumentStore from '../stores/document';

/*
 * API Name: getDocumentOperations
 * Returns: An array of operations to get to where the document is currently
 * Used for setting up a new agent
 */
export default () => DocumentStore.getDocument().getOperations();
