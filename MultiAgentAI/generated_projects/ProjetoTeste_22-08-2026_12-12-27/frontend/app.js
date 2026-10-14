const express = require('express');
const app = express();
const auth = require('./auth/auth');
const inventory = require('./inventory/inventory');
const orders = require('./orders/orders');
const payments = require('./payments/payments');
const clients = require('./clients/clients');
const db = require('./db/db');

app.use(express.json());
app.use('/auth', auth);
app.use('/inventory', inventory);
app.use('/orders', orders);
app.use('/payments', payments);
app.use('/clients', clients);
app.use('/db', db);

app.listen(3000, () => {
    console.log('Servidor ligado em http://localhost:3000');
});