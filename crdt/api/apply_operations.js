import DocumentStore from '../stores/document';

/*
 * API Name: applyOperations
 * Returns: Plugin changes that need to be applied to show non-local changes
 * Used for applying CRDT operations to the local document
 */
export default (operations) => {
    const { textUpdates } = DocumentStore.getDocument().integrateOperations(operations);
    return textUpdates;
};
