let localDocument = null;

export default {
    getDocument: () => localDocument,
    setDocument: (newDocument) => {
        localDocument = newDocument;
    }
};
