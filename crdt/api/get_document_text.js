import DocumentStore from '../stores/document';

/*
 * API Name: getDocumentText
 * Returns: The text value of the document's contents
 * Used for retrieving the text contents of the document
 */
export default () => {
    return DocumentStore.getDocument().getText();
};
