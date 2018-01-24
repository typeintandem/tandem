import uuid from 'uuid';
import { Document } from '@atom/teletype-crdt';
import DocumentStore from './stores/document';
import api from './api';
import io from './io';
import logger from './utils/logger';

const localDocument = new Document({ siteId: uuid(), text: '' });
DocumentStore.setDocument(localDocument);

const processPayload = (payload) => {
    try {
        logger.debug(`Processing payload: ${payload}`);
        const { function: fcn, parameters: params = [] } = JSON.parse(payload);

        logger.debug(`Calling api function: ${JSON.stringify(fcn)}, with parameters: ${JSON.stringify(params)}`);
        const res = { value: api[fcn](...params) };
        const result = JSON.stringify(res);

        logger.debug(`Finished processing, with result: ${result}`);
        io.write(result);
    } catch (error) {
        logger.error(`There has been an error in processing payload: ${payload}`);
        logger.error(`Error: ${JSON.stringify(error)}`);
    }
};

io.addIoHandler(processPayload);

logger.info('Tandem-CRDT is up and running');
