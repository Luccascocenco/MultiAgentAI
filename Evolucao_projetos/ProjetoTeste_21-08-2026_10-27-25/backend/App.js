// app.js
const express = require('express');
const app = express();
const port = 3000;

const router = require('./src/constructors/aplicacao');
app.use('/api', router);

app.listen(port, () => {
  console.log(`Servidor rodando na porta ${port}`);
});